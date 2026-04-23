#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Callable

import httpx


BASE_URL = "https://api.assemblyai.com"
DEFAULT_OUTPUT_DIR = Path.home() / "Downloads"
ENV_FILENAME = ".env"
DEFAULT_CONNECT_TIMEOUT_SECONDS = 15.0
DEFAULT_UPLOAD_WRITE_TIMEOUT_SECONDS = 120.0
DEFAULT_UPLOAD_READ_TIMEOUT_SECONDS = 60.0
DEFAULT_CREATE_READ_TIMEOUT_SECONDS = 60.0
DEFAULT_POLL_REQUEST_TIMEOUT_SECONDS = 30.0
DEFAULT_QUEUED_SOFT_TIMEOUT_SECONDS = 20 * 60
DEFAULT_PROCESSING_SOFT_TIMEOUT_SECONDS = 90 * 60
DEFAULT_HARD_TIMEOUT_SECONDS = 6 * 60 * 60
DEFAULT_CHUNK_SIZE_MB = 4.0
DEFAULT_PROGRESS_LOG_INTERVAL_SECONDS = 1.0


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def read_env_value(env_path: Path, key: str) -> str | None:
    if not env_path.is_file():
        return None

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue

        current_key, value = line.split("=", 1)
        if current_key.strip() != key:
            continue

        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        return value

    return None


def resolve_api_key() -> str | None:
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if api_key:
        return api_key

    script_dir = Path(__file__).resolve().parent
    env_candidates = [
        Path.cwd() / ENV_FILENAME,
        script_dir.parent / ENV_FILENAME,
        script_dir / ENV_FILENAME,
    ]

    seen = set()
    for env_path in env_candidates:
        resolved = env_path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)

        api_key = read_env_value(resolved, "ASSEMBLYAI_API_KEY")
        if api_key:
            return api_key

    return None


def format_bytes(num_bytes: int) -> str:
    value = float(num_bytes)
    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f}{unit}"
        value /= 1024
    return f"{num_bytes}B"


def format_duration(seconds: float) -> str:
    total_seconds = max(int(seconds), 0)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:d}h{minutes:02d}m{secs:02d}s"
    if minutes:
        return f"{minutes:d}m{secs:02d}s"
    return f"{secs:d}s"


def build_timeout(connect: float, read: float, write: float | None = None) -> httpx.Timeout:
    return httpx.Timeout(connect=connect, read=read, write=read if write is None else write, pool=connect)


