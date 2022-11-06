"""Work with tmuxp sessions"""
import logging
from pathlib import Path

from . import tmuxp_client


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    pass


def get_sessions():
    """Get tmuxp sessions.

    Returns a dictionary mapping session name to config file paths.
    """
    sessions = {}

    for config_path in _get_config_paths():
        try:
            config = _read_config_file(config_path)
        except ValidationError as e:
            logger.warning("Invalid config '%s': %s", config_path, e)
        except Exception as e:
            logger.error("Error loading config '%s': %r", config_path, e)
        else:
            sessions[config["session_name"]] = config_path

    return sessions


def _get_config_paths():
    config_dir = Path(tmuxp_client.get_workspace_dir())

    yield from (
        config_dir / filename
        for filename in tmuxp_client.configs_in_dir(str(config_dir))
    )


def _read_config_file(config_path):
    """Read a tmuxp session config  file.

    If `tmuxp.config_reader.ConfigReader` is available, use that. Otherwise, fall back
    to `yaml.safe_load`.
    """
    cfg_reader = tmuxp_client.ConfigReader.from_file(config_path)
    config = tmuxp_client.expand_config(cfg_reader.content)

    if "session_name" not in config:
        raise ValidationError("No session name configured")

    return config
