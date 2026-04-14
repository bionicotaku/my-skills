#!/usr/bin/env python3
"""
Video Watcher - Universal transcript fetcher for YouTube and Bilibili

Primary path:
- Fetch platform subtitles with yt-dlp

Fallback path:
- If subtitles are unavailable, download audio locally
- Transcribe via the sibling assemblyai-transcript skill

Output:
- Print transcript/metadata to stdout
- Save a markdown file under the chosen download directory
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads"
ASSEMBLYAI_TRANSCRIBE_SCRIPT = Path(__file__).resolve().parents[2] / "assemblyai-transcript" / "scripts" / "transcribe.py"
INTERMEDIATE_TRANSCRIPT_FILENAME = "transcript.md"
INTERMEDIATE_TRANSCRIPT_HEADER = "# Intermediate Transcript"


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


def _write_transcript_markdown(text: str, path: Path, source_mode: str, language_label: str) -> None:
    markdown = (
        f"{INTERMEDIATE_TRANSCRIPT_HEADER}\n\n"
        "## Metadata\n\n"
        f"- Source mode: {source_mode}\n"
        f"- Language: {language_label}\n\n"
        "## Transcript\n\n"
        f"{text}\n"
    ) if text else (
        f"{INTERMEDIATE_TRANSCRIPT_HEADER}\n\n"
        "## Metadata\n\n"
        f"- Source mode: {source_mode}\n"
        f"- Language: {language_label}\n\n"
        "## Transcript\n"
    )
    path.write_text(markdown, encoding="utf-8")


def try_fetch_subtitles(url: str, platform: str, language: str, temp_dir: Path, transcript_path: Path):
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
    except subprocess.CalledProcessError as e:
        error_msg = (e.stderr or e.stdout or "").lower()
        if any(x in error_msg for x in ["unavailable", "not available", "region-restricted"]):
            raise RuntimeError("Video not available or region-restricted.")
        return None

    subtitle_files = list(temp_dir.glob("*.vtt")) + list(temp_dir.glob("*.srt"))
    if not subtitle_files:
        return None

    subtitle_file = subtitle_files[0]
    content = subtitle_file.read_text(encoding="utf-8", errors="ignore")
    transcript = clean_vtt(content) if subtitle_file.suffix.lower() == ".vtt" else clean_srt(content)
    transcript = transcript.strip()
    if not transcript:
        return None

    _write_transcript_markdown(transcript, transcript_path, "subtitles", language)
    return transcript_path


def download_audio(url: str, platform: str, temp_dir: Path) -> Path:
    outtmpl = str(temp_dir / "audio.%(ext)s")
    cmd = [
        "yt-dlp",
        "-f", "bestaudio/best",
        "-o", outtmpl,
        *platform_headers(platform),
        url,
    ]
    try:
        run(cmd, cwd=temp_dir)
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or e.stdout or "Unknown yt-dlp error"
        raise RuntimeError(f"Failed to download audio: {error_msg.strip()}")

    candidates = sorted([p for p in temp_dir.glob("audio.*") if p.is_file()])
    if not candidates:
        raise RuntimeError("Audio download completed but no local audio file was found.")
    return candidates[0]


def _read_transcript_output(path: Path) -> str:
    if not path.exists():
        raise RuntimeError("Intermediate transcript file was not created.")
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        raise RuntimeError("Intermediate transcript file is empty.")

    intermediate_marker = "## Transcript"
    if text.startswith(INTERMEDIATE_TRANSCRIPT_HEADER) and intermediate_marker in text:
        transcript = text.split(intermediate_marker, 1)[1].lstrip()
        return transcript.strip()

    prefix = "# Transcript"
    if text == prefix:
        return ""
    if text.startswith(f"{prefix}\n"):
        return text[len(prefix):].lstrip()
    return text


def _transcribe_single_file(audio_path: Path, out_file: Path, temp_dir: Path) -> str:
    cmd = [
        "python3",
        str(ASSEMBLYAI_TRANSCRIBE_SCRIPT),
        str(audio_path),
        "--save",
        str(out_file),
    ]
    try:
        run(cmd, cwd=temp_dir)
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or e.stdout or "Unknown transcription error"
        raise RuntimeError(error_msg.strip())
    return str(out_file)


def transcribe_audio(audio_path: Path, temp_dir: Path, transcript_path: Path) -> tuple[Path, str]:
    if not ASSEMBLYAI_TRANSCRIBE_SCRIPT.exists():
        raise RuntimeError(f"assemblyai-transcript script not found: {ASSEMBLYAI_TRANSCRIBE_SCRIPT}")

    try:
        _transcribe_single_file(audio_path, transcript_path, temp_dir)
        transcript = _read_transcript_output(transcript_path)
        _write_transcript_markdown(transcript, transcript_path, "audio-assemblyai-fallback", "auto-detect")
        return transcript_path, "audio-assemblyai-fallback"
    except RuntimeError as e:
        raise RuntimeError(f"AssemblyAI transcription failed: {str(e).strip()}")


def format_duration(seconds):
    if not seconds:
        return "unknown"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def clean_transcript_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()

    sentences = re.split(r"(?<=[。！？!?])\s+", text)
    cleaned = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if cleaned and cleaned[-1] == s:
            continue
        cleaned.append(s)
    return "\n".join(cleaned)


def paragraphize_text(text: str, group_size: int = 3) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    paragraphs = []
    for i in range(0, len(lines), group_size):
        chunk = " ".join(lines[i:i + group_size]).strip()
        if chunk:
            paragraphs.append(chunk)
    return "\n\n".join(paragraphs)


def write_markdown(out_dir: Path, metadata: dict, platform: str, language_label: str, source_mode: str, transcript: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{slugify(metadata['title'])}.md"
    out_path = out_dir / filename
    cleaned = clean_transcript_text(transcript)
    paragraphed = paragraphize_text(cleaned)
    body = f"""# {metadata['title']}

