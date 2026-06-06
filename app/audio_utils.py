from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


class AudioToolError(RuntimeError):
    """Raised when an external audio tool is unavailable or fails."""


def _require_tool(name: str) -> str:
    tool_path = shutil.which(name)
    if not tool_path:
        raise AudioToolError(f"{name} is not installed or not available in PATH.")
    return tool_path


def _require_ffmpeg() -> str:
    return _require_tool("ffmpeg")


def _validate_input_file(path: str | Path) -> Path:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {source}")
    if not source.is_file():
        raise FileNotFoundError(f"Input path is not a file: {source}")
    return source


def build_normalize_to_wav_command(input_path: Path, output_path: Path, sample_rate: int = 40000) -> list[str]:
    return [
        _require_ffmpeg(),
        "-y",
        "-i",
        str(input_path),
        "-af",
        "highpass=f=40,lowpass=f=18000,loudnorm=I=-18:TP=-1.5:LRA=11",
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        "-c:a",
        "pcm_s16le",
        "-vn",
        "-f",
        "wav",
        str(output_path),
    ]


def build_export_mp3_command(input_wav: Path, output_mp3: Path, bitrate: str = "192k") -> list[str]:
    return [
        _require_ffmpeg(),
        "-y",
        "-i",
        str(input_wav),
        "-codec:a",
        "libmp3lame",
        "-b:a",
        bitrate,
        str(output_mp3),
    ]


def _run_ffmpeg(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise AudioToolError(f"ffmpeg failed: {detail}") from exc


def normalize_to_wav(input_path: str | Path, output_path: str | Path, sample_rate: int = 40000) -> Path:
    source = _validate_input_file(input_path)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    _run_ffmpeg(build_normalize_to_wav_command(source, target, sample_rate))
    return target


def export_mp3(input_wav: str | Path, output_mp3: str | Path, bitrate: str = "192k") -> Path:
    source = _validate_input_file(input_wav)
    target = Path(output_mp3)
    target.parent.mkdir(parents=True, exist_ok=True)
    _run_ffmpeg(build_export_mp3_command(source, target, bitrate))
    return target


def probe_audio(input_path: str | Path) -> dict[str, object]:
    source = _validate_input_file(input_path)
    info: dict[str, object] = {
        "path": str(source),
        "exists": True,
        "size_bytes": source.stat().st_size,
    }

    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        info["ffprobe_available"] = False
        return info

    command = [
        ffprobe,
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(source),
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        info["ffprobe_available"] = True
        info["probe_error"] = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        return info

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        info["ffprobe_available"] = True
        info["probe_error"] = f"Could not parse ffprobe output: {exc}"
        return info

    audio_stream = next(
        (stream for stream in data.get("streams", []) if stream.get("codec_type") == "audio"),
        {},
    )
    media_format = data.get("format", {})

    info.update(
        {
            "ffprobe_available": True,
            "format_name": media_format.get("format_name"),
            "duration_seconds": _optional_float(media_format.get("duration")),
            "bit_rate": _optional_int(media_format.get("bit_rate")),
            "codec_name": audio_stream.get("codec_name"),
            "sample_rate": _optional_int(audio_stream.get("sample_rate")),
            "channels": audio_stream.get("channels"),
            "channel_layout": audio_stream.get("channel_layout"),
        }
    )
    return info


def _optional_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _optional_int(value: object) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
