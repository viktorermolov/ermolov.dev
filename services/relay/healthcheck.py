"""Liveness check; external outages remain visible as degraded in health.json."""

import json
import os
import time
from pathlib import Path


def healthy(path, now=None):
    try:
        state = json.loads(path.read_text())
        age = (time.time() if now is None else now) - state["heartbeat"]
        return 0 <= age <= 180 and state["status"] in {"ok", "processing", "degraded"}
    except (OSError, ValueError, KeyError, TypeError):
        return False


if __name__ == "__main__":
    path = Path(os.environ.get("RELAY_STATE_DIR", "/app/state")) / "health.json"
    raise SystemExit(0 if healthy(path) else 1)
