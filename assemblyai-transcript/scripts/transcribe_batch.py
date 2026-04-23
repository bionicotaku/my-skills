#!/usr/bin/env python3
import argparse
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable


SUPPORTED_MEDIA_SUFFIXES = {
    ".aac",
    ".aiff",
    ".avi",
    ".flac",
    ".m4a",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".ogg",
    ".wav",
    ".webm",
}
MAX_PARALLEL_WORKERS = 4
TRANSCRIBE_SCRIPT = Path(__file__).resolve().parent / "transcribe.py"


def log_line(message: str) -> None:
    print(message, flush=True)


def natural_sort_key(path: Path) -> list[object]:
    parts = re.split(r"(\d+)", path.name)
    key: list[object] = []
    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part.lower())
    return key


def is_supported_media_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_MEDIA_SUFFIXES


def collect_supported_media_files(directory: Path) -> list[Path]:
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    media_files = [path for path in directory.iterdir() if is_supported_media_file(path)]
    return sorted(media_files, key=natural_sort_key)


def build_output_path(target_dir: Path, input_path: Path) -> Path:
    return target_dir / f"{input_path.stem}.md"


def collect_existing_output_names(directory: Path) -> set[str]:
    if not directory.exists():
        return set()
    return {path.name for path in directory.iterdir() if path.is_file() and path.suffix.lower() == ".md"}


def transcribe_with_subprocess(
    input_path: Path,
    output_path: Path,
    extra_cli_args: list[str],
    *,
    python_executable: str = sys.executable,
    script_path: Path = TRANSCRIBE_SCRIPT,
) -> None:
    cmd = [
        python_executable,
        str(script_path),
        str(input_path),
        "--save",
        str(output_path),
        *extra_cli_args,
    ]
    subprocess.run(cmd, check=True)


def run_batch_transcribe(
    *,
    source_dir: Path,
    target_dir: Path,
    max_workers: int = MAX_PARALLEL_WORKERS,
    transcriber: Callable[[Path, Path, list[str]], None] = transcribe_with_subprocess,
    extra_cli_args: list[str] | None = None,
    logger: Callable[[str], None] = log_line,
) -> dict[str, int]:
    source_files = collect_supported_media_files(source_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    existing_names = collect_existing_output_names(target_dir)
    extra_cli_args = extra_cli_args or []

    processed = 0
    skipped = 0
    failed = 0

    logger(f"源目录: {source_dir}")
    logger(f"目标目录: {target_dir}")
    logger(f"源媒体文件数: {len(source_files)}")
    logger(f"目标已存在 markdown 数: {len(existing_names)}")

    if not source_files:
        logger("没有找到可处理的媒体文件。")
        return {
            "total_source_files": 0,
            "processed": 0,
            "skipped": 0,
            "failed": 0,
        }

    worker_count = max(1, min(max_workers, MAX_PARALLEL_WORKERS))
    logger(f"并发 worker 数: {worker_count}")

    def worker(index: int, total: int, source_path: Path) -> tuple[str, str]:
        output_path = build_output_path(target_dir, source_path)
        logger(f"[{index}/{total}] 开始处理: {source_path.name}")
        transcriber(source_path, output_path, list(extra_cli_args))
        logger(f"[{index}/{total}] 处理完成: {source_path.name}")
        return source_path.name, output_path.name

    futures = {}
    total = len(source_files)
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        for index, source_path in enumerate(source_files, start=1):
            output_path = build_output_path(target_dir, source_path)
            if output_path.name in existing_names:
                skipped += 1
                logger(f"[{index}/{total}] 跳过: {source_path.name}")
                continue

            future = executor.submit(worker, index, total, source_path)
            futures[future] = (index, source_path)

        for future in as_completed(futures):
            index, source_path = futures[future]
            try:
                _, output_name = future.result()
                existing_names.add(output_name)
                processed += 1
            except Exception as exc:
                failed += 1
                logger(f"[{index}/{total}] 处理失败: {source_path.name} | {type(exc).__name__}: {exc}")

    logger("")
    logger("批处理完成")
    logger(f"- 成功: {processed}")
    logger(f"- 跳过: {skipped}")
    logger(f"- 失败: {failed}")

    return {
        "total_source_files": len(source_files),
        "processed": processed,
        "skipped": skipped,
        "failed": failed,
    }


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Batch wrapper for transcribe.py with at most 4 parallel workers."
    )
    parser.add_argument("--source-dir", required=True, help="Directory containing local audio/video files")
    parser.add_argument("--target-dir", required=True, help="Directory for generated markdown files")
    parser.add_argument(
        "--max-workers",
        type=int,
        default=MAX_PARALLEL_WORKERS,
        help=f"Requested worker count; actual concurrency is capped at {MAX_PARALLEL_WORKERS}",
    )
    return parser.parse_known_args()


def main() -> None:
    args, extra_cli_args = parse_args()
    run_batch_transcribe(
        source_dir=Path(args.source_dir).expanduser(),
        target_dir=Path(args.target_dir).expanduser(),
        max_workers=args.max_workers,
        extra_cli_args=extra_cli_args,
    )


if __name__ == "__main__":
    main()
