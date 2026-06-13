"""Test bootstrap for source-checkout unittest discovery.

The package uses a ``src`` layout. Pytest reads ``pythonpath`` from
``pyproject.toml``, and installed-package test runs work normally. Plain
``unittest discover`` needs this package initializer so tests can import
``linked_list`` before an editable install has happened.
"""

from __future__ import annotations

import sys
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"
SOURCE_ROOT_TEXT = str(SOURCE_ROOT)

if SOURCE_ROOT_TEXT not in sys.path:
    sys.path.insert(0, SOURCE_ROOT_TEXT)
