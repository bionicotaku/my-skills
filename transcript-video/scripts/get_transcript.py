#!/usr/bin/env python3
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_WORK_DIR = Path.home() / "Downloads" / "transcript-video-assets"


def detect_platform(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    if any(d in domain for d in ["youtube.com", "youtu.be", "youtube-nocookie.com"]):
        return "youtube"
    if any(d in domain for d in ["bilibili.com", "b23.tv"]):
        return "bilibili"
    return "unknown"


def slugify(value: str, max_len: int = 120) -> str:
    value = re.sub(r"\s+", "-", value.strip())
    value = re.sub(r"[\\/:*?\"<>|]+", "-", value)
    value = re.sub(r"[^\w\-.\u4e00-\u9fff]+", "-", value, flags=re.UNICODE)
    value = re.sub(r"-+", "-", value).strip("-._")
    return (value or "video-transcript")[:max_len]


def run(cmd, cwd=None, check=True):
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def platform_headers(platform: str):
    if platform != "bilibili":
        return []
    return [
        "--add-header", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "--add-header", "Referer: https://www.bilibili.com/",
    ]


def clean_vtt(content: str) -> str:
    lines = content.splitlines()
    text_lines = []
    timestamp_pattern = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3}\s-->\s\d{2}:\d{2}:\d{2}\.\d{3}")
    for line in lines:
        line = line.strip()
        if not line or line == "WEBVTT" or line.isdigit():
            continue
        if timestamp_pattern.match(line):
            continue
        if line.startswith("NOTE") or line.startswith("STYLE"):
            continue
        line = re.sub(r"<[^>]+>", "", line)
        if text_lines and text_lines[-1] == line:
            continue
        text_lines.append(line)
    return "\n".join(text_lines).strip()


def clean_srt(content: str) -> str:
    lines = content.splitlines()
    text_lines = []
    timestamp_pattern = re.compile(r"\d{2}:\d{2}:\d{2},\d{3}\s-->\s\d{2}:\d{2}:\d{2},\d{3}")
    for line in lines:
        line = line.strip()
        if not line or line.isdigit() or timestamp_pattern.match(line):
            continue
        line = re.sub(r"<[^>]+>", "", line)
        if text_lines and text_lines[-1] == line:
            continue
        text_lines.append(line)
    return "\n".join(text_lines).strip()


def get_video_metadata(url: str, platform: str):
    cmd = ["yt-dlp", "--dump-single-json", "--no-warnings", *platform_headers(platform), url]
    try:
        result = run(cmd)
        data = json.loads(result.stdout)
        return {
            "title": data.get("title") or "Untitled Video",
            "id": data.get("id") or "unknown",
            "uploader": data.get("uploader") or data.get("channel") or "unknown",
            "duration": data.get("duration"),
            "webpage_url": data.get("webpage_url") or url,
        }
    except Exception:
        return {
            "title": "Untitled Video",
            "id": "unknown",
            "uploader": "unknown",
            "duration": None,
            "webpage_url": url,
        }


def build_asset_dir(base_dir: Path, metadata: dict) -> Path:
    slug = slugify(metadata.get("title") or "video-transcript")
    video_id = slugify(str(metadata.get("id") or "unknown"), max_len=40)
    return base_dir / f"{slug}-{video_id}"


def write_metadata(asset_dir: Path, metadata: dict) -> Path:
    metadata_path = asset_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata_path


def fetch_subtitles(url: str, platform: str, language: str, asset_dir: Path):
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        cmd = [
            "yt-dlp",
            "--write-subs",
            "--write-auto-subs",
            "--skip-download",
            "--sub-lang", language,
            "--sub-format", "vtt/srt/best",
            "--output", "subs",
            *platform_headers(platform),
            url,
        ]
        try:
            run(cmd, cwd=temp_dir)
        except subprocess.CalledProcessError as exc:
            error_msg = (exc.stderr or exc.stdout or "").lower()
            if any(x in error_msg for x in ["unavailable", "not available", "region-restricted"]):
                raise RuntimeError("Video not available or region-restricted.")
            return None

        subtitle_files = list(temp_dir.glob("*.vtt")) + list(temp_dir.glob("*.srt"))
        if not subtitle_files:
            return None

        subtitle_file = subtitle_files[0]
        raw_subtitle_path = asset_dir / f"subtitle{subtitle_file.suffix.lower()}"
        shutil.copy2(subtitle_file, raw_subtitle_path)

        content = subtitle_file.read_text(encoding="utf-8", errors="ignore")
        transcript = clean_vtt(content) if subtitle_file.suffix.lower() == ".vtt" else clean_srt(content)
        transcript = transcript.strip()
        if not transcript:
            return None

        transcript_path = asset_dir / "subtitle.txt"
        transcript_path.write_text(transcript, encoding="utf-8")
        return {
            "kind": "subtitle",
            "asset_path": transcript_path,
            "subtitle_path": raw_subtitle_path,
            "transcript_path": transcript_path,
            "language": language,
        }


