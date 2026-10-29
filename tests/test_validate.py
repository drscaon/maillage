"""Every generated file passes OpenUSD's own validators (what usdchecker runs)."""

import pytest

from maillage import generate_scene, write_outputs
from maillage.validate import main, validate


@pytest.mark.parametrize(
    ("preset", "topology"),
    [("tea_towel", "tri"), ("tablecloth", "tri"), ("bath_towel", "grid"), ("flag", "tri")],
)
def test_openusd_validators(preset, topology, tmp_path):
    scene = generate_scene(preset, count=2, topology=topology, vertices=400)
    folder = write_outputs(scene, tmp_path)
    files = sorted(folder.glob("*.usd*"))
    assert files
    for f in files:
        assert validate(f) == [], f.name


def test_command_line(tmp_path, capsys):
    write_outputs(generate_scene("napkin", count=1, vertices=300), tmp_path)
    assert main([str(tmp_path)]) == 0
    assert "0 with issues" in capsys.readouterr().out
