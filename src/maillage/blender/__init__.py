"""Blender validation. drop_test.py runs inside Blender (or with the bpy module)
and does not import maillage, so Blender's own Python needs nothing installed."""

from pathlib import Path

DROP_TEST_SCRIPT = Path(__file__).with_name("drop_test.py")
