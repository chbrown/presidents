from pathlib import Path
import os

# `ROOT_DIR` is the directory containing the "presidents" package
# (i.e., the git repo root)
ROOT_DIR = Path(os.path.dirname(__file__) or os.curdir).parent
DATA_DIR = ROOT_DIR / "data"