def response_json(response: httpx.Response, context: str) -> dict:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        body = response.text.strip()
        raise RuntimeError(f"{context} failed with HTTP {response.status_code}: {body}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(f"{context} returned non-JSON response: {response.text.strip()}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError(f"{context} returned unexpected JSON payload: {json.dumps(payload)}")
    return payload


class UploadProgressTracker:
    def __init__(
        self,
        total_bytes: int,
        clock: Callable[[], float] = time.monotonic,
        logger: Callable[[str], None] = eprint,
        log_interval_seconds: float = DEFAULT_PROGRESS_LOG_INTERVAL_SECONDS,
    ):
        self.total_bytes = total_bytes
        self.clock = clock
        self.logger = logger
        self.log_interval_seconds = log_interval_seconds
        self.started_at = clock()
        self.last_log_at = self.started_at
        self.bytes_confirmed = 0

    def confirm_bytes_sent(self, byte_count: int) -> None:
        if byte_count <= 0:
            return
        self.bytes_confirmed += byte_count
        self.log_progress()

    def log_progress(self, force: bool = False) -> None:
        now = self.clock()
        if not force and now - self.last_log_at < self.log_interval_seconds and self.bytes_confirmed < self.total_bytes:
            return

        elapsed = max(now - self.started_at, 1e-6)
        rate = self.bytes_confirmed / elapsed
        percent = 100.0 if self.total_bytes == 0 else min((self.bytes_confirmed / self.total_bytes) * 100.0, 100.0)
        if rate > 0 and self.bytes_confirmed < self.total_bytes:
            remaining_seconds = (self.total_bytes - self.bytes_confirmed) / rate
            eta = format_duration(remaining_seconds)
        else:
            eta = "0s"

        self.logger(
            "Upload progress: "
            f"{percent:.1f}% "
            f"({format_bytes(self.bytes_confirmed)}/{format_bytes(self.total_bytes)}) "
            f"at {format_bytes(int(rate))}/s, ETA {eta}"
        )
        self.last_log_at = now


class FileChunkStream:
    def __init__(self, file_path: Path, chunk_size: int, tracker: UploadProgressTracker):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.tracker = tracker

    def __iter__(self):
        pending_chunk_size = 0
        with self.file_path.open("rb") as handle:
            while True:
                if pending_chunk_size:
                    self.tracker.confirm_bytes_sent(pending_chunk_size)
                    pending_chunk_size = 0

                chunk = handle.read(self.chunk_size)
                if not chunk:
                    break

                pending_chunk_size = len(chunk)
                yield chunk

            if pending_chunk_size:
                self.tracker.confirm_bytes_sent(pending_chunk_size)


def upload_file(
    file_path: Path,
    api_key: str,
    client: httpx.Client,
    *,
    chunk_size_bytes: int,
    connect_timeout: float,
    upload_write_timeout: float,
    upload_read_timeout: float,
) -> str:
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size = file_path.stat().st_size
    if file_size <= 0:
        raise RuntimeError(f"File is empty: {file_path}")

    tracker = UploadProgressTracker(total_bytes=file_size)
    stream = FileChunkStream(file_path, chunk_size_bytes, tracker)
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/octet-stream",
        "Content-Length": str(file_size),
    }

    eprint(f"Uploading {file_path.name} ({format_bytes(file_size)}) ...")
    try:
        response = client.post(
            "/v2/upload",
            headers=headers,
            content=stream,
            timeout=build_timeout(connect_timeout, upload_read_timeout, upload_write_timeout),
        )
    except httpx.ConnectTimeout as exc:
        raise RuntimeError(f"Upload connection timed out after {format_duration(connect_timeout)}.") from exc
    except httpx.WriteTimeout as exc:
        raise RuntimeError(
            "Upload stalled while sending bytes. "
            f"No upload progress was confirmed within {format_duration(upload_write_timeout)}."
        ) from exc
    except httpx.ReadTimeout as exc:
        raise RuntimeError(
            "Upload bytes finished sending, but AssemblyAI did not return an upload response within "
            f"{format_duration(upload_read_timeout)}."
        ) from exc
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Upload request failed: {exc}") from exc

    payload = response_json(response, "POST /v2/upload")
    upload_url = payload.get("upload_url")
    if not upload_url:
        raise RuntimeError(f"Upload succeeded but no upload_url returned: {payload}")
    eprint("Upload complete.")
    return upload_url


def create_transcript(
    upload_url: str,
    api_key: str,
    client: httpx.Client,
    *,
    connect_timeout: float,
    create_read_timeout: float,
) -> str:
    payload = {
        "audio_url": upload_url,
        "language_detection": True,
        "speech_models": ["universal-3-pro", "universal-2"],
    }
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }

    try:
        response = client.post(
            "/v2/transcript",
            headers=headers,
            json=payload,
            timeout=build_timeout(connect_timeout, create_read_timeout),
        )
    except httpx.ConnectTimeout as exc:
        raise RuntimeError(f"Transcript creation connection timed out after {format_duration(connect_timeout)}.") from exc
    except httpx.ReadTimeout as exc:
        raise RuntimeError(
            "AssemblyAI did not return a transcript job response within "
            f"{format_duration(create_read_timeout)}."
        ) from exc
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Transcript creation request failed: {exc}") from exc

    result = response_json(response, "POST /v2/transcript")
    transcript_id = result.get("id")
    if not transcript_id:
        raise RuntimeError(f"Transcript creation failed: {result}")
    return transcript_id


