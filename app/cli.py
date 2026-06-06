from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.audio_utils import export_mp3, normalize_to_wav, probe_audio
from app.config import settings


def _cmd_normalize(args: argparse.Namespace) -> int:
    output = normalize_to_wav(args.input, args.output, sample_rate=args.sample_rate)
    print(output)
    return 0


def _cmd_export_mp3(args: argparse.Namespace) -> int:
    output = export_mp3(args.input_wav, args.output_mp3, bitrate=args.bitrate)
    print(output)
    return 0


def _cmd_probe(args: argparse.Namespace) -> int:
    info = probe_audio(args.input)
    print(json.dumps(info, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m app.cli", description="voice-lab audio preparation tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    normalize = subparsers.add_parser("normalize", help="Convert MP3/M4A/WAV input to clean mono WAV")
    normalize.add_argument("--input", required=True, type=Path, help="Input MP3/M4A/WAV path")
    normalize.add_argument("--output", required=True, type=Path, help="Output WAV path")
    normalize.add_argument("--sample-rate", type=int, default=settings.default_sample_rate)
    normalize.set_defaults(func=_cmd_normalize)

    export = subparsers.add_parser("export-mp3", help="Export a WAV file to MP3")
    export.add_argument("--input-wav", required=True, type=Path, help="Input WAV path")
    export.add_argument("--output-mp3", required=True, type=Path, help="Output MP3 path")
    export.add_argument("--bitrate", default=settings.output_mp3_bitrate)
    export.set_defaults(func=_cmd_export_mp3)

    probe = subparsers.add_parser("probe", help="Show basic audio metadata")
    probe.add_argument("--input", required=True, type=Path, help="Input audio path")
    probe.set_defaults(func=_cmd_probe)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
