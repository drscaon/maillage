"""Change one thing and nothing else: the aspects of Maillage.

What varies from one piece to the next is split into aspects (size, cut,
corners, fabric, color), each with its own random stream. Turning one aspect
off leaves the draws of the others as they were. With the same seed you get
the same pieces with a single difference, which is what you want when you
study what a robot or a perception model is sensitive to.

Here: the same napkins twice, the second time with a perfect cut (no wavy
edges, no skew). Sizes, fabrics and patterns stay the same, piece for piece.

    python examples/02_one_aspect_at_a_time.py
"""

from maillage import Variations, generate_scene

SEED = 5

varied = generate_scene("napkin", count=5, vertices=200, seed=SEED)
perfect = generate_scene("napkin", count=5, vertices=200, seed=SEED, variations=Variations(cut=False))

print(f"{'piece':12s} {'skew (deg)':>20s} {'length (cm)':>20s}  fabric, pattern")
print(f"{'':12s} {'varied':>10s} {'cut off':>9s} {'varied':>10s} {'cut off':>9s}")
for a, b in zip(varied.pieces, perfect.pieces, strict=True):
    va, vb = a.variation, b.variation
    print(
        f"{a.name:12s} {va['cut_skew_deg']:10.2f} {vb['cut_skew_deg']:9.2f} "
        f"{va['length_m'] * 100:10.1f} {vb['length_m'] * 100:9.1f}  {va['fabric']}, {va['pattern']}"
    )

# The cut changed; the rest did not.
assert all(p.variation["cut_skew_deg"] == 0 for p in perfect.pieces)
for name in ("length_m", "width_m", "fabric", "pattern", "colors"):
    assert [p.variation[name] for p in varied.pieces] == [p.variation[name] for p in perfect.pieces], name
print("\nsame seed, cut switched off: straight edges, same sizes, fabrics and patterns")
