from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from uuid import uuid4

from app.config import settings


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


@dataclass(frozen=True)
class Job:
    id: str
    input_path: str
    model_name: str
    status: JobStatus
    created_at: str


def new_job(input_path: str | Path, model_name: str | None = None) -> Job:
    return Job(
        id=uuid4().hex,
        input_path=str(input_path),
        model_name=model_name or settings.default_model_name,
        status=JobStatus.QUEUED,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def queue_path(status: JobStatus) -> Path:
    if status == JobStatus.QUEUED:
        return settings.queue_dir / "jobs"
    return settings.queue_dir / status.value


def job_file(job_id: str, status: JobStatus = JobStatus.QUEUED) -> Path:
    return queue_path(status) / f"{job_id}.json"


def write_job(job: Job) -> Path:
    path = job_file(job.id, job.status)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(job), indent=2) + "\n", encoding="utf-8")
    return path


def read_job(path: str | Path) -> Job:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    data["status"] = JobStatus(data["status"])
    return Job(**data)


def move_job(path: str | Path, status: JobStatus) -> Path:
    source = Path(path)
    job = read_job(source)
    updated = Job(
        id=job.id,
        input_path=job.input_path,
        model_name=job.model_name,
        status=status,
        created_at=job.created_at,
    )
    target = job_file(updated.id, status)
    target.parent.mkdir(parents=True, exist_ok=True)
    source.replace(target)
    target.write_text(json.dumps(asdict(updated), indent=2) + "\n", encoding="utf-8")
    return target
