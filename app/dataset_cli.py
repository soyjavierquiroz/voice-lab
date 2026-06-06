from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.audio_utils import AudioToolError, clean_dataset_audio_to_wav, probe_audio
from app.config import settings


AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac"}
COMMON_SAMPLE_RATES = {8000, 11025, 16000, 22050, 24000, 32000, 40000, 44100, 48000, 88200, 96000}


class DatasetLogger:
    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.log_path.open("a", encoding="utf-8")

    def close(self) -> None:
        self._handle.close()

    def write(self, message: str) -> None:
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        line = f"[{timestamp}] {message}"
        print(line)
        self._handle.write(line + "\n")
        self._handle.flush()


def _dataset_dir(dataset_name: str) -> Path:
    return settings.datasets_dir / dataset_name


def _dataset_paths(dataset_name: str) -> dict[str, Path]:
    root = _dataset_dir(dataset_name)
    return {
        "root": root,
        "raw": root / "raw",
        "clean": root / "clean",
        "metadata": root / "metadata",
        "logs": root / "logs",
    }


def _audio_files(raw_dir: Path) -> list[Path]:
    if not raw_dir.exists():
        return []
    return sorted(
        path
        for path in raw_dir.iterdir()
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
    )


def _round_seconds(value: float | int | None) -> float:
    if value is None:
        return 0.0
    return round(float(value), 3)


def _duration(info: dict[str, Any]) -> float:
    return _round_seconds(info.get("duration_seconds"))


def _minutes(seconds: float) -> float:
    return round(seconds / 60, 2)


def _clean_output_path(clean_dir: Path, raw_file: Path) -> Path:
    return clean_dir / f"{raw_file.stem}.clean.wav"


def _file_probe_summary(path: Path) -> dict[str, Any]:
    info = probe_audio(path)
    return {
        "path": str(path),
        "duration_seconds": info.get("duration_seconds"),
        "sample_rate": info.get("sample_rate"),
        "channels": info.get("channels"),
        "codec_name": info.get("codec_name"),
        "bit_rate": info.get("bit_rate"),
        "ffprobe_available": info.get("ffprobe_available"),
        "probe_error": info.get("probe_error"),
    }


def _warning_for_duration(total_seconds: float) -> str:
    minutes = total_seconds / 60
    if minutes < 10:
        return "menos de 10 minutos: minimo viable bajo para RVC"
    if minutes < 30:
        return "10 a 30 minutos: usable pero puede mejorar"
    if minutes < 60:
        return "30 a 60 minutos: bueno"
    return "mas de 60 minutos: muy bueno, revisar consistencia"


