from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


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
    def processing_dir(self) -> Path:
        return self.root / "processing"

    @property
    def output_wav_dir(self) -> Path:
        return self.root / "output" / "wav"

    @property
    def output_mp3_dir(self) -> Path:
        return self.root / "output" / "mp3"

    @property
    def logs_dir(self) -> Path:
        return self.root / "logs"

    @property
    def models_dir(self) -> Path:
        return self.root / "models"

    @property
    def datasets_dir(self) -> Path:
        return self.root / "datasets"

    @property
    def queue_dir(self) -> Path:
        return self.root / "queue"

    @property
    def output_dir(self) -> Path:
        return self.root / "output"

    @property
    def tmp_dir(self) -> Path:
        return self.root / "tmp"


def get_settings() -> Settings:
    initial_root = Path(os.getenv("VOICE_LAB_ROOT", "/opt/voice-lab")).resolve()
    _load_env_file(initial_root / ".env")

    root = Path(os.getenv("VOICE_LAB_ROOT", str(initial_root))).resolve()
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

ROOT = settings.root
INPUT_DIR = settings.input_dir
PROCESSING_DIR = settings.processing_dir
OUTPUT_WAV_DIR = settings.output_wav_dir
OUTPUT_MP3_DIR = settings.output_mp3_dir
LOGS_DIR = settings.logs_dir
MODELS_DIR = settings.models_dir
DATASETS_DIR = settings.datasets_dir
DEFAULT_SAMPLE_RATE = settings.default_sample_rate
OUTPUT_MP3_BITRATE = settings.output_mp3_bitrate
