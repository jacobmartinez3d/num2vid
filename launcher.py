"""This script simulates launching num2vid in a controlled production environment.

Before running num2vid Flask server or Client it is expected that:
    - the num2vid module is available in PYTHONPATH
    - environment variable NUM2VID_CONFIG is set as a valid path to a json config (see README)

This scripts automates the above tasks then launches the given python target.

Default logging directory: ./logging_output
Default client ui: ./num2vid_client/ui.py
"""
import argparse
import os
import platform
import subprocess
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class Num2VidLauncherError(Exception):
    """Base Exception class."""
    def __init__(self, msg: str, *args: ..., **kwargs: ...):
        """Initialize with message str.

        :param msg: message describing exception from raiser.
        """
        super(Num2VidLauncherError, self).__init__(*args, **kwargs)
        self.msg = msg

    def __repr__(self):
        return "<{error}: {msg}>".format(error=self.__class__.__name__, msg=self.msg)


class InvalidConfigPathError(Num2VidLauncherError):
    """NUM2VID_CONFIG env variable not set or is invalid."""


class InvalidLoggingOutputDirError(Num2VidLauncherError):
    """NUM2VID_LOGGING_OUTPUT_DIR env variable not set or is invalid."""


class InvalidPython3AliasError(Num2VidLauncherError):
    """Argument given for python3 alias was invalid or not given."""

def main(target: int):
    """Launch client and server apps with pythonpath injection and environment variables.

    :param target: int representing server/client (0: server, 1: client).
    """
    os.environ["NUM2VID_CONFIG"] = os.path.join(
        CURRENT_DIR, "num2vid", "config", "num2vid_config.json")
    # validate file exists
    if not os.path.isfile(os.environ["NUM2VID_CONFIG"]):
        raise InvalidConfigPathError(
            "The 'NUM2VID_CONFIG' env variable: {0} doesn't exist or is not a file.")

    from num2vid import Config
    config = Config(os.environ["NUM2VID_CONFIG"])

    # create temporary logging and vid output dirs if needed
    if not os.path.isdir(config.get("logging_output_dir")):
        os.mkdir(config.get("logging_output_dir"))
    if not os.path.isdir(config.get("vid_output_dir")):
        os.mkdir(config.get("vid_output_dir"))

    env = os.environ.copy()
    launch_target(target, config, env)

def launch_target(target: int, config: "num2vid.Config", env: dict):
    """Launch target with current directory appended to PYTHONPATH.

    :param target: int representing server/client (0: server, 1: client).
    :param env: dictionary containing environment variables to inject.
    :param config: Config instance.
    """
    # inject num2vid repo dir to PYTHONPATH
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = os.pathsep.join(
            [
                env["PYTHONPATH"],
                CURRENT_DIR
            ]
        )
    else:
        env["PYTHONPATH"] = CURRENT_DIR

    python_path = config.get("python_{system}".format(system=platform.system().lower()))

    if target == 0:
        # start server
        subprocess.run([python_path, "app.py"], shell=False)
        return

    if target == 1:
        # start ffmpeg
        client_ui = os.path.join(CURRENT_DIR, "num2vid_client", "ui.py")
        cmd_list = [python_path, client_ui]
        subprocess.run(cmd_list, shell=False, env=env)
    elif target == 2:
        # start python shell
        subprocess.run([python_path], shell=False, env=env)
    elif target == 3:
        # start nuke interactive instance
        subprocess.run([config.get("nuke_{system}".format(
            system=platform.system().lower()))], shell=False, env=env)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    grp = parser.add_mutually_exclusive_group()  # this ensures only one arg can be used at a time
    grp.add_argument(
        "-s",
        "--server",
        action="store_true",
        help="Launch Flask server(./app.py).")
    grp.add_argument(
        "-c",
        "--client",
        action="store_true",
        help="Launch Client UI(./num2vid_client/ui.py).")
    grp.add_argument(
        "-p",
        "--python",
        action="store_true",
        help="Launch a Python 3 shell for importing and using num2vid module interactively.")
    grp.add_argument(
        "-n",
        "--nuke",
        action="store_true",
        help="Launch a Nuke interactive instance for importing and using num2vid module.")
    args = parser.parse_args()
    
    # generate int representing target
    target_choice = (args.server, args.client, args.python, args.nuke).index(True)  
    main(target_choice)
