import struct
import zlib

import numpy as np
import pytest

from maillage import texture


def _read_png(path):
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    w, h = struct.unpack(">II", data[16:24])
    idat = data[data.index(b"IDAT") + 4 : data.index(b"IEND") - 8]
    raw = zlib.decompress(idat)
    rows = np.frombuffer(raw, np.uint8).reshape(h, 1 + 3 * w)
    return rows[:, 1:].reshape(h, w, 3)


def test_png_round_trip(tmp_path):
    img = np.random.default_rng(0).random((20, 30, 3))
    out = _read_png(texture.write_png(tmp_path / "t.png", img))
    assert out.shape == (20, 30, 3)
    assert np.abs(out / 255.0 - img).max() <= 0.5 / 255 + 1e-9


@pytest.mark.parametrize("pattern", texture.PATTERNS)
def test_every_pattern_renders(pattern):
    rng = np.random.default_rng(1)
    spec = texture.draw_pattern(rng, pattern, ["#ffffff", "#204080"], ["#c03020", "#000000"])
    img = texture.render(spec, 0.7, 0.5, rng, max_px=256)
    assert img.shape == (round(0.5 * 256 / 0.7), 256, 3)
    assert 0.0 <= img.min() and img.max() <= 1.0


def test_adjacent_bands_differ():
    for seed in range(30):
        rng = np.random.default_rng(seed)
        spec = texture.draw_pattern(rng, "bands", ["#ffffff", "#c62828"], ["#1565c0", "#ffffff"])
        c = spec["colors"]
        assert all(a != b for a, b in zip(c, c[1:], strict=False))


def test_unknown_pattern():
    with pytest.raises(ValueError):
        texture.draw_pattern(np.random.default_rng(0), "paisley", ["#ffffff"], ["#000000"])


def test_srgb_to_linear():
    assert texture.srgb_to_linear(1.0) == pytest.approx(1.0)
    assert texture.srgb_to_linear(0.5) == pytest.approx(0.214, abs=1e-3)


def test_flag_bands_are_unequal_and_asymmetric():
    for seed in range(50):
        rng = np.random.default_rng(seed)
        spec = texture.draw_pattern(rng, "bands", ["#ffffff", "#c62828"], ["#1565c0", "#ffffff"])
        w = spec["widths"]
        assert sum(w) == pytest.approx(1.0) and min(w) >= 0.12
        assert max(w) / min(w) >= 1.4
        assert abs(w[0] - w[-1]) >= 0.12
