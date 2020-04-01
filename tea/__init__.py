"""
tea is a thin tmuxp wrapper.
"""

import argparse
import copy
import os
import sys
from pathlib import Path

import yaml

YAML_EXT = "yml"

TMUX_DEFAULT_BIN = Path("tmux")

TMUXP_DEFAULT_BIN = Path("tmuxp")
TMUXP_DEFAULT_CONFIG_DIR = Path.home().joinpath(".tmuxp")
TMUXP_CONFIG_DIR_ENV_VAR = "TMUXP_CONFIG_DIR"

TMUXP_CONFIG_TEMPLATE = {
    "session_name": "session_name",
    "windows": [
        {
            "window_name": "window_name",
            "start_directory": "$HOME",
            "focus": True,
            "layout": "main-vertical",
            "options": {},
            "panes": [{"focus": True}, "blank", "blank"],
        }
    ],
}


def _tmuxp_config_dir():
    config_dir = os.getenv(TMUXP_CONFIG_DIR_ENV_VAR, "")

    if config_dir == "":
        config_dir = TMUXP_DEFAULT_CONFIG_DIR

    return Path(config_dir)


def patharg(must_exist=False, expand=False, return_raw=False):
    """ Creates a Path argument parser """

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


def err(*args, **kwargs):
    """ Prints a message to stderr """
    print(*args, **kwargs, file=sys.stderr)


def main():
    """ CLI entry-point """
    parser = argparse.ArgumentParser(description="""Control tmux (with tmuxp)""")

    parser.add_argument(
        "-t",
        "--tmux",
        type=patharg,
        default=TMUX_DEFAULT_BIN,
        help="""tmux executable path (default: %(default)s)""",
    )

    parser.add_argument(
        "-T",
        "--tmuxp",
        type=patharg,
        default=TMUXP_DEFAULT_BIN,
        help="""tmuxp executable path (default: %(default)s)""",
    )

    parser.add_argument(
        "-c",
        "--config-dir",
        type=patharg(must_exist=True),
        default=_tmuxp_config_dir(),
        help="""tmuxp config path (default: %(default)s)""",
    )

    parser.add_argument(
        "-K",
        "--kill",
        action="store_true",
        default=False,
        help="""Kill the tmux server""",
    )

    parser.add_argument(
        "-g",
        "--generate",
        action="store_true",
        default=False,
        help="""Generate a tmuxp session configuration for a project""",
    )

    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        default=False,
        help="""List available configurations""",
    )

    parser.add_argument(
        "-a",
        "--active",
        action="store_true",
        default=False,
        help="""List active sessions""",
    )

    parser.add_argument(
        "-D",
        "--print-dir",
        action="store_true",
        default=False,
        help="""Print the starting directory of a project""",
    )

    parser.add_argument(
        "-d",
        "--directory",
        type=patharg(must_exist=True, expand=True, return_raw=True),
        default=Path.cwd(),
        help="""Project directory (default: %(default)s)""",
    )

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        default=False,
        help="""Force execution (overwrite files, etc. default: %(default)s)""",
    )

    parser.add_argument(
        "name", metavar="NAME", nargs="?", help="""Act on project/session NAME"""
    )

    options = parser.parse_args()

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


def tmux(cmd, *args, **kwargs):
    """ Runs tmux command """
    os.execlp(cmd, "tmux", *args, **kwargs)


def tmuxp(cmd, *args, **kwargs):
    """ Runs tmuxp command """
    os.execlp(cmd, "tmuxp", *args, **kwargs)


def _parse_config(name, config_dir):
    with config_dir.joinpath(f"{name}.{YAML_EXT}").open("r") as cfg_file:
        return yaml.load(cfg_file)


def cmd_kill_server(options):
    """ Kills tmux server """
    return tmux(options.tmux, "kill-server")


def cmd_list_configs(options):
    """ Lists available tmuxp configs """
    for path in sorted(options.config_dir.glob(f"*.{YAML_EXT}")):
        print(path.name[: path.name.rfind(path.suffix)])

    return 0


def cmd_list_active(options):
    """ Lists active tmux sessions """
    return tmux(options.tmux, "ls")


def cmd_print_dir(options):
    """ Prints the starting directory of a tmuxp config (if defined) """
    try:
        config = _parse_config(options.name, options.config_dir)
        print(config["windows"][0]["start_directory"])
    except FileNotFoundError:
        err(f"Session configuration {options.name} does not exist")
        return 1

    return 0


def cmd_generate_config(options):
    """ Generates a tmuxp session config """
    output_name = f"{options.name}.{YAML_EXT}"
    output_path = options.config_dir.joinpath(output_name)

    if output_path.exists() and not options.force:
        print(f"Session configuration {options.name} [{output_path}] already exists")
        return 1

    config = copy.deepcopy(TMUXP_CONFIG_TEMPLATE)
    config["session_name"] = options.name
    config["windows"][0].update(
        window_name=options.name, start_directory=str(options.directory)
    )

    with output_path.open("w") as cfg_file:
        yaml.dump(config, cfg_file, default_flow_style=False)

    print(f"Saved session configuration to {output_path}")

    return 0


def cmd_load_session(options):
    """ Loads a tmuxp session """
    return tmuxp(options.tmuxp, "load", "-y", options.name)
