#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
from urllib.request import Request, urlopen

USER_AGENT = "Mozilla/5.0"
TIMEOUT_SECONDS = 60


def load_urls(path: Path):
    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        data = json.loads(stripped)
        if not isinstance(data, list):
            raise ValueError("JSON input must be an array of URLs")
        return [str(item).strip() for item in data if str(item).strip()]
    return [line.strip() for line in text.splitlines() if line.strip()]


def extension_from_response(url: str, content_type: Optional[str]):
    path_ext = Path(urlparse(url).path).suffix
    if path_ext:
        return path_ext
    if content_type:
        mime = content_type.split(";", 1)[0].strip().lower()
        guessed = mimetypes.guess_extension(mime)
        if guessed == ".jpe":
            return ".jpg"
        if guessed:
            return guessed
    return ".jpg"


def download(url: str, dest: Path, referer: Optional[str]):
    headers = {"User-Agent": USER_AGENT}
    if referer:
        headers["Referer"] = referer
    request = Request(url, headers=headers)
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        content_type = response.headers.get("Content-Type")
        suffix = extension_from_response(url, content_type)
        final_dest = dest.with_suffix(suffix)
        final_dest.write_bytes(response.read())
        return final_dest


def main():
    parser = argparse.ArgumentParser(description="Download ordered image URLs into a folder with sequential names.")
    parser.add_argument("--input", required=True, help="Path to a JSON array or newline-delimited URL list")
    parser.add_argument("--output-dir", required=True, help="Directory to save images into")
    parser.add_argument("--referer", help="Optional Referer header for image requests")
    args = parser.parse_args()

    input_path = Path(os.path.expanduser(args.input)).resolve()
    output_dir = Path(os.path.expanduser(args.output_dir)).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    urls = load_urls(input_path)
    if not urls:
        print("ERROR: no image URLs found in input", file=sys.stderr)
        return 1

    failures = []
    for index, url in enumerate(urls):
        try:
            saved = download(url, output_dir / str(index), args.referer)
            print(saved)
        except Exception as exc:
            failures.append((index, url, str(exc)))
            print(f"FAILED {index} {url} :: {exc}", file=sys.stderr)

    print(f"COUNT={len(urls)}")
    print(f"OUTDIR={output_dir}")

    if failures:
        print(f"FAILURES={len(failures)}", file=sys.stderr)
        for index, url, error in failures:
            print(f"FAIL {index} {url} :: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
