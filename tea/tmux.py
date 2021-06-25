"""
tmux integration
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final, NoReturn

from .path import PathLike

TMUX_DEFAULT_BIN: Final[Path] = Path("tmux")


def run(*args: PathLike, cmd: PathLike = TMUX_DEFAULT_BIN) -> NoReturn:
    """Runs tmux command, replacing the current process"""
    os.execlp(cmd, "tmux", *args)
