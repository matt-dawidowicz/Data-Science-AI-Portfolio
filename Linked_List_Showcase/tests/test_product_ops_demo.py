"""Smoke tests for the portfolio product-operations demo script."""

import subprocess
import sys
import unittest
from pathlib import Path


class TestProductOpsDemo(unittest.TestCase):
    """Verify the multi-structure demo remains runnable and deterministic."""

    def test_product_ops_demo_runs_from_package_root(self) -> None:
        """The reviewer demo should run as a standalone example."""
        package_root = Path(__file__).resolve().parents[1]
        demo_path = package_root / "examples" / "product_ops_demo.py"

        result = subprocess.run(
            [sys.executable, str(demo_path)],
            cwd=package_root,
            capture_output=True,
            check=True,
            text=True,
        )

        output = result.stdout
        self.assertIn("Product ops snapshot", output)
        self.assertIn(
            "first tasks: rollback failed deploy, sync billing report",
            output,
        )
        self.assertIn("next escalation: INC-101 in 10 minutes", output)
        self.assertIn("next after 20 minutes: INC-104", output)
        self.assertIn("service impact scores:", output)
        self.assertIn("event blocks:", output)
