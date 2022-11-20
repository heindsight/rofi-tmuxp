"""Work with tmuxp sessions"""
import logging
from pathlib import Path
from typing import Dict, Iterator

from . import tmuxp_client


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    pass


def get_sessions() -> Dict[str, Path]:
    """Get tmuxp sessions.

    Returns a dictionary mapping session name to config file paths.
    """
    sessions = {}

    for config_path in _get_config_paths():
        try:
            config = _load_session_config(config_path)
        except ValidationError as e:
            logger.warning("Invalid config '%s': %s", config_path, e)
        except Exception as e:
            logger.error("Error loading config '%s': %r", config_path, e)
        else:
            sessions[config["session_name"]] = config_path

    return sessions


def _get_config_paths() -> Iterator[Path]:
    config_dir = Path(tmuxp_client.get_workspace_dir())

    yield from (
        config_dir / filename
        for filename in tmuxp_client.configs_in_dir(str(config_dir))
    )


def _load_session_config(config_path: Path) -> tmuxp_client.Config:
    """Load a tmuxp session config file.


    Raises `ValidationError` if there is no `session_name` defined in the config file.
    """
    raw_config = tmuxp_client.read_config_file(config_path)

    if "session_name" not in raw_config:
        raise ValidationError("No session name configured")

    return tmuxp_client.expand_config(raw_config)
