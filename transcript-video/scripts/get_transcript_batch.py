#!/usr/bin/env python
import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from get_transcript import DEFAULT_WORK_DIR, prepare_video_asset, serialize_result


DEFAULT_WORKERS = 4


def read_urls(input_file: str | None, urls: list[str]) -> list[str]:
    collected = []
    if input_file:
        input_path = Path(input_file).expanduser()
        for line in input_path.read_text(encoding="utf-8").splitlines():
            value = line.strip()
            if not value or value.startswith("#"):
                continue
            collected.append(value)

    collected.extend(url.strip() for url in urls if url.strip())
    return collected


def prepare_one(args: tuple[int, str, str | None, str]) -> dict:
    index, url, language, work_dir = args
    try:
        result = prepare_video_asset(
            url=url,
            language=language,
            work_dir=Path(work_dir).expanduser(),
        )
        return {
            "index": index,
            "url": url,
            "ok": True,
            "result": serialize_result(result),
        }
    except Exception as exc:
        return {
            "index": index,
            "url": url,
            "ok": False,
            "error": str(exc),
        }


def run_batch(urls: list[str], language: str | None, work_dir: Path, workers: int) -> dict:
    tasks = [
        (index, url, language, str(work_dir))
        for index, url in enumerate(urls, start=1)
    ]
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(prepare_one, tasks))

    ok_count = sum(1 for item in results if item["ok"])
    failed_count = len(results) - ok_count
    return {
        "ok": failed_count == 0,
        "workers": workers,
        "total": len(results),
        "succeeded": ok_count,
        "failed": failed_count,
        "results": results,
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch subtitles or download audio for multiple YouTube/Bilibili URLs with a process pool."
    )
    parser.add_argument("urls", nargs="*", help="Video URLs (YouTube or Bilibili)")
    parser.add_argument(
        "--input-file",
        "-i",
        default=None,
        help="Text file with one URL per line. Blank lines and lines starting with # are ignored.",
    )
    parser.add_argument("--lang", "-l", default=None, help="Preferred subtitle language code")
    parser.add_argument(
        "--work-dir",
        default=str(DEFAULT_WORK_DIR),
        help=f"Directory for prepared subtitle/audio assets (default: {DEFAULT_WORK_DIR})",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Number of worker processes (default: {DEFAULT_WORKERS})",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    urls = read_urls(args.input_file, args.urls)
    if not urls:
        print("Error: provide at least one URL or --input-file.", file=sys.stderr)
        sys.exit(2)
    if args.workers < 1:
        print("Error: --workers must be at least 1.", file=sys.stderr)
        sys.exit(2)

    summary = run_batch(
        urls=urls,
        language=args.lang,
        work_dir=Path(args.work_dir).expanduser(),
        workers=args.workers,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not summary["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
