"""Every cloth piece draws what docs/variation.md declares (PRV-34).

For every preset, a thousand pieces are drawn with fixed seeds (the mesh and the texture are not
built: they are replaced by a fixed stand-in, as they draw nothing that is recorded), so the result
is the same on every run. Every value must lie in its declared range and follow its rule
(chi-square for choices, Kolmogorov-Smirnov for numbers, at p > 0.001), and a piece must record
exactly the declared values and those of its pattern. The rules are in maillage.declared, which
also writes the documentation.
"""

from pathlib import Path

import numpy as np
import pytest
from scipy import stats

from maillage import declared, generator
from maillage import mesh as meshing
from maillage.outline import Outline
from maillage.presets import PRESETS

N = 1000
P_MIN = 1e-3
SEED = 20261116
DOC = Path(__file__).parents[1] / "docs" / "variation.md"


@pytest.fixture(scope="module")
def stand_in():
    """One real mesh and its metrics, reused for every piece: the draws do not depend on them."""
    m = meshing.build(Outline("rect", 0.5, 0.4, 0.0), "tri", 300, np.random.default_rng(0))
    return m, meshing.metrics(m)


def draws(key, stand_in, monkeypatch):
    m, met = stand_in
    monkeypatch.setattr(generator.meshing, "build", lambda *a, **k: m)
    monkeypatch.setattr(generator.meshing, "metrics", lambda *a, **k: met)
    monkeypatch.setattr(generator.texture, "render", lambda *a, **k: np.zeros((2, 2, 3)))
    var = generator.Variations()
    return [generator.make_piece(key, i, SEED, var, "tri", 300).variation for i in range(N)]


def chi2(values, weights: dict, what):
    keys = list(weights)
    observed = np.array([sum(v == k for v in values) for k in keys])
    assert observed.sum() == len(values), f"{what}: a value outside {keys}"
    if len(keys) > 1:
        p = np.array([weights[k] for k in keys], float)
        assert stats.chisquare(observed, p / p.sum() * len(values)).pvalue > P_MIN, f"{what}: {observed}"


def uniform(values, lo, hi, what):
    values = np.asarray(values, float)
    assert lo - 1e-12 <= values.min() and values.max() <= hi + 1e-12, f"{what}: outside {lo} to {hi}"
    if hi > lo and len(values) >= 30:
        assert stats.kstest(values, stats.uniform(lo, hi - lo).cdf).pvalue > P_MIN, what


def clipped_normal(e, what):
    assert np.all(np.abs(e) <= declared.CLIP + 1e-9), f"{what}: beyond ±{declared.CLIP}"
    inner = e[np.abs(e) < declared.CLIP - 1e-9]
    _, repeats = np.unique(np.round(inner, 7), return_counts=True)
    assert repeats.max() < 3, f"{what}: a value repeated inside ±{declared.CLIP}: clipped elsewhere?"
    assert stats.kstest(inner, stats.truncnorm(-declared.CLIP, declared.CLIP).cdf).pvalue > P_MIN, what
    at, expected = len(e) - len(inner), 2 * stats.norm.sf(declared.CLIP) * len(e)
    assert abs(at - expected) < 3.5 * np.sqrt(expected) + 1, f"{what}: {at} at ±{declared.CLIP}"


