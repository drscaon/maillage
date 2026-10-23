"""Animated GIF from the frames rendered by the drape test (needs Pillow,
installed with matplotlib: pip install "maillage[render]")."""

from __future__ import annotations

from pathlib import Path


def make_gif(
    frames_dir: str | Path, output: str | Path, fps: float = 12.0, width: int = 640, hold: float = 1.5
):
    """Assemble frames_dir/frame_*.png into a looping GIF; the last frame is held
    `hold` seconds so the final drape can be seen."""
    from PIL import Image

    files = sorted(Path(frames_dir).glob("frame_*.png"))
    if not files:
        raise FileNotFoundError(f"no frame_*.png in {frames_dir}")
    frames = []
    for f in files:
        im = Image.open(f).convert("RGB")
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        frames.append(im.quantize(colors=200, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
    durations = [round(1000 / fps)] * len(frames)
    durations[-1] = round(1000 * hold)
    output = Path(output)
    frames[0].save(output, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
    return output