## Metadata

- Platform: {platform}
- Source mode: {source_mode}
- Language: {language_label}
- Uploader: {metadata['uploader']}
- Duration: {format_duration(metadata.get('duration'))}
- URL: {metadata['webpage_url']}
- Video ID: {metadata['id']}

## Transcript

{paragraphed}
"""
    out_path.write_text(body, encoding="utf-8")
    return out_path


def get_transcript(url: str, language: str = None, out_dir: Path = DEFAULT_DOWNLOAD_DIR):
    platform = detect_platform(url)
    if platform == "unknown":
        raise RuntimeError("Unsupported URL format. Please use YouTube or Bilibili URLs.")

    subtitle_language = language
    if subtitle_language is None:
        subtitle_language = "zh-CN" if platform == "bilibili" else "en"

    metadata = get_video_metadata(url, platform)

    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        transcript_path = temp_dir / INTERMEDIATE_TRANSCRIPT_FILENAME
        source_mode = "subtitles"
        language_label = subtitle_language

        transcript_file = try_fetch_subtitles(url, platform, subtitle_language, temp_dir, transcript_path)

        if not transcript_file:
            audio_path = download_audio(url, platform, temp_dir)
            transcript_file, source_mode = transcribe_audio(audio_path, temp_dir, transcript_path)
            language_label = "auto-detect"

        transcript = _read_transcript_output(transcript_file)
        out_path = write_markdown(out_dir, metadata, platform, language_label, source_mode, transcript)

        print(f"# Title: {metadata['title']}")
        print(f"# Platform: {platform.title()}")
        print(f"# Language: {language_label}")
        print(f"# Source mode: {source_mode}")
        print(f"# URL: {metadata['webpage_url']}")
        print(f"# Saved markdown: {out_path}")
        print()
        print(transcript)


def main():
    parser = argparse.ArgumentParser(description="Fetch video transcripts from YouTube or Bilibili, with audio-transcription fallback.")
    parser.add_argument("url", help="Video URL (YouTube or Bilibili)")
    parser.add_argument("--lang", "-l", default=None, help="Preferred subtitle language code (default: zh-CN for Bilibili, en for YouTube); ASR fallback uses auto-detection")
    parser.add_argument("--out-dir", default=str(DEFAULT_DOWNLOAD_DIR), help=f"Directory to save the markdown transcript (default: {DEFAULT_DOWNLOAD_DIR})")
    args = parser.parse_args()

    try:
        get_transcript(args.url, args.lang, Path(args.out_dir).expanduser())
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
