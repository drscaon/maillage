"""Command-line interface.

maillage list
maillage generate --preset tea_towel [--count 12] [--seed 1] [--topology tri|grid] [--vertices 1500]
                  [--fabric linen] [--format 50x70,oval:140x200,round:150]
                  [--no-size] [--no-cut] [--no-corners] [--no-color] [--out output]
maillage preview output/tea_towel
maillage drop-test output/tea_towel [--pieces 4] [--frames 120] [--render] [--gif]   (Blender)
maillage sim-test output/tea_towel [--pieces 4] [--seconds 5]                       (MuJoCo, needs [sim])
maillage blender-script
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from . import __version__
from .blender import DROP_TEST_SCRIPT
from .fabrics import FABRICS
from .formats import describe, parse_formats
from .generator import Variations, generate_scene, summarize, write_outputs
from .mesh import TOPOLOGIES
from .presets import CATEGORIES, PRESETS

VARIATION_HELP = {
    "size": "format and size drawn (off: first format, exact size)",
    "cut": "wavy edges and slight skew (off: perfect cut)",
    "corners": "corner radius drawn (off: middle of the range)",
    "color": "pattern and colours drawn (off: first pattern and colours)",
}


def _positive_int(text: str) -> int:
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, got {value}")
    return value


def _formats(text: str):
    try:
        return parse_formats(text)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e)) from e


def _fabrics(text: str):
    names = [n.strip() for n in text.split(",") if n.strip()]
    unknown = [n for n in names if n not in FABRICS]
    if unknown or not names:
        raise argparse.ArgumentTypeError(f"unknown fabric(s) {unknown}; choose from {', '.join(FABRICS)}")
    return names[0] if len(names) == 1 else names


def _cmd_list(_args) -> int:
    for c in CATEGORIES:
        print(c)
        for k, p in PRESETS.items():
            if p["category"] != c:
                continue
            sizes = ", ".join(describe(f) for f in p["formats"])
            print(f"  {k:<18} {p['label']:<42} {sizes} cm  [{', '.join(p['fabrics'])}]")
    print("Fabrics")
    for k, f in FABRICS.items():
        print(f"  {k:<18} {f['label']:<42} {f['areal_density'] * 1000:.0f} g/m², {f['thickness'] * 1e3:g} mm")
    return 0


def _cmd_generate(args) -> int:
    var = Variations(**{k: getattr(args, k) for k in VARIATION_HELP})  # fabric: see --fabric
    scene = generate_scene(
        args.preset, args.count, args.seed, var, args.topology, args.vertices, args.fabric, args.format
    )
    out = write_outputs(scene, args.out)
    print(json.dumps(summarize(scene), indent=2, ensure_ascii=False))
    print(f"written to {out}")
    return 0


def _cmd_preview(args) -> int:
    from . import render

    for folder in args.folders:
        print(render.sheet(folder, wireframe=not args.no_wireframe))
    return 0


def _drop_test_args(args) -> list[str]:
    a = [args.target, "--pieces", str(args.pieces), "--frames", str(args.frames), "--seed", str(args.seed)]
    a += ["--samples", str(args.samples), "--wind", str(args.wind), "--quality", str(args.quality)]
    if args.out:
        a += ["--out", args.out]
    if args.render:
        a.append("--render")
    if args.gif:
        a += ["--animate", str(args.gif_step)]
    if not args.self_collision:
        a.append("--no-self-collision")
    return a


def _run_drop_test(args) -> int:
    forwarded = _drop_test_args(args)
    blender = args.blender or shutil.which("blender")
    if not args.blender:
        try:
            import bpy  # noqa: F401
        except ImportError:
            pass
        else:
            from .blender import drop_test

            return drop_test.main(forwarded)
    if blender:
        cmd = [blender, "-b", "--factory-startup", "-P", str(DROP_TEST_SCRIPT), "--", *forwarded]
        return subprocess.call(cmd)
    print(
        "Blender not found: install the bpy module (pip install 'maillage[blender]', Python 3.13), "
        "put `blender` on the PATH, or pass --blender /path/to/blender. Or run it yourself:\n"
        f"  blender -b -P {DROP_TEST_SCRIPT} -- {' '.join(forwarded)}",
        file=sys.stderr,
    )
    return 2


def _cmd_drop_test(args) -> int:
    code = _run_drop_test(args)
    if args.gif and code in (0, 1):
        from .animate import make_gif

        target = Path(args.target)
        out = Path(args.out) if args.out else (target if target.is_dir() else target.parent) / "drop_test"
        print(make_gif(out / "frames", out / "drop_test.gif"))
    return code


def _cmd_blender_script(_args) -> int:
    print(DROP_TEST_SCRIPT)
    return 0


def _cmd_sim_test(args) -> int:
    try:
        import mujoco  # noqa: F401
    except ImportError:
        print('MuJoCo is needed: pip install "maillage[sim]"', file=sys.stderr)
        return 2
    from .sim import mujoco_test

    code = 0
    for target in args.targets:
        report = mujoco_test.run(target, args.out, args.pieces, args.seconds, args.seed)
        print("\n".join(mujoco_test.summary_lines(report)))
        print(f"report: {report['report']}")
        code |= not report["passed"]
    return code


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="maillage",
        description="Realistic textile assets generator for Physical AI, exporting to OpenUSD.",
    )
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list presets and fabrics").set_defaults(func=_cmd_list)

    g = sub.add_parser("generate", help="generate textile pieces and an OpenUSD scene")
    g.add_argument("--preset", default="tea_towel", choices=sorted(PRESETS))
    g.add_argument("--count", type=_positive_int, default=12, help="number of pieces (default: 12)")
    g.add_argument("--seed", type=int, default=1, help="random seed (default: 1)")
    g.add_argument(
        "--topology",
        choices=TOPOLOGIES,
        default="tri",
        help="tri: near-equilateral triangles, any outline (default); grid: quads, rectangles only",
    )
    g.add_argument(
        "--vertices", type=_positive_int, default=1500, help="target vertices per piece (default: 1500)"
    )
    g.add_argument(
        "--format",
        default=None,
        type=_formats,
        help="sizes and shapes in cm instead of the preset's, comma-separated, drawn by weight: "
        "50x70, oval:140x200, round:150; @W sets a weight (default 1), each piece drawing a format "
        "with probability weight / sum of weights: 140x180@2,round:150 gives 2/3 rectangles",
    )
    g.add_argument(
        "--fabric",
        default=None,
        type=_fabrics,
        help="fabric for all pieces, or a comma-separated list used in turn (default: preset's mix)",
    )
    g.add_argument("--out", default="output", help="output root folder (default: output)")
    for name, text in VARIATION_HELP.items():
        g.add_argument(f"--{name}", dest=name, action=argparse.BooleanOptionalAction, default=True, help=text)
    g.set_defaults(func=_cmd_generate)

    p = sub.add_parser("preview", help="flat preview sheet of generated pieces (needs matplotlib)")
    p.add_argument("folders", nargs="+")
    p.add_argument("--no-wireframe", action="store_true", help="hide the mesh edges")
    p.set_defaults(func=_cmd_preview)

    d = sub.add_parser("drop-test", help="simulate pieces in Blender and check the result")
    d.add_argument("target", help="a generated folder (output/<preset>) or a maillage_*.usdc file")
    d.add_argument("--out", default=None, help="output folder (default: <folder>/drop_test)")
    d.add_argument("--pieces", type=_positive_int, default=4, help="pieces tested (default: 4)")
    d.add_argument("--frames", type=_positive_int, default=120, help="frames at 24 fps (default: 120)")
    d.add_argument("--seed", type=int, default=1, help="random drop poses (default: 1)")
    d.add_argument("--render", action="store_true", help="render a Cycles image of the result")
    d.add_argument("--gif", action="store_true", help="also render an animated GIF (drop_test.gif)")
    d.add_argument(
        "--gif-step", type=_positive_int, default=3, help="render every N-th frame for the GIF (default: 3)"
    )
    d.add_argument("--samples", type=_positive_int, default=32, help="Cycles samples (default: 32)")
    d.add_argument("--wind", type=float, default=0.0, help="wind strength on hung pieces (default: 0)")
    d.add_argument(
        "--quality", type=_positive_int, default=10, help="cloth solver steps per frame (default: 10)"
    )
    d.add_argument(
        "--self-collision",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="cloth self-collisions (default: on)",
    )
    d.add_argument("--blender", default=None, help="Blender executable (default: bpy module, then PATH)")
    d.set_defaults(func=_cmd_drop_test)

    sub.add_parser(
        "blender-script", help="print the path of the drop-test script, to run with Blender"
    ).set_defaults(func=_cmd_blender_script)

    s = sub.add_parser("sim-test", help="drape test in MuJoCo, read back from the OpenUSD file (needs [sim])")
    s.add_argument("targets", nargs="+", help="generated folders (output/<preset>) or maillage_*.usdc files")
    s.add_argument("--out", default=None, help="report folder (default: <folder>/sim_test)")
    s.add_argument("--pieces", type=_positive_int, default=4, help="pieces tested (default: 4)")
    s.add_argument("--seconds", type=float, default=5.0, help="simulated time in s (default: 5)")
    s.add_argument("--seed", type=int, default=1, help="random drop poses (default: 1)")
    s.set_defaults(func=_cmd_sim_test)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
