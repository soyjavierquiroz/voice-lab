from __future__ import annotations

from pathlib import Path

from app.config import settings


class RvcRunnerError(RuntimeError):
    """Raised when the RVC/Applio engine is not ready."""


class RvcRunner:
    def __init__(self, engine_path: str | Path | None = None) -> None:
        self.engine_path = Path(engine_path).resolve() if engine_path else settings.rvc_engine_path

    def ensure_configured(self) -> None:
        if self.engine_path is None:
            raise RvcRunnerError(
                "RVC/Applio engine is not configured yet. Set RVC_ENGINE_PATH after installing "
                "the chosen engine in a future MVP phase."
            )
        if not self.engine_path.exists():
            raise RvcRunnerError(f"Configured RVC_ENGINE_PATH does not exist: {self.engine_path}")

    def infer(self, input_wav: str | Path, model_name: str, output_wav: str | Path) -> Path:
        self.ensure_configured()
        raise RvcRunnerError(
            "Real RVC/Applio inference is not implemented in Fase 1. "
            f"Requested input={input_wav}, model={model_name}, output={output_wav}."
        )


runner = RvcRunner()
