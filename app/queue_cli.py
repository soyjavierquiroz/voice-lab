from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from app.config import settings
from app.jobs import create_job, list_jobs, load_job, move_job, save_job, utc_now


AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".flac", ".ogg"}


def _queue_jobs_dir() -> Path:
    return settings.queue_dir / "jobs"


def _queue_done_dir() -> Path:
    return settings.queue_dir / "done"


def _queue_failed_dir() -> Path:
    return settings.queue_dir / "failed"


def _pending_dir() -> Path:
    return settings.input_dir / "pending"


def _job_path(job: dict[str, str | None], status_dir: Path | None = None) -> Path:
    directory = status_dir or _queue_jobs_dir()
    return directory / f"{job['job_id']}.json"


def _audio_paths() -> list[Path]:
    pending = _pending_dir()
    if not pending.exists():
        return []
    return sorted(
        item.resolve()
        for item in pending.iterdir()
        if item.is_file() and item.suffix.lower() in AUDIO_EXTENSIONS
    )


def _all_job_files() -> list[Path]:
    files: list[Path] = []
    for directory in (_queue_jobs_dir(), _queue_done_dir(), _queue_failed_dir()):
        files.extend(list_jobs(directory))
    return sorted(files)


def _queued_job_files() -> list[Path]:
    queued: list[Path] = []
    for job_file in list_jobs(_queue_jobs_dir()):
        try:
            job = load_job(job_file)
        except (OSError, ValueError):
            continue
        if job.get("status") == "queued":
            queued.append(job_file)
    return queued


def _known_input_paths() -> set[str]:
    known: set[str] = set()
    for job_file in _all_job_files():
        try:
            job = load_job(job_file)
        except (OSError, ValueError):
            continue
        input_path = job.get("input_path")
        if input_path:
            known.add(str(Path(input_path).resolve()))
    return known


def _infer_outputs(input_path: str | Path) -> tuple[Path, Path, Path]:
    stem = Path(input_path).name.rsplit(".", 1)[0]
    output_wav = settings.output_wav_dir / f"{stem}.clean.wav"
    output_mp3 = settings.output_mp3_dir / f"{stem}.clean.mp3"
    log_path = settings.logs_dir / "jobs" / f"{stem}.log"
    return output_wav.resolve(), output_mp3.resolve(), log_path.resolve()


def _cmd_enqueue_pending(args: argparse.Namespace) -> int:
    known_inputs = _known_input_paths()
    created = 0
    skipped = 0

    for audio_path in _audio_paths():
        if str(audio_path) in known_inputs:
            skipped += 1
            continue

        job = create_job(audio_path, model_name=args.model_name)
        save_job(job, _job_path(job))
        known_inputs.add(str(audio_path))
        created += 1
        print(f"queued {job['job_id']} {audio_path}", flush=True)

    print(f"enqueue-pending: created={created} skipped={skipped}")
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    for status, directory in (
        ("queued", _queue_jobs_dir()),
        ("done", _queue_done_dir()),
        ("failed", _queue_failed_dir()),
    ):
        print(f"{status}:")
        files = list_jobs(directory)
        if not files:
            print("  (none)")
            continue
        for job_file in files:
            try:
                job = load_job(job_file)
            except (OSError, ValueError) as exc:
                print(f"  invalid {job_file}: {exc}")
                continue
            print(
                "  "
                f"{job.get('job_id')} "
                f"status={job.get('status')} "
                f"model={job.get('model_name')} "
                f"input={job.get('input_path')}"
            )
    return 0


def _run_job(job: dict[str, str | None], job_file: Path) -> tuple[dict[str, str | None], Path, int]:
    script = (settings.root / "scripts" / "infer_one.sh").resolve()
    input_path = str(job["input_path"])
    model_name = str(job["model_name"] or settings.default_model_name)
    output_wav, output_mp3, log_path = _infer_outputs(input_path)

    job["status"] = "processing"
    job["started_at"] = utc_now()
    job["finished_at"] = None
    job["error"] = None
    job["output_wav"] = str(output_wav)
    job["output_mp3"] = str(output_mp3)
    job["log_path"] = str(log_path)
    save_job(job, job_file)

    env = os.environ.copy()
    env.setdefault("VOICE_LAB_ROOT", str(settings.root))

    result = subprocess.run(
        [str(script), input_path, model_name],
        cwd=settings.root,
        env=env,
        shell=False,
        check=False,
    )

    job["finished_at"] = utc_now()
    if result.returncode == 0:
        job["status"] = "done"
        save_job(job, job_file)
        target = move_job(job_file, _queue_done_dir())
    else:
        job["status"] = "failed"
        job["error"] = f"infer_one.sh exited with code {result.returncode}"
        save_job(job, job_file)
        target = move_job(job_file, _queue_failed_dir())

    return job, target, result.returncode


def _cmd_process_next(args: argparse.Namespace) -> int:
    queued = _queued_job_files()
    if not queued:
        print("process-next: no queued jobs", flush=True)
        return 0

    job_file = queued[0]
    job = load_job(job_file)
    if job.get("status") != "queued":
        print(f"process-next: first job is not queued: {job_file}", file=sys.stderr)
        return 1

    print(f"process-next: processing {job.get('job_id')} input={job.get('input_path')}", flush=True)
    job, target, returncode = _run_job(job, job_file)
    print(f"process-next: {job['status']} {target}", flush=True)
    return 0 if returncode == 0 else 1


def _cmd_process_all(args: argparse.Namespace) -> int:
    limit = max(0, min(args.limit, settings.max_batch_jobs))
    processed = 0
    failed = 0

    for _ in range(limit):
        queued = _queued_job_files()
        if not queued:
            break
        result = _cmd_process_next(args)
        processed += 1
        if result != 0:
            failed += 1

    print(f"process-all: processed={processed} failed={failed} limit={limit}")
    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m app.queue_cli", description="voice-lab file queue tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    enqueue = subparsers.add_parser("enqueue-pending", help="Create queued jobs for audio files in input/pending")
    enqueue.add_argument("--model-name", default=settings.default_model_name)
    enqueue.set_defaults(func=_cmd_enqueue_pending)

    list_parser = subparsers.add_parser("list", help="List queued, done and failed jobs")
    list_parser.set_defaults(func=_cmd_list)

    process_next = subparsers.add_parser("process-next", help="Process the first queued job")
    process_next.set_defaults(func=_cmd_process_next)

    process_all = subparsers.add_parser("process-all", help="Process up to N queued jobs")
    process_all.add_argument("--limit", type=int, default=1)
    process_all.set_defaults(func=_cmd_process_all)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
