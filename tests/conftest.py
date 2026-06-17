"""Test package bootstrap without importing Home Assistant."""

from pathlib import Path
import sys
import types

PACKAGE = "mg_ismart_india"
PACKAGE_PATH = Path(__file__).parents[1] / "custom_components" / PACKAGE

module = types.ModuleType(PACKAGE)
module.__path__ = [str(PACKAGE_PATH)]
sys.modules[PACKAGE] = module