def fetch_transcript_status(
    transcript_id: str,
    api_key: str,
    client: httpx.Client,
    *,
    connect_timeout: float,
    poll_request_timeout: float,
) -> dict:
    headers = {"Authorization": api_key}
    try:
        response = client.get(
            f"/v2/transcript/{transcript_id}",
            headers=headers,
            timeout=build_timeout(connect_timeout, poll_request_timeout),
        )
    except httpx.ConnectTimeout as exc:
        raise RuntimeError(f"Polling could not connect within {format_duration(connect_timeout)}.") from exc
    except httpx.ReadTimeout as exc:
        raise RuntimeError(
            "Polling timed out waiting for AssemblyAI status response after "
            f"{format_duration(poll_request_timeout)}."
        ) from exc
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Polling transcript status failed: {exc}") from exc

    return response_json(response, f"GET /v2/transcript/{transcript_id}")


def wait_for_transcript_completion(
    fetch_status: Callable[[], dict],
    interval: int,
    queued_soft_timeout: int,
    processing_soft_timeout: int,
    hard_timeout: int,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    logger: Callable[[str], None] = eprint,
) -> dict:
    started_at = clock()
    last_status = None
    last_status_change_at = started_at
    warned_for_status = set()

    while True:
        now = clock()
        elapsed = now - started_at
        if hard_timeout and elapsed > hard_timeout:
            raise RuntimeError(
                "Transcript polling exceeded the hard timeout after "
                f"{format_duration(elapsed)}."
            )

        result = fetch_status()
        status = result.get("status", "unknown")
        now = clock()
        elapsed = now - started_at

        if status == "completed":
            logger(f"Transcript status changed to completed after {format_duration(elapsed)}.")
            return result

        if status == "error":
            raise RuntimeError(f"Transcription failed: {result.get('error', result)}")

        if status != last_status:
            last_status = status
            last_status_change_at = now
            warned_for_status.discard(status)
            logger(f"Transcript status changed to {status} after {format_duration(elapsed)}.")
        else:
            same_status_elapsed = now - last_status_change_at
            logger(f"Transcript status still {status} after {format_duration(elapsed)}.")
            if status == "queued" and queued_soft_timeout and same_status_elapsed > queued_soft_timeout and status not in warned_for_status:
                logger(
                    "Warning: transcript has remained queued for "
                    f"{format_duration(same_status_elapsed)}."
                )
                warned_for_status.add(status)
            elif (
                status == "processing"
                and processing_soft_timeout
                and same_status_elapsed > processing_soft_timeout
                and status not in warned_for_status
            ):
                logger(
                    "Warning: transcript has remained processing for "
                    f"{format_duration(same_status_elapsed)}."
                )
                warned_for_status.add(status)

        sleep(interval)


