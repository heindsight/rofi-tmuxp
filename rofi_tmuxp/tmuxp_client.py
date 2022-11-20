"""Tmuxp compatibility layer"""
from pathlib import Path
from typing import Any, Dict


try:
    _have_config_reader = True
    from tmuxp.config_reader import ConfigReader
except ImportError:  # no_cover_tmuxp_gte_1_16
    # In tmuxp < 1.16, 3d party library `Kaptan` was used to read config files.
    # `Kaptan` is just a wrapper around `PyYAML` and `json`. Since Yaml is a superset of
    # JSON, we'll just use `yaml.safe_load`.
    import yaml

    _have_config_reader = False


try:
    from tmuxp.workspace.loader import expand as expand_config
except ImportError:  # no_cover_tmuxp_gte_1_18
    # In tmuxp < 1.18, `expand` was in `tmuxp.config`
    from tmuxp.config import expand as expand_config

try:
    from tmuxp.workspace.finders import get_workspace_dir
except ImportError:  # no_cover_tmuxp_gte_1_18
    # In tmuxp < 1.18, `get_workspace_dir` was called `get_config_dir`.
    # In tmuxp >= 1.11, < 1.18 get_config_dir was in `tmuxp.cli.utils`.
    # In tmuxp < 1.11, get_config_dir was in tmuxp.cli.
    try:
        from tmuxp.cli.utils import get_config_dir as get_workspace_dir
    except ImportError:  # no_cover_tmuxp_gte_1_11
        from tmuxp.cli import get_config_dir as get_workspace_dir

try:
    from tmuxp.workspace.finders import in_dir as configs_in_dir
except ImportError:  # no_cover_tmuxp_gte_1_18
    # In tmuxp < 1.18, `in_dir` was in `tmuxp.config`
    from tmuxp.config import in_dir as configs_in_dir


__all__ = [
    "Config",
    "configs_in_dir",
    "expand_config",
    "get_workspace_dir",
    "read_config_file",
]


Config = Dict[str, Any]


def read_config_file(config_path: Path) -> Config:
    """Read a tmuxp session config  file.

    If `tmuxp.config_reader.ConfigReader` is available, use that. Otherwise, fall back
    to `yaml.safe_load`.
    """
    if _have_config_reader:  # no_cover_tmuxp_lt_1_16
        cfg_reader = ConfigReader.from_file(config_path)
        return cfg_reader.content
    else:  # no_cover_tmuxp_gte_1_16
        return yaml.safe_load(config_path.read_text())
