#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib import error, request

BASE_URL = "https://api.assemblyai.com"
DEFAULT_OUTPUT_DIR = Path.home() / "Downloads"


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def http_post(url: str, headers: dict, data: bytes, timeout: int = 300) -> dict:
    req = request.Request(url, data=data, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} POST {url} failed: {body}") from e
    except error.URLError as e:
        raise RuntimeError(f"POST {url} failed: {e}") from e


def http_get(url: str, headers: dict, timeout: int = 60) -> dict:
    req = request.Request(url, headers=headers, method="GET")
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} GET {url} failed: {body}") from e
    except error.URLError as e:
        raise RuntimeError(f"GET {url} failed: {e}") from e


def upload_file(file_path: str, api_key: str) -> str:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    data = path.read_bytes()
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/octet-stream",
    }

    result = http_post(f"{BASE_URL}/v2/upload", headers, data, timeout=300)
    upload_url = result.get("upload_url")
    if not upload_url:
        raise RuntimeError(f"Upload succeeded but no upload_url returned: {result}")
    return upload_url


def create_transcript(upload_url: str, api_key: str) -> str:
    payload = {
        "audio_url": upload_url,
        "language_detection": True,
        "speech_models": ["universal-3-pro", "universal-2"],
    }

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }

    result = http_post(
        f"{BASE_URL}/v2/transcript",
        headers,
        json.dumps(payload).encode("utf-8"),
        timeout=60,
    )

    transcript_id = result.get("id")
    if not transcript_id:
        raise RuntimeError(f"Transcript creation failed: {result}")
    return transcript_id


def poll_transcript(transcript_id: str, api_key: str, interval: int = 3) -> dict:
    headers = {"Authorization": api_key}
    polling_url = f"{BASE_URL}/v2/transcript/{transcript_id}"

    while True:
        result = http_get(polling_url, headers, timeout=60)
        status = result.get("status")

        if status == "completed":
            return result
        if status == "error":
            raise RuntimeError(f"Transcription failed: {result.get('error', result)}")

        eprint(f"Current status: {status} ...")
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(
        description="Upload a local audio file to AssemblyAI and transcribe it using only Python stdlib."
    )
    parser.add_argument("file", help="Path to local audio file")
    parser.add_argument("--save", help="Optional full output file path; overrides --out-dir and --name", default=None)
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Directory to save the markdown transcript (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Optional output filename stem or filename; the saved file still uses a .md extension unless --save is used",
    )
    parser.add_argument("--interval", type=int, default=3, help="Polling interval in seconds")
    args = parser.parse_args()

    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing ASSEMBLYAI_API_KEY for assemblyai-transcript skill.")

    input_path = Path(args.file).expanduser()

    if args.save:
        save_path = Path(args.save).expanduser()
    else:
        filename = args.name or input_path.stem
        raw_name = Path(filename).name
        suffix = Path(raw_name).suffix
        base_name = raw_name[: -len(suffix)] if suffix else raw_name
        output_name = f"{(base_name or input_path.stem or 'transcript')}.md"
        save_path = Path(args.out_dir).expanduser() / output_name

    save_path.parent.mkdir(parents=True, exist_ok=True)

    eprint("Uploading local file...")
    upload_url = upload_file(str(input_path), api_key)
    eprint("Upload complete.")

    eprint("Creating transcript job...")
    transcript_id = create_transcript(upload_url, api_key)
    eprint(f"Transcript ID: {transcript_id}")

    eprint("Polling transcript result...")
    result = poll_transcript(transcript_id, api_key, interval=args.interval)

    text = result.get("text", "")
    markdown = f"# Transcript\n\n{text}\n" if text else "# Transcript\n"
    save_path.write_text(markdown, encoding="utf-8")

    print(save_path)
    print(text)


if __name__ == "__main__":
    main()
