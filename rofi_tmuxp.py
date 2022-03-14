"""Rofi script to launch tmuxp sessions"""
import logging
import subprocess
import sys
from pathlib import Path

import tmuxp
from kaptan import Kaptan


logger = logging.getLogger("rofi_tmuxp")


class ValidationError(Exception):
    pass


def main():
    """Main script entrypoint.

    If no command line arguments are provided, print out a list of available
    sessions. Otherwise, run tmuxp in a new terminal with the session provided
    on the command line.
    """
    _setup_logging()

    if len(sys.argv) == 1:
        for session in sorted(get_sessions()):
            print(session)
    else:
        session_name = sys.argv[1]
        start_session(session_name)


def get_sessions():
    """Get tmuxp sessions.

    Returns a dictionary mapping session name to config file paths.
    """
    config_dir = Path(tmuxp.cli.get_config_dir())

    for filename in tmuxp.config.in_dir(str(config_dir)):
        config_path = config_dir / filename
        try:
            config = _load_config(config_path)
        except ValidationError as e:
            logger.warning("Invalid config '%s': %s", config_path, e)
        except Exception as e:
            logger.warning("Error loading config '%s': %r", config_path, e)
        else:
            yield config["session_name"]


def _load_config(cfg_path):
    """Load config from a given config file.

    Raises `ValidationError` if the config does not define a session name"""
    config = Kaptan()
    config.import_config(str(cfg_path))
    config = tmuxp.cli.config.expand(config.configuration_data)

    if "session_name" not in config:
        raise ValidationError("No session name configured")

    return config


def start_session(session_name):
    """Lanuch tmuxp in a new terminal window."""
    subprocess.Popen(
        ["rofi-sensible-terminal", "-e", "tmuxp", "load", session_name],
        stdout=subprocess.DEVNULL,
    )


def _setup_logging():
    logging.basicConfig(
        style="{",
        level=logging.WARNING,
        format="{asctime} - {name} - {levelname} - {message}",
    )


if __name__ == "__main__":  # pragma: no cover
    main()