def download_audio(url: str, platform: str, asset_dir: Path) -> Path:
    outtmpl = str(asset_dir / "audio.%(ext)s")
    cmd = [
        "yt-dlp",
        "-f", "bestaudio/best",
        "-o", outtmpl,
        *platform_headers(platform),
        url,
    ]
    try:
        run(cmd, cwd=asset_dir)
    except subprocess.CalledProcessError as exc:
        error_msg = exc.stderr or exc.stdout or "Unknown yt-dlp error"
        raise RuntimeError(f"Failed to download audio: {error_msg.strip()}") from exc

    candidates = sorted([path for path in asset_dir.glob("audio.*") if path.is_file()])
    if not candidates:
        raise RuntimeError("Audio download completed but no local audio file was found.")
    return candidates[0]


def prepare_video_asset(
    url: str,
    language: str | None,
    work_dir: Path,
    fetch_subtitles=fetch_subtitles,
    download_audio_fn=download_audio,
    metadata_fetcher=get_video_metadata,
    platform_detector=detect_platform,
):
    platform = platform_detector(url)
    if platform == "unknown":
        raise RuntimeError("Unsupported URL format. Please use YouTube or Bilibili URLs.")

    preferred_language = language or ("zh-CN" if platform == "bilibili" else "en")
    metadata = metadata_fetcher(url, platform)
    asset_dir = build_asset_dir(work_dir, metadata)
    asset_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = write_metadata(asset_dir, metadata)

    subtitle_result = fetch_subtitles(url, platform, preferred_language, asset_dir)
    if subtitle_result:
        transcript_path = subtitle_result.get("transcript_path") or subtitle_result.get("asset_path")
        if transcript_path is None:
            raise RuntimeError("Subtitle fetch returned no transcript path.")
        return {
            "kind": "subtitle",
            "source_mode": "subtitles",
            "platform": platform,
            "language": subtitle_result["language"],
            "asset_dir": asset_dir,
            "asset_path": transcript_path,
            "subtitle_path": subtitle_result.get("subtitle_path"),
            "transcript_path": transcript_path,
            "metadata_path": metadata_path,
            "metadata": metadata,
        }

    audio_path = download_audio_fn(url, platform, asset_dir)
    return {
        "kind": "audio",
        "source_mode": "audio-download",
        "platform": platform,
        "language": "auto-detect",
        "asset_dir": asset_dir,
        "asset_path": audio_path,
        "audio_path": audio_path,
        "metadata_path": metadata_path,
        "metadata": metadata,
    }


def serialize_result(result: dict) -> dict:
    serialized = {}
    for key, value in result.items():
        if isinstance(value, Path):
            serialized[key] = str(value)
        else:
            serialized[key] = value
    return serialized


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch subtitles or download audio for a YouTube/Bilibili video without invoking downstream transcription."
    )
    parser.add_argument("url", help="Video URL (YouTube or Bilibili)")
    parser.add_argument("--lang", "-l", default=None, help="Preferred subtitle language code (default: zh-CN for Bilibili, en for YouTube)")
    parser.add_argument(
        "--work-dir",
        default=str(DEFAULT_WORK_DIR),
        help=f"Directory for prepared subtitle/audio assets (default: {DEFAULT_WORK_DIR})",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        result = prepare_video_asset(
            url=args.url,
            language=args.lang,
            work_dir=Path(args.work_dir).expanduser(),
        )
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(serialize_result(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
