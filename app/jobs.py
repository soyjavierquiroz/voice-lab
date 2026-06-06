from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


VALID_STATUSES = {"queued", "processing", "done", "failed"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_job(input_path: str | Path, model_name: str = "mi_voz") -> dict[str, str | None]:
    return {
        "job_id": uuid4().hex,
        "input_path": str(Path(input_path).resolve()),
        "model_name": model_name,
        "status": "queued",
        "created_at": utc_now(),
        "started_at": None,
        "finished_at": None,
        "error": None,
        "output_wav": None,
        "output_mp3": None,
        "log_path": None,
    }


def load_job(job_file: str | Path) -> dict[str, str | None]:
    job = json.loads(Path(job_file).read_text(encoding="utf-8"))
    if job.get("status") not in VALID_STATUSES:
        raise ValueError(f"Invalid job status in {job_file}: {job.get('status')}")
    return job


def save_job(job: dict[str, str | None], job_file: str | Path) -> Path:
    path = Path(job_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(job, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def list_jobs(status_dir: str | Path) -> list[Path]:
    path = Path(status_dir)
    if not path.exists():
        return []
    return sorted(item for item in path.glob("*.json") if item.is_file())


def move_job(job_file: str | Path, target_dir: str | Path) -> Path:
    source = Path(job_file)
    target = Path(target_dir) / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    source.replace(target)
    return target
