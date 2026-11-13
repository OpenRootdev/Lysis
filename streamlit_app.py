import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
runpy.run_path(str(ROOT / "src" / "lysis" / "app.py"), run_name="__main__")