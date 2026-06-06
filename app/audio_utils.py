from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from app.config import settings


class AudioToolError(RuntimeError):
    """Raised when an external audio tool is unavailable or fails."""


def _require_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise AudioToolError("ffmpeg is not installed or not available in PATH.")
    return ffmpeg


def build_normalize_to_wav_command(input_path: Path, output_path: Path) -> list[str]:
    return [
        _require_ffmpeg(),
        "-y",
        "-i",
        str(input_path),
        "-ac",
        "1",
        "-ar",
        str(settings.default_sample_rate),
        "-vn",
        str(output_path),
    ]


def build_export_mp3_command(input_wav: Path, output_mp3: Path) -> list[str]:
    return [
        _require_ffmpeg(),
        "-y",
        "-i",
        str(input_wav),
        "-codec:a",
        "libmp3lame",
        "-b:a",
        settings.output_mp3_bitrate,
        str(output_mp3),
    ]


def _run_ffmpeg(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise AudioToolError(f"ffmpeg failed: {detail}") from exc


def normalize_to_wav(input_path: str | Path, output_path: str | Path) -> Path:
    source = Path(input_path)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    _run_ffmpeg(build_normalize_to_wav_command(source, target))
    return target


def export_mp3(input_wav: str | Path, output_mp3: str | Path) -> Path:
    source = Path(input_wav)
    target = Path(output_mp3)
    target.parent.mkdir(parents=True, exist_ok=True)
    _run_ffmpeg(build_export_mp3_command(source, target))
    return target
