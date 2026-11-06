"""Replay independent contract checks for both recorded code-task results."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent

for arm in ("baseline", "candidate"):
    path = ROOT / "results" / ("code-" + arm) / "ports.py"
    spec = importlib.util.spec_from_file_location("ports_" + arm, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for raw, expected in (("1", 1), ("80", 80), ("65535", 65535), (" 443 ", 443)):
        actual = module.parse_port(raw)
        if actual != expected:
            raise AssertionError(f"{arm}: {raw!r}: expected {expected}, got {actual}")
    for raw in ("0", "-1", "65536", "abc"):
        try:
            module.parse_port(raw)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{arm}: {raw!r}: expected ValueError")
    print(f"{arm}: 8/8 independent contract checks passed")
