"""
tmuxp integration
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Final

import yaml
from tmuxp import cli as tmuxp_cli

from .config import Config
from .path import PathLike, expand_path

CONFIG_EXT: Final = "yml"

CONFIG_TEMPLATE: Final = """
__base_window__: &base_window
  layout: main-vertical
  panes:
    - focus: true
    - blank
    - blank

session_name: "{session_name!s}"
start_directory: "{start_directory!s}"
windows:
  - window_name: "{window_name!s}"
    focus: true
    <<: *base_window
  - window_name: "{window_name!s}"
    <<: *base_window
"""


def config_dir() -> Path:
    """Returns path to tmuxp's configuration directory"""

    return Path(tmuxp_cli.get_config_dir())


def config_name(name: str) -> str:
    """Returns base filename for a tmuxp configuration with given session name"""

    return f"{name}.{CONFIG_EXT}"


def config_file(name: str) -> Path:
    """Returns path to tmuxp session configuration file with given session name"""

    return config_dir() / config_name(name)


def parse_config(name: str) -> Config:
    """Parses the configuration for the given session name"""

    with config_file(name).open("r") as cfg_file:
        return yaml.safe_load(cfg_file)  # type: ignore


def config_list() -> list[Path]:
    """Returns a list of available tmuxp session configuration paths"""

    return sorted(config_dir().glob(f"*.{CONFIG_EXT}"))


def _start_directory(config: Config) -> str | None:
    if "start_directory" in config:
        return config["start_directory"]

    if "windows" in config:
        for window in config["windows"]:
            if "start_directory" in window:
                return window["start_directory"]

    return None


def config_start_dir(name: str, expand: bool = False) -> str | None:
    """Returns the starting directory of a tmuxp session configuration (if defined)"""

    config = parse_config(name)
    start_dir = _start_directory(config)

    if start_dir is None:
        return None

    if expand:
        return str(expand_path(start_dir))

    return start_dir


def config_create(name: str, start_dir: PathLike, force: bool = False) -> Path | None:
    """Writes a tmuxp session configuration and returns its path"""

    content = CONFIG_TEMPLATE.format(
        session_name=name,
        start_directory=start_dir,
        window_name=name,
    )

    output_path = config_file(name)
    mode = "x"

    if force:
        mode = "w"

    with output_path.open(mode) as file:
        file.write(content)

    return output_path


def load(name: str) -> None:
    """Loads a tmuxp session"""

    config_path = config_file(name)

    tmuxp_cli.load_workspace(config_file=config_path, answer_yes=True)
