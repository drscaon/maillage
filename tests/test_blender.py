"""Blender drop test, run in a subprocess (Blender's USD and usd-core's must not
share a process). Skipped when the bpy module is not installed."""

import importlib.util
import json
import subprocess
import sys

import pytest

pytestmark = pytest.mark.skipif(importlib.util.find_spec("bpy") is None, reason="bpy not installed")


@pytest.mark.parametrize("preset,scenario", [("washcloth", "drape"), ("flag", "hang")])
def test_drop_test(tmp_path, preset, scenario):
    run = [sys.executable, "-m", "maillage"]
    gen = ["generate", "--preset", preset, "--count", "1", "--vertices", "400", "--out", str(tmp_path)]
    subprocess.run(run + gen, check=True, capture_output=True)
    folder = tmp_path / preset
    result = subprocess.run(
        run + ["drop-test", str(folder), "--pieces", "1", "--frames", "72"], capture_output=True, text=True
    )
    report = json.loads((folder / "drop_test" / "drop_test.json").read_text())
    piece = report["pieces"][0]
    assert piece["scenario"] == scenario
    assert piece["finite"]
    assert piece["checks"]["stretch"], piece
    assert piece["checks"]["penetration"], piece
    assert (folder / "drop_test" / "draped.usdc").exists()
    assert result.returncode in (0, 1)
