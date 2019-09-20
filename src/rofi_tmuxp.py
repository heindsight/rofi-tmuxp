"""Rofi script to launch tmuxp sessions"""
import logging
import subprocess
import sys
from pathlib import Path

import tmuxp
from kaptan import Kaptan


__version__ = "0.0.1"


logger = logging.getLogger("rofi_tmuxp")


def main():
    """Main script entrypoint.

    If no command line arguments are provided, print out a list of available
    sessions. Otherwise, run tmuxp in a new terminal with the session provided
    on the command line.
    """
    sessions = get_sessions()

    if len(sys.argv) == 1:
        for session in sorted(sessions):
            print(session)
    else:
        try:
            session = sessions[sys.argv[1]]
        except KeyError:
            msg = f"No such session: {sys.argv[1]}"
            logger.warning(msg)
            rofi_error(msg)
            return

        start_session(session)


def get_sessions():
    """Get tmuxp sessions.

    Returns a dictionary mapping session name to config file paths.
    """
    config_dir = Path(tmuxp.cli.get_config_dir())
    sessions = {}

    for filename in tmuxp.config.in_dir(config_dir):
        config_path = config_dir / filename
        try:
            sessions[_get_session_name(config_path)] = config_path
        except KeyError:
            logger.warning("No session name configured in '%s'", config_path)
        except Exception as e:
            logger.warning("Error loading config '%s': %r", config_path, e)

    return sessions


def _get_session_name(cfg_path):
    """Extract the session name from a tmuxp config file"""
    config = Kaptan()
    config.import_config(str(cfg_path))

    return config.get("session_name")


def start_session(config_name):
    """Lanuch tmuxp in a new terminal window."""
    subprocess.Popen(
        ["rofi-sensible-terminal", "-e", "tmuxp", "load", config_name],
        stdout=subprocess.DEVNULL,
    )


def rofi_error(message):
    """Display an error message using the rofi error dialog"""
    subprocess.Popen(["rofi", "-e", message], stdout=subprocess.DEVNULL)


if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(
        style="{",
        level=logging.WARNING,
        fmt="{asctime} - {name} - {levelname} - {message}",
    )
    main()