def poll_transcript(
    transcript_id: str,
    api_key: str,
    client: httpx.Client,
    *,
    interval: int,
    connect_timeout: float,
    poll_request_timeout: float,
    queued_soft_timeout: int,
    processing_soft_timeout: int,
    hard_timeout: int,
) -> dict:
    return wait_for_transcript_completion(
        fetch_status=lambda: fetch_transcript_status(
            transcript_id,
            api_key,
            client,
            connect_timeout=connect_timeout,
            poll_request_timeout=poll_request_timeout,
        ),
        interval=interval,
        queued_soft_timeout=queued_soft_timeout,
        processing_soft_timeout=processing_soft_timeout,
        hard_timeout=hard_timeout,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload a local audio file to AssemblyAI with progress-aware upload and transcript polling."
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
    parser.add_argument("--chunk-size-mb", type=float, default=DEFAULT_CHUNK_SIZE_MB, help="Upload chunk size in MB")
    parser.add_argument("--connect-timeout", type=float, default=DEFAULT_CONNECT_TIMEOUT_SECONDS, help="Connection timeout in seconds")
    parser.add_argument(
        "--upload-write-timeout",
        type=float,
        default=DEFAULT_UPLOAD_WRITE_TIMEOUT_SECONDS,
        help="Upload idle timeout in seconds while sending file bytes",
    )
    parser.add_argument(
        "--upload-read-timeout",
        type=float,
        default=DEFAULT_UPLOAD_READ_TIMEOUT_SECONDS,
        help="Timeout in seconds to wait for AssemblyAI upload response after bytes are sent",
    )
    parser.add_argument(
        "--create-read-timeout",
        type=float,
        default=DEFAULT_CREATE_READ_TIMEOUT_SECONDS,
        help="Timeout in seconds to wait for transcript job creation response",
    )
    parser.add_argument(
        "--poll-request-timeout",
        type=float,
        default=DEFAULT_POLL_REQUEST_TIMEOUT_SECONDS,
        help="Timeout in seconds for each transcript status polling request",
    )
    parser.add_argument(
        "--queued-soft-timeout",
        type=int,
        default=DEFAULT_QUEUED_SOFT_TIMEOUT_SECONDS,
        help="Warn if transcript stays queued longer than this many seconds",
    )
    parser.add_argument(
        "--processing-soft-timeout",
        type=int,
        default=DEFAULT_PROCESSING_SOFT_TIMEOUT_SECONDS,
        help="Warn if transcript stays processing longer than this many seconds",
    )
    parser.add_argument(
        "--hard-timeout",
        type=int,
        default=DEFAULT_HARD_TIMEOUT_SECONDS,
        help="Fail if transcript polling exceeds this many seconds in total",
    )
    return parser.parse_args()


def resolve_output_path(args: argparse.Namespace, input_path: Path) -> Path:
    if args.save:
        return Path(args.save).expanduser()

    filename = args.name or input_path.stem
    raw_name = Path(filename).name
    suffix = Path(raw_name).suffix
    base_name = raw_name[: -len(suffix)] if suffix else raw_name
    output_name = f"{(base_name or input_path.stem or 'transcript')}.md"
    return Path(args.out_dir).expanduser() / output_name


def main():
    args = parse_args()

    api_key = resolve_api_key()
    if not api_key:
        raise RuntimeError("Missing ASSEMBLYAI_API_KEY for assemblyai-transcript skill. Checked process env and local .env files.")

    input_path = Path(args.file).expanduser()
    save_path = resolve_output_path(args, input_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    chunk_size_bytes = max(int(args.chunk_size_mb * 1024 * 1024), 64 * 1024)

    with httpx.Client(base_url=BASE_URL) as client:
        upload_url = upload_file(
            input_path,
            api_key,
            client,
            chunk_size_bytes=chunk_size_bytes,
            connect_timeout=args.connect_timeout,
            upload_write_timeout=args.upload_write_timeout,
            upload_read_timeout=args.upload_read_timeout,
        )

        eprint("Creating transcript job...")
        transcript_id = create_transcript(
            upload_url,
            api_key,
            client,
            connect_timeout=args.connect_timeout,
            create_read_timeout=args.create_read_timeout,
        )
        eprint(f"Transcript ID: {transcript_id}")

        eprint("Polling transcript result...")
        result = poll_transcript(
            transcript_id,
            api_key,
            client,
            interval=args.interval,
            connect_timeout=args.connect_timeout,
            poll_request_timeout=args.poll_request_timeout,
            queued_soft_timeout=args.queued_soft_timeout,
            processing_soft_timeout=args.processing_soft_timeout,
            hard_timeout=args.hard_timeout,
        )

    text = result.get("text", "")
    markdown = f"# Transcript\n\n{text}\n" if text else "# Transcript\n"
    save_path.write_text(markdown, encoding="utf-8")

    print(save_path)
    print(text)


if __name__ == "__main__":
    main()
