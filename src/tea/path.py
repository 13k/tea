"""
path module
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Union

PathLike = Union[str, os.PathLike[str]]


def expand_path(path: PathLike) -> Path:
    """Returns a Path with expanded environment variables and username in given path"""
    return Path(os.path.expandvars(path)).expanduser()
