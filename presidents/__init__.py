import os
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('presidents')

# `here` is the directory containing this file
here = os.path.dirname(__file__) or os.curdir
# `root` is the directory containing the "presidents" package
# (i.e., the git repo root)
root = os.path.dirname(here)


