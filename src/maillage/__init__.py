"""Maillage: realistic textile assets generator for Physical AI, exporting to OpenUSD."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("maillage")
except PackageNotFoundError:  # running from a source tree without installation
    __version__ = "0.0.0+unknown"

from .fabrics import FABRICS  # noqa: E402
from .generator import Piece, Scene, Variations, generate_scene, write_outputs  # noqa: E402
from .presets import CATEGORIES, PRESETS  # noqa: E402

__all__ = [
    "CATEGORIES",
    "FABRICS",
    "PRESETS",
    "Piece",
    "Scene",
    "Variations",
    "__version__",
    "generate_scene",
    "write_outputs",
]
