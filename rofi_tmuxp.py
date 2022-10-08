"""Rofi script to launch tmuxp sessions"""
import logging
import subprocess
import sys
from pathlib import Path

import tmuxp


try:
    # ConfigReader is only available in tmuxp >= 1.16.0
    from tmuxp.config_reader import ConfigReader

    have_config_reader = True  # pragma: no cover
except ImportError:  # pragma: no cover
    import yaml

    have_config_reader = False

try:
    # get_config_dir moved to `tmuxp.cli.utils` in tmuxp 1.11.0
    from tmuxp.cli.utils import get_config_dir
except ImportError:  # pragma: no cover
    from tmuxp.cli import get_config_dir


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
    sessions = get_sessions()

    if len(sys.argv) == 1:
        for session in sorted(sessions):
            print(session)
    else:
        try:
            session = sessions[sys.argv[1]]
        except KeyError:
            msg = "No such session: {}".format(sys.argv[1])
            logger.warning(msg)
            rofi_error(msg)
            return

        start_session(session)


def get_sessions():
    """Get tmuxp sessions.

    Returns a dictionary mapping session name to config file paths.
    """
    config_dir = Path(get_config_dir())
    sessions = {}

    for filename in tmuxp.config.in_dir(str(config_dir)):
        config_path = config_dir / filename
        try:
            config = _load_config(config_path)
        except ValidationError as e:
            logger.warning("Invalid config '%s': %s", config_path, e)
        except Exception as e:
            logger.warning("Error loading config '%s': %r", config_path, e)
        else:
            sessions[config["session_name"]] = config_path

    return sessions


def _load_config(cfg_path):
    """Load config from a given config file.

    Raises `ValidationError` if the config does not define a session name"""
    if have_config_reader:  # pragma: no cover
        cfg_reader = ConfigReader.from_file(cfg_path)
        config = cfg_reader.content
    else:  # pragma: no cover
        config = yaml.safe_load(cfg_path.read_text())

    tmuxp.config.expand(config)

    if "session_name" not in config:
        raise ValidationError("No session name configured")

    return config


def start_session(config_path):
    """Lanuch tmuxp in a new terminal window."""
    subprocess.Popen(
        ["rofi-sensible-terminal", "-e", "tmuxp", "load", str(config_path)],
        stdout=subprocess.DEVNULL,
    )


def rofi_error(message):
    """Display an error message using the rofi error dialog"""
    subprocess.Popen(["rofi", "-e", message], stdout=subprocess.DEVNULL)


def _setup_logging():
    logging.basicConfig(
        style="{",
        level=logging.WARNING,
        format="{asctime} - {name} - {levelname} - {message}",
    )


if __name__ == "__main__":  # pragma: no cover
    main()
