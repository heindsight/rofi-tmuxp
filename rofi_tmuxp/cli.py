"""Functions to drive the commandline interface"""
import argparse
import logging

from . import rofi_client, sessions


logger = logging.getLogger(__name__)


def main():
    """Main script entrypoint.

    If no command line arguments are provided, print out a list of available
    sessions. Otherwise, run tmuxp in a new terminal with the session provided
    on the command line.
    """
    args = _parse_args()
    _setup_logging(args.quiet)

    session_info = sessions.get_sessions()

    if args.session:
        try:
            config_path = session_info[args.session]
        except KeyError:
            msg = "No such session: {}".format(args.session)
            logger.warning(msg)
            rofi_client.error(msg)
        else:
            rofi_client.start_session(config_path)
    else:
        for session_name in sorted(session_info):
            print(session_name)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("session", help="Name of the session to load", nargs="?")
    parser.add_argument("--quiet", help="Reduce log verbosity", action="store_true")
    args, _ = parser.parse_known_args()
    return args


def _setup_logging(quiet: bool):
    logging.basicConfig(
        style="{",
        level=logging.ERROR if quiet else logging.INFO,
        format="{asctime} - {name} - {levelname} - {message}",
    )
