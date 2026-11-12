"""Fixtures shared by the tests."""

import pytest

from maillage import generate_scene, write_outputs
from maillage.contract import usd_files


@pytest.fixture(scope="session")
def contract_files(tmp_path_factory):
    """OpenUSD files freshly generated: the main file and its OmniPhysics layer."""
    out = tmp_path_factory.mktemp("contract")
    folder = write_outputs(generate_scene("tea_towel", count=2, vertices=300), out)
    return usd_files([folder])


@pytest.fixture(scope="session")
def pack_folder(tmp_path_factory):
    """A pack freshly generated."""
    return write_outputs(generate_scene("bath_towel", count=3, vertices=300), tmp_path_factory.mktemp("pack"))