def _file_warnings(raw_file: Path, raw_probe: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    duration = raw_probe.get("duration_seconds")
    sample_rate = raw_probe.get("sample_rate")
    channels = raw_probe.get("channels")

    if isinstance(duration, (int, float)):
        if duration < 2:
            warnings.append(f"{raw_file.name}: duracion menor a 2 segundos")
        if duration > 20 * 60:
            warnings.append(f"{raw_file.name}: duracion mayor a 20 minutos")

    if isinstance(channels, int) and channels > 1:
        warnings.append(f"{raw_file.name}: canales > 1 en raw ({channels})")

    if isinstance(sample_rate, int) and sample_rate not in COMMON_SAMPLE_RATES:
        warnings.append(f"{raw_file.name}: sample rate raro ({sample_rate} Hz)")

    if raw_probe.get("probe_error"):
        warnings.append(f"{raw_file.name}: ffprobe no pudo leer metadata")

    return warnings


def _write_report(report_path: Path, report: dict[str, Any]) -> None:
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown_report(report_path: Path, report: dict[str, Any]) -> None:
    lines = [
        f"# Dataset report: {report['dataset_name']}",
        "",
        f"- Generated UTC: {report['generated_at']}",
        f"- Raw dir: `{report['raw_dir']}`",
        f"- Clean dir: `{report['clean_dir']}`",
        f"- Raw files: {report['total_raw_files']}",
        f"- Clean files: {report['total_clean_files']}",
        f"- Raw duration: {report['total_duration_minutes_raw']} min ({report['total_duration_seconds_raw']} s)",
        f"- Clean duration: {report['total_duration_minutes_clean']} min ({report['total_duration_seconds_clean']} s)",
        "",
        "## Warnings",
        "",
    ]

    warnings = report.get("warnings", [])
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- Sin warnings.")

    lines.extend(["", "## Files", "", "| File | Status | Duration raw | Output |", "| --- | --- | ---: | --- |"])
    for item in report.get("files", []):
        raw_name = Path(item["raw_path"]).name
        duration = item.get("raw_probe", {}).get("duration_seconds")
        duration_text = "" if duration is None else str(round(float(duration), 3))
        output = item.get("clean_path") or ""
        if item.get("error"):
            output = f"ERROR: {item['error']}"
        lines.append(f"| {raw_name} | {item['status']} | {duration_text} | `{output}` |")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _print_scan_summary(dataset_name: str, raw_dir: Path, files: list[Path], probes: list[dict[str, Any]]) -> None:
    total_seconds = sum(_duration(info) for info in probes)
    print(f"Dataset: {dataset_name}")
    print(f"Raw dir: {raw_dir}")
    print(f"Audio files: {len(files)}")
    print(f"Total raw duration: {_minutes(total_seconds)} min ({round(total_seconds, 3)} s)")
    print()
    for path, info in zip(files, probes):
        duration = info.get("duration_seconds")
        duration_text = "unknown" if duration is None else f"{round(float(duration), 3)}s"
        sample_rate = info.get("sample_rate") or "unknown"
        channels = info.get("channels") or "unknown"
        codec = info.get("codec_name") or "unknown"
        bit_rate = info.get("bit_rate") or "unknown"
        print(f"- {path.name}: {duration_text}, {sample_rate} Hz, {channels} ch, codec={codec}, bit_rate={bit_rate}")
        if info.get("probe_error"):
            print(f"  probe_error: {info['probe_error']}")


def _cmd_scan(args: argparse.Namespace) -> int:
    paths = _dataset_paths(args.dataset)
    files = _audio_files(paths["raw"])
    probes = [_file_probe_summary(path) for path in files]
    _print_scan_summary(args.dataset, paths["raw"], files, probes)
    if not paths["raw"].exists():
        print(f"WARNING: raw dir does not exist: {paths['raw']}")
    return 0


def _build_report(dataset_name: str, paths: dict[str, Path], files_report: list[dict[str, Any]]) -> dict[str, Any]:
    clean_files = sorted(paths["clean"].glob("*.clean.wav")) if paths["clean"].exists() else []
    clean_probes = [_file_probe_summary(path) for path in clean_files]
    raw_duration = sum(_duration(item.get("raw_probe", {})) for item in files_report)
    clean_duration = sum(_duration(info) for info in clean_probes)

    warnings = [_warning_for_duration(raw_duration)]
    for item in files_report:
        warnings.extend(_file_warnings(Path(item["raw_path"]), item.get("raw_probe", {})))

    return {
        "dataset_name": dataset_name,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "raw_dir": str(paths["raw"]),
        "clean_dir": str(paths["clean"]),
        "total_raw_files": len(files_report),
        "total_clean_files": len(clean_files),
        "total_duration_seconds_raw": round(raw_duration, 3),
        "total_duration_minutes_raw": _minutes(raw_duration),
        "total_duration_seconds_clean": round(clean_duration, 3),
        "total_duration_minutes_clean": _minutes(clean_duration),
        "files": files_report,
        "warnings": warnings,
    }


def _cmd_prepare(args: argparse.Namespace) -> int:
    paths = _dataset_paths(args.dataset)
    paths["clean"].mkdir(parents=True, exist_ok=True)
    paths["metadata"].mkdir(parents=True, exist_ok=True)
    paths["logs"].mkdir(parents=True, exist_ok=True)

    logger = DatasetLogger(paths["logs"] / "prepare_dataset.log")
    failures = 0
    files_report: list[dict[str, Any]] = []

    try:
        logger.write(f"Preparing dataset={args.dataset} sample_rate={args.sample_rate} overwrite={args.overwrite}")
        logger.write(f"Raw dir: {paths['raw']}")
        logger.write(f"Clean dir: {paths['clean']}")

        raw_files = _audio_files(paths["raw"])
        if not paths["raw"].exists():
            logger.write(f"WARNING raw dir does not exist: {paths['raw']}")
        if not raw_files:
            logger.write("No raw audio files found.")

        for raw_file in raw_files:
            clean_file = _clean_output_path(paths["clean"], raw_file)
            raw_probe = _file_probe_summary(raw_file)
            item: dict[str, Any] = {
                "raw_path": str(raw_file),
                "clean_path": str(clean_file),
                "status": "skipped",
                "raw_probe": raw_probe,
                "clean_probe": None,
                "error": None,
            }

            if clean_file.exists() and not args.overwrite:
                logger.write(f"SKIP {raw_file.name}: output exists ({clean_file.name})")
                item["status"] = "skipped"
                item["clean_probe"] = _file_probe_summary(clean_file)
                files_report.append(item)
                continue

            try:
                clean_dataset_audio_to_wav(raw_file, clean_file, sample_rate=args.sample_rate, overwrite=args.overwrite)
                item["status"] = "processed"
                item["clean_probe"] = _file_probe_summary(clean_file)
                logger.write(f"OK {raw_file.name} -> {clean_file.name}")
            except (AudioToolError, FileNotFoundError, RuntimeError) as exc:
                failures += 1
                item["status"] = "failed"
                item["error"] = str(exc)
                logger.write(f"FAIL {raw_file.name}: {exc}")
            files_report.append(item)

        report = _build_report(args.dataset, paths, files_report)
        _write_report(paths["metadata"] / "report.json", report)
        _write_markdown_report(paths["metadata"] / "report.md", report)
        logger.write(f"Report JSON: {paths['metadata'] / 'report.json'}")
        logger.write(f"Report MD: {paths['metadata'] / 'report.md'}")
        logger.write(
            "Summary: "
            f"raw_files={report['total_raw_files']} clean_files={report['total_clean_files']} "
            f"raw_minutes={report['total_duration_minutes_raw']} clean_minutes={report['total_duration_minutes_clean']} "
            f"failures={failures}"
        )
    finally:
        logger.close()

    return 1 if failures else 0


def _cmd_report(args: argparse.Namespace) -> int:
    paths = _dataset_paths(args.dataset)
    report_path = paths["metadata"] / "report.json"
    if not report_path.exists():
        print(f"No existe reporte para dataset '{args.dataset}'. Ejecuta primero:")
        print(f"python -m app.dataset_cli prepare --dataset {args.dataset}")
        return 1

    report = json.loads(report_path.read_text(encoding="utf-8"))
    print(f"Dataset: {report['dataset_name']}")
    print(f"Generated UTC: {report['generated_at']}")
    print(f"Raw files: {report['total_raw_files']}")
    print(f"Clean files: {report['total_clean_files']}")
    print(f"Raw duration: {report['total_duration_minutes_raw']} min ({report['total_duration_seconds_raw']} s)")
    print(f"Clean duration: {report['total_duration_minutes_clean']} min ({report['total_duration_seconds_clean']} s)")
    print("Files:")
    for item in report.get("files", []):
        name = Path(item["raw_path"]).name
        print(f"- {name}: {item['status']}")
    print("Warnings:")
    for warning in report.get("warnings", []):
        print(f"- {warning}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m app.dataset_cli", description="voice-lab dataset preparation tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan raw dataset audio files without modifying them")
    scan.add_argument("--dataset", required=True, help="Dataset name under datasets/")
    scan.set_defaults(func=_cmd_scan)

    prepare = subparsers.add_parser("prepare", help="Prepare clean WAV files and dataset metadata")
    prepare.add_argument("--dataset", required=True, help="Dataset name under datasets/")
    prepare.add_argument("--sample-rate", type=int, default=settings.default_sample_rate)
    prepare.add_argument("--overwrite", action="store_true", help="Overwrite existing clean WAV outputs")
    prepare.set_defaults(func=_cmd_prepare)

    report = subparsers.add_parser("report", help="Print the latest dataset report")
    report.add_argument("--dataset", required=True, help="Dataset name under datasets/")
    report.set_defaults(func=_cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except (FileNotFoundError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
