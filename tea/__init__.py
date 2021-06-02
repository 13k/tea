"""
tea is a thin tmuxp wrapper.
"""

from __future__ import annotations

import argparse
import copy
import os
import sys
from pathlib import Path
from typing import Any, Final, NamedTuple, NoReturn, Union

import yaml
from tmuxp import cli as tmuxp_cli

PathLike = Union[str, os.PathLike[str]]

__version__: Final[str] = "0.3.0"

YAML_EXT: Final[str] = "yml"
TMUX_DEFAULT_BIN: Final[Path] = Path("tmux")
TMUXP_CONFIG_TEMPLATE: Final[dict] = {
    "session_name": "session_name",
    "start_directory": "$HOME",
    "windows": [
        {
            "window_name": "window_name",
            "focus": True,
            "layout": "main-vertical",
            "options": {},
            "panes": [{"focus": True}, "blank", "blank"],
        }
    ],
}


class Options(NamedTuple):
    """Command-line options"""

    tmux: Path
    kill: bool
    generate: bool
    list: bool
    active: bool
    print_dir: bool
    print_dir_exp: bool
    directory: Path
    force: bool
    version: bool
    name: str


def _patharg(must_exist=False, expand=False, return_raw=False):
    def validate_patharg(arg):
        raw = Path(arg)

        if expand:
            path = Path(os.path.expandvars(arg)).expanduser()
        else:
            path = raw

        if must_exist and not path.exists():
            msg = f"Path {path} doesn't exist"
            raise argparse.ArgumentTypeError(msg)

        return raw if return_raw else path

    return validate_patharg


def _err(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


def main():
    """CLI entry-point"""
    parser = argparse.ArgumentParser(description="Control tmux (with tmuxp)")

    parser.add_argument(
        "-t",
        "--tmux",
        type=_patharg,
        default=TMUX_DEFAULT_BIN,
        help="tmux executable path (default: %(default)s)",
    )

    parser.add_argument(
        "-K",
        "--kill",
        action="store_true",
        default=False,
        help="Kill the tmux server",
    )

    parser.add_argument(
        "-g",
        "--generate",
        action="store_true",
        default=False,
        help="Generate a tmuxp session configuration for a project",
    )

    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        default=False,
        help="List available configurations",
    )

    parser.add_argument(
        "-a",
        "--active",
        action="store_true",
        default=False,
        help="List active sessions",
    )

    parser.add_argument(
        "-D",
        "--print-dir",
        action="store_true",
        default=False,
        help="Print the starting directory of a project",
    )

    parser.add_argument(
        "-E",
        "--print-dir-exp",
        action="store_true",
        default=False,
        help="Expand environment variables when printing project directory",
    )

    parser.add_argument(
        "-d",
        "--directory",
        type=_patharg(must_exist=True, expand=True, return_raw=True),
        default=Path.cwd(),
        help="Project directory (default: %(default)s)",
    )

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        default=False,
        help="Force execution (overwrite files, etc. default: %(default)s)",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        default=False,
        help="Show version",
    )

    parser.add_argument(
        "name",
        metavar="NAME",
        nargs="?",
        help="Act on project/session NAME",
    )

    options: Options = parser.parse_args()

    if options.version:
        return cmd_version(options)

    if options.kill:
        return cmd_kill_server(options)

    if options.list:
        return cmd_list_configs(options)

    if options.active:
        return cmd_list_active(options)

    if options.name is None:
        parser.error("NAME is required")

    if options.print_dir:
        return cmd_print_dir(options)

    if options.generate:
        return cmd_generate_config(options)

    return cmd_load_session(options)


def _tmuxp_config_dir() -> Path:
    return Path(tmuxp_cli.get_config_dir())


def _tmuxp_config_name(name: str) -> str:
    return f"{name}.{YAML_EXT}"


def _tmuxp_config_file(name: str) -> Path:
    return _tmuxp_config_dir() / _tmuxp_config_name(name)


def _parse_config(name: str) -> Any:
    with _tmuxp_config_file(name).open("r") as cfg_file:
        return yaml.load(cfg_file)


def _tmux(cmd: PathLike, *args: PathLike) -> NoReturn:
    os.execlp(cmd, "tmux", *args)


def cmd_version(_options: Options) -> int:
    """Prints tea version"""
    print(__version__)
    return 0


def cmd_kill_server(options: Options) -> NoReturn:
    """Kills tmux server"""
    _tmux(options.tmux, "kill-server")


def cmd_list_configs(_options: Options) -> int:
    """Lists available tmuxp configs"""

    config_dir = _tmuxp_config_dir()

    for path in sorted(config_dir.glob(f"*.{YAML_EXT}")):
        print(path.name[: path.name.rfind(path.suffix)])

    return 0


def cmd_list_active(options: Options) -> NoReturn:
    """Lists active tmux sessions"""
    _tmux(options.tmux, "ls")


def _start_directory(config: Any) -> Path | None:
    if "start_directory" in config:
        return Path(config["start_directory"])

    if "windows" in config:
        for window in config["windows"]:
            if "start_directory" in window:
                return Path(window["start_directory"])

    return None


def cmd_print_dir(options: Options) -> int:
    """Prints the starting directory of a tmuxp config (if defined)"""

    try:
        config = _parse_config(options.name)
        start_dir = _start_directory(config)

        if start_dir is None:
            _err(f"{options.name}: start directory not configured")
        else:
            if options.print_dir_exp:
                print(Path(os.path.expandvars(start_dir)).expanduser())
            else:
                print(start_dir)
    except FileNotFoundError:
        _err(f"{options.name}: session configuration not found")
        return 1

    return 0


def cmd_generate_config(options: Options) -> int:
    """Generates a tmuxp session config"""

    output_path = _tmuxp_config_file(options.name)

    if output_path.exists() and not options.force:
        print(f"{options.name}: session configuration ({output_path}) already exists")
        return 1

    config = copy.deepcopy(TMUXP_CONFIG_TEMPLATE)

    config.update(
        session_name=options.name,
        start_directory=str(options.directory),
    )

    config["windows"][0].update(
        window_name=options.name,
    )

    with output_path.open("w") as cfg_file:
        yaml.dump(config, cfg_file, default_flow_style=False)

    print(f"{options.name}: session configuration saved in {output_path}")

    return 0


def cmd_load_session(options: Options) -> int:
    """Loads a tmuxp session"""

    config_file = _tmuxp_config_file(options.name)

    tmuxp_cli.load_workspace(config_file=config_file, answer_yes=True)

    return 0
