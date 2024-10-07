"""Run 'rofi' commands to display messages or launch sessions."""

import subprocess
from pathlib import Path


def start_session(config_path: Path) -> None:
    """Lanuch tmuxp in a new terminal window."""
    subprocess.Popen(
        ["rofi-sensible-terminal", "-e", "tmuxp", "load", str(config_path)],
        stdout=subprocess.DEVNULL,
    )


def error(message: str) -> None:
    """Display an error message using the rofi error dialog."""
    subprocess.Popen(["rofi", "-e", message], stdout=subprocess.DEVNULL)
