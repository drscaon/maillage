import json

import pytest

from maillage import __version__
from maillage.cli import main


def test_list(capsys):
    assert main(["list"]) == 0
    out = capsys.readouterr().out
    assert "tea_towel" in out and "Fabrics" in out and "silk" in out


def test_version(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])
    assert __version__ in capsys.readouterr().out


def test_generate(tmp_path, capsys):
    code = main(
        [
            "generate",
            "--preset",
            "napkin",
            "--count",
            "2",
            "--vertices",
            "200",
            "--no-color",
            "--out",
            str(tmp_path),
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    summary = json.loads(out[: out.rindex("}") + 1])
    assert summary["count"] == 2 and summary["variations"]["color"] is False
    assert (tmp_path / "napkin" / "maillage_napkin.usdc").exists()


def test_generate_grid_topology(tmp_path, capsys):
    code = main(
        ["generate", "--preset", "napkin", "--topology", "grid", "--count", "1", "--out", str(tmp_path)]
    )
    assert code == 0


def test_count_must_be_positive(capsys):
    with pytest.raises(SystemExit):
        main(["generate", "--count", "0"])


def test_preview(tmp_path):
    pytest.importorskip("matplotlib")
    main(["generate", "--preset", "washcloth", "--count", "2", "--vertices", "150", "--out", str(tmp_path)])
    assert main(["preview", str(tmp_path / "washcloth")]) == 0
    assert (tmp_path / "washcloth" / "sheet.png").stat().st_size > 1000


def test_blender_script_path(capsys):
    assert main(["blender-script"]) == 0
    assert capsys.readouterr().out.strip().endswith("drop_test.py")


def test_gif_from_frames(tmp_path):
    pytest.importorskip("PIL")
    import numpy as np
    from PIL import Image

    from maillage.animate import make_gif

    for i in range(3):
        Image.fromarray(np.full((45, 80, 3), 60 * i, np.uint8)).save(tmp_path / f"frame_{i:04d}.png")
    gif = make_gif(tmp_path, tmp_path / "a.gif")
    with Image.open(gif) as im:
        assert im.n_frames == 3


def test_fabric_list_option(tmp_path, capsys):
    out = ["--out", str(tmp_path)]
    assert (
        main(
            ["generate", "--preset", "napkin", "--count", "2", "--vertices", "150", "--fabric", "silk,linen"]
            + out
        )
        == 0
    )
    with pytest.raises(SystemExit):
        main(["generate", "--fabric", "velvet"])
