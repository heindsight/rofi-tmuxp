"""Tmuxp compatibility layer."""

from pathlib import Path
from typing import Any, Dict

import yaml
from tmuxp.workspace.finders import get_workspace_dir
from tmuxp.workspace.finders import in_dir as configs_in_dir
from tmuxp.workspace.loader import expand as expand_config


__all__ = [
    "Config",
    "configs_in_dir",
    "expand_config",
    "get_workspace_dir",
    "read_config_file",
]


Config = Dict[str, Any]


def read_config_file(config_path: Path) -> Config:
    """Read a tmuxp session config  file."""
    cfg: Config = yaml.safe_load(config_path.read_text())
    return cfg
