"""Public demonstration entry point. Never opens inventory.db."""
import os
import runpy
from pathlib import Path


os.environ["RAREMOTION_DEMO"] = "1"
runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")
