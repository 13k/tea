"""
cli module
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple, NoReturn, TypeVar

from . import __version__
from .path import PathLike, expand_path
from .tmux import TMUX_DEFAULT_BIN
from .tmux import run as tmux
from .tmuxp import config_create as tmuxp_config_create
from .tmuxp import config_list as tmuxp_config_list
from .tmuxp import config_start_dir as tmuxp_config_start_dir
from .tmuxp import load as tmuxp_load

OptionTypeRt = TypeVar("OptionTypeRt")
OptionType = Callable[[str], OptionTypeRt]


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


def _err(*args: Any, **kwargs: Any) -> None:
    print(*args, **kwargs, file=sys.stderr)


def _patharg(
    must_exist: bool = False,
    expand: bool = False,
    return_raw: bool = False,
) -> OptionType[PathLike]:
    def validate_patharg(arg: str) -> PathLike:
        raw = Path(arg)
        path = expand_path(arg) if expand else raw

        if must_exist and not path.exists():
            msg = f"Path {path} doesn't exist"
            raise argparse.ArgumentTypeError(msg)

        return raw if return_raw else path

    return validate_patharg


def main() -> int:  # pylint: disable=too-many-return-statements
    """CLI entry-point"""
    parser = argparse.ArgumentParser(description="Control tmux (with tmuxp)")

    parser.add_argument(
        "-t",
        "--tmux",
        type=_patharg(expand=True),
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

    args = parser.parse_args()

    if args.name is None:
        parser.error("NAME is required")

    options: Options = Options(
        tmux=args.tmux,
        kill=args.kill,
        generate=args.generate,
        list=args.list,
        active=args.active,
        print_dir=args.print_dir,
        print_dir_exp=args.print_dir_exp,
        directory=args.directory,
        force=args.force,
        version=args.version,
        name=args.name,
    )

    if options.version:
        return _cmd_version(options)

    if options.kill:
        return _cmd_kill_server(options)

    if options.list:
        return _cmd_list_configs(options)

    if options.active:
        return _cmd_list_active(options)

    if options.print_dir or options.print_dir_exp:
        return _cmd_print_dir(options)

    if options.generate:
        return _cmd_generate_config(options)

    return _cmd_load_session(options)


def _cmd_version(_: Options) -> int:
    print(__version__)
    return 0


def _cmd_kill_server(options: Options) -> NoReturn:
    tmux("kill-server", cmd=options.tmux)


def _cmd_list_configs(_: Options) -> int:
    for path in tmuxp_config_list():
        print(path.name[: path.name.rfind(path.suffix)])

    return 0


def _cmd_list_active(options: Options) -> NoReturn:
    tmux("ls", cmd=options.tmux)


def _cmd_print_dir(options: Options) -> int:
    try:
        start_dir = tmuxp_config_start_dir(options.name, expand=options.print_dir_exp)

        if start_dir is None:
            _err(f"{options.name}: start directory not configured")
        else:
            print(start_dir)
    except FileNotFoundError:
        _err(f"{options.name}: session configuration not found")
        return 1

    return 0


def _cmd_generate_config(options: Options) -> int:
    try:
        config_path = tmuxp_config_create(
            name=options.name,
            start_dir=options.directory,
            force=options.force,
        )

        print(f"{options.name}: session configuration saved in {config_path}")

        return 0
    except FileExistsError:
        print(f"{options.name}: session configuration already exists")

        return 1


def _cmd_load_session(options: Options) -> int:
    try:
        tmuxp_load(options.name)
    except RuntimeError as err:
        _err(f"Error loading session: {err}")
        return 1

    return 0
