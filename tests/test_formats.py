import pytest

from maillage import generate_scene
from maillage.formats import describe, parse_format, parse_formats


@pytest.mark.parametrize(
    "text,expected",
    [
        ("50x70", {"width": 50, "length": 70, "shape": "rect", "weight": 1}),
        ("70×50", {"width": 50, "length": 70, "shape": "rect", "weight": 1}),
        ("rect:45x65@3", {"width": 45, "length": 65, "shape": "rect", "weight": 3}),
        ("oval:140x200", {"width": 140, "length": 200, "shape": "ellipse", "weight": 1}),
        ("ellipse:200x140@0.5", {"width": 140, "length": 200, "shape": "ellipse", "weight": 0.5}),
        ("round:150", {"width": 150, "length": 150, "shape": "ellipse", "weight": 1}),
        (" Round:37.5 ", {"width": 37.5, "length": 37.5, "shape": "ellipse", "weight": 1}),
    ],
)
def test_parse_text(text, expected):
    assert parse_format(text) == expected


def test_parse_dict_and_tuple():
    assert parse_format({"width": 30, "length": 180}) == parse_format("30x180")
    assert parse_format((150, 150, "round")) == parse_format("round:150")
    assert parse_formats("50x70, round:40") == [parse_format("50x70"), parse_format("round:40")]


@pytest.mark.parametrize(
    "bad", ["50x", "x70", "hex:50x70", "round:50x70", "50x70@heavy", "0x70", "50x70@0", ""]
)
def test_bad_formats(bad):
    with pytest.raises(ValueError):
        parse_formats(bad)


def test_describe():
    assert [describe(parse_format(t)) for t in ("50x70", "round:150", "oval:140x200")] == [
        "50×70",
        "⌀150",
        "oval 140×200",
    ]


def test_custom_formats_replace_the_presets():
    s = generate_scene("napkin", count=30, vertices=100, formats="30x30@3, round:45")
    nominal = {(p.shape, round(p.nominal[0], 3), round(p.nominal[1], 3)) for p in s.pieces}
    assert nominal == {("rect", 0.3, 0.3), ("ellipse", 0.45, 0.45)}
    assert sum(p.shape == "rect" for p in s.pieces) > sum(p.shape == "ellipse" for p in s.pieces)


def test_custom_formats_and_grid_topology():
    s = generate_scene("napkin", count=6, vertices=100, topology="grid", formats="40x60, round:50")
    assert {p.shape for p in s.pieces} == {"rect"}
    with pytest.raises(ValueError):
        generate_scene("napkin", count=1, topology="grid", formats="round:50")
