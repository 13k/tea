"""
config module
"""

from __future__ import annotations

from typing import Literal, TypedDict

type TmuxLayout = (
    Literal["even-horizontal"]
    | Literal["even-vertical"]
    | Literal["main-horizontal"]
    | Literal["main-vertical"]
    | Literal["tiled"]
)


class Config(TypedDict, total=False):
    """Session configuration"""

    session_name: str
    global_options: dict[str, str]
    options: dict[str, str]
    environment: dict[str, str]
    start_directory: str
    before_script: str
    shell_command_before: str | list[str]
    shell_command: str | list[str]
    supress_history: bool
    windows: list[WindowConfig]


class WindowConfig(TypedDict, total=False):
    """Window configuration"""

    window_name: str
    window_index: int
    options: dict[str, str]
    options_after: dict[str, str]
    start_directory: str
    shell_command_before: str | list[str]
    supress_history: bool
    focus: bool
    layout: TmuxLayout
    panes: list[PaneConfig | Literal["blank"] | Literal["pane"] | Literal["null"] | str]


class PaneConfig(TypedDict, total=False):
    """Pane configuration"""

    start_directory: str
    shell_command: str | list[str]
    supress_history: bool
    focus: bool
