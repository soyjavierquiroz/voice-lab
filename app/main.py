from __future__ import annotations

from app.config import settings

try:
    from fastapi import FastAPI
except ImportError:  # FastAPI is optional in Fase 1.
    FastAPI = None  # type: ignore[assignment]


def create_app():
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Install optional API dependencies in a future phase.")

    app = FastAPI(title="voice-lab", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "root": str(settings.root),
            "model": settings.default_model_name,
        }

    return app


app = create_app() if FastAPI is not None else None