@pytest.mark.slow
@pytest.mark.parametrize("key", list(PRESETS))
def test_drawn_as_declared(key, stand_in, monkeypatch):
    p, rows = PRESETS[key], draws(key, stand_in, monkeypatch)
    base_columns = {c for c, _a, _how in declared.DECLARED}
    for row in rows:
        own = {declared.pattern_column(n, r) for n, r in declared.PATTERNS[row["pattern"]].items()}
        assert set(row) == base_columns | own, f"{key}: records {sorted(set(row) ^ (base_columns | own))}"

    # format and size
    formats = [(f["shape"], f["length"] / 100, f["width"] / 100) for f in p["formats"]]
    drawn = [(r["format_shape"], r["format_length_m"], r["format_width_m"]) for r in rows]
    weights = {}
    for f, spec in zip(formats, p["formats"], strict=True):
        weights[f] = weights.get(f, 0) + spec["weight"]
    chi2(drawn, weights, f"{key}: format")
    for size, nominal in (("length_m", "format_length_m"), ("width_m", "format_width_m")):
        e = np.array([(r[size] / r[nominal] - 1) / p["tolerance"] for r in rows])
        clipped_normal(e, f"{key}: {size}")

    # corners: none on an ellipse
    lo, hi = (x / 100 for x in p["corner_radius"])
    rect = [r["corner_radius_m"] for r in rows if r["format_shape"] == "rect"]
    assert all(r["corner_radius_m"] == 0 for r in rows if r["format_shape"] != "rect"), key
    uniform(rect, lo, hi, f"{key}: corner_radius_m")

    # the cut
    w_lo, w_hi = (x * 1e-3 for x in p["cut"]["waviness_mm"])
    amps = np.array([r["cut_amplitudes_m"] for r in rows])
    total = amps[:, 0] + amps[:, 1] + amps[:, 2] / 0.3
    uniform(total, w_lo, w_hi, f"{key}: cut amplitude")
    share = amps[:, 0] / total
    assert stats.kstest(share, stats.beta(2, 4).cdf).pvalue > P_MIN, f"{key}: cut shares"
    cycles = np.array([r["cut_cycles"] for r in rows])
    for i, (c_lo, c_hi) in enumerate(((2, 5), (5, 11), (18, 39))):
        chi2(list(cycles[:, i]), {float(k): 1 for k in range(c_lo, c_hi + 1)}, f"{key}: cut cycles {i}")
    skew = p["cut"]["skew_deg"]
    uniform([r["cut_skew_deg"] for r in rows], -skew, skew, f"{key}: cut_skew_deg")

    # fabric, pattern, colours
    chi2([r["fabric"] for r in rows], p["fabrics"], f"{key}: fabric")
    chi2([r["pattern"] for r in rows], p["patterns"], f"{key}: pattern")
    plain = [r for r in rows if r["pattern"] != "bands"]
    if plain:
        chi2([r["colors"][0] for r in plain], dict.fromkeys(p["base_colors"], 1), f"{key}: base colour")
    for r in plain:
        if r["pattern"] == "solid":
            assert len(r["colors"]) == 1, f"{key}: a solid piece paints one colour"
        else:
            base, accent = r["colors"]
            assert accent in p["accent_colors"] and accent != base, f"{key}: accent {accent}"
    bands = [r for r in rows if r["pattern"] == "bands"]
    if bands:
        three = sum(len(r["colors"]) == 3 for r in bands)
        assert all(len(r["colors"]) in (2, 3) for r in bands), key
        assert abs(three - 0.7 * len(bands)) < 3.5 * np.sqrt(0.21 * len(bands)) + 1, f"{key}: {three} with 3"

    # the pattern's own values
    for pattern, params in declared.PATTERNS.items():
        mine = [r for r in rows if r["pattern"] == pattern]
        for name, rule in params.items():
            column, what = declared.pattern_column(name, rule), f"{key}: {pattern} {name}"
            values = [r[column] for r in mine]
            if not values:
                continue
            if rule[0] == "uniform":
                uniform(values, rule[1], rule[2], what)
            elif rule[0] == "times":
                other = [r[declared.pattern_column(rule[1], ("uniform",))] for r in mine]
                uniform(np.array(values) / np.array(other), rule[2], rule[3], what)
            else:
                yes = sum(values)
                n = len(values)
                assert abs(yes - rule[1] * n) < 3.5 * np.sqrt(rule[1] * (1 - rule[1]) * n) + 1, (
                    f"{what}: {yes}/{n}"
                )


def test_documentation_is_the_declaration():
    text = DOC.read_text(encoding="utf-8")
    begin, end = "<!-- declared: begin -->\n", "<!-- declared: end -->"
    assert begin in text and end in text, "docs/variation.md has lost its markers"
    block = text[text.index(begin) + len(begin) : text.index(end)].strip()
    stale = "docs/variation.md is out of date: python -m maillage.declared"
    assert block == declared.table().strip(), stale
