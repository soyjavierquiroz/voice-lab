from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


@dataclass(frozen=True)
class Settings:
    root: Path
    default_model_name: str
    default_sample_rate: int
    output_mp3_bitrate: str
    max_batch_jobs: int
    cpu_quota: str
    memory_max: str
    log_level: str
    rvc_engine_path: Path | None

    @property
    def input_dir(self) -> Path:
        return self.root / "input"

    @property
    def queue_dir(self) -> Path:
        return self.root / "queue"

    @property
    def processing_dir(self) -> Path:
        return self.root / "processing"

    @property
    def output_dir(self) -> Path:
        return self.root / "output"

    @property
    def datasets_dir(self) -> Path:
        return self.root / "datasets"

    @property
    def models_dir(self) -> Path:
        return self.root / "models"

    @property
    def logs_dir(self) -> Path:
        return self.root / "logs"

    @property
    def tmp_dir(self) -> Path:
        return self.root / "tmp"


def get_settings() -> Settings:
    root = Path(os.getenv("VOICE_LAB_ROOT", "/opt/voice-lab")).resolve()
    engine = os.getenv("RVC_ENGINE_PATH")

    return Settings(
        root=root,
        default_model_name=os.getenv("DEFAULT_MODEL_NAME", "mi_voz"),
        default_sample_rate=_env_int("DEFAULT_SAMPLE_RATE", 40000),
        output_mp3_bitrate=os.getenv("OUTPUT_MP3_BITRATE", "192k"),
        max_batch_jobs=_env_int("MAX_BATCH_JOBS", 1),
        cpu_quota=os.getenv("CPU_QUOTA", "60%"),
        memory_max=os.getenv("MEMORY_MAX", "5G"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        rvc_engine_path=Path(engine).resolve() if engine else None,
    )


settings = get_settings()
