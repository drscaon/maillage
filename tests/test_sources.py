"""Every physical value names its source, and lies in the range its source gives (PRV-33).

docs/sources.md is written from maillage.sources; this test fails on a value of the catalogue with no
source, on a source that is neither cited nor an explained estimate, on a value outside the range its
source gives, and when the page is not the module's tables. A fabric's values are the same for every
piece made of it (no draw), so the values themselves are what is checked.
"""

import numbers
from pathlib import Path

import pytest

from maillage import sources
from maillage.fabrics import FABRICS
from maillage.presets import PRESETS

DOC = Path(__file__).parents[1] / "docs" / "sources.md"
BY_PATH = {v.path: v for v in sources.values()}
NOT_PHYSICAL = ("blender", "roughness")


def test_every_number_of_the_catalogue_names_its_source():
    expected = []
    for key, f in FABRICS.items():
        for field, x in f.items():
            if field not in NOT_PHYSICAL and isinstance(x, numbers.Number):
                expected.append(f"FABRICS.{key}.{field}")
    for key, p in PRESETS.items():
        for i, _ in enumerate(p["formats"]):
            expected += [f"PRESETS.{key}.formats.{i}.width", f"PRESETS.{key}.formats.{i}.length"]
        expected += [f"PRESETS.{key}.tolerance", f"PRESETS.{key}.hem", f"PRESETS.{key}.cut.skew_deg"]
        expected += [f"PRESETS.{key}.corner_radius.{e}" for e in ("min", "max")]
        expected += [f"PRESETS.{key}.cut.waviness_mm.{e}" for e in ("min", "max")]
    missing = [path for path in expected if path not in BY_PATH]
    assert not missing, f"no source for {missing}"


def test_values_are_the_code_values():
    for key, f in FABRICS.items():
        assert BY_PATH[f"FABRICS.{key}.areal_density"].value == pytest.approx(f["areal_density"] * 1e3)
        assert BY_PATH[f"FABRICS.{key}.friction"].value == f["friction"]
        assert BY_PATH[f"FABRICS.{key}.bending_rigidity"].value == f["bending_rigidity"]


@pytest.mark.parametrize("key", list(sources.SOURCES))
def test_a_source_is_cited_or_an_explained_estimate(key):
    s = sources.SOURCES[key]
    assert s.kind in sources.KINDS
    if s.kind == "estimate":
        assert s.note, f"{key}: an estimate says what it rests on"
    else:
        assert s.urls and all(u.startswith("https://") for u in s.urls), f"{key}: where to read it"


def test_every_source_is_used():
    used = {v.source for v in sources.values()}
    assert set(sources.SOURCES) == used, set(sources.SOURCES) - used


def test_every_value_lies_in_the_range_its_source_gives():
    for v in sources.values():
        assert v.source in sources.SOURCES, v.path
        if v.low is not None:
            assert v.value >= v.low - 1e-9, v.path
        if v.high is not None:
            assert v.value <= v.high + 1e-9, v.path


def test_documentation_is_the_sources():
    text = DOC.read_text(encoding="utf-8")
    start, end = "<!-- sources: begin -->\n", "<!-- sources: end -->"
    assert start in text and end in text
    written = text[text.index(start) + len(start) : text.index(end)]
    assert written.strip() == sources.table().strip(), "docs/sources.md: run python -m maillage.sources"
