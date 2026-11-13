"""Prove that a piece behaves like cloth: drop it on a pedestal and let it drape.

The drape test builds a MuJoCo model from the OpenUSD file (mesh, mass and
stiffness of the fabric are read from it), drops each piece on a round
pedestal smaller than itself and checks that it hangs like cloth: it does not
stretch, it does not pass through the pedestal and it comes to rest. The
drape coefficient is reported too: the share of the piece's area that still
shows from above (lower for a soft fabric, higher for a stiff one). It is the
test that runs in Maillage's continuous integration.

Needs MuJoCo:  pip install "maillage[sim]"
Takes about 10 seconds.

    python examples/04_drape_test_in_mujoco.py
"""

import sys

from maillage import generate_scene, write_outputs
from maillage.sim import mujoco_test

out = sys.argv[1] if len(sys.argv) > 1 else "output/examples"
folder = write_outputs(generate_scene("washcloth", count=2, vertices=200, seed=1), out)

# One piece, two simulated seconds; the report also goes to <folder>/sim_test/.
report = mujoco_test.run(folder, pieces=1, seconds=2.0)
print("\n".join(mujoco_test.summary_lines(report)))

# Each criterion is a threshold; the report holds the numbers behind them.
print("criteria:", report["criteria"])

sys.exit(0 if report["passed"] else 1)
