"""Tmuxp compatibility layer"""
try:
    from tmuxp.config_reader import ConfigReader
except ImportError:  # pragma: no cover
    # In tmuxp < 1.16, 3d party library `Kaptan` was used to read config files.
    # `Kaptan` is just a wrapper around `yaml.safe_load` and `json.load`. Since Yaml is
    # a superset of JSON, we just use `yaml.safe_load` and wrap it in a class with
    # a similar interface to `tmuxp.config_reader.ConfigReader`.
    import yaml

    class _ConfigReader:
        def __init__(self, content):
            self.content = content

        @classmethod
        def from_file(cls, config_path):
            data = yaml.safe_load(config_path.read_text())
            return cls(data)

    ConfigReader = _ConfigReader

try:
    from tmuxp.workspace.loader import expand as expand_config
except ImportError:  # pragma: no cover
    # In tmuxp < 1.18, `expand` was in `tmuxp.config`
    from tmuxp.config import expand as expand_config

try:
    from tmuxp.workspace.finders import get_workspace_dir
except ImportError:  # pragma: no cover
    # In tmuxp < 1.18, `get_workspace_dir` was called `get_config_dir`.
    # In tmuxp >= 1.11, < 1.18 get_config_dir was in `tmuxp.cli.utils`.
    # In tmuxp < 1.11, get_config_dir was in tmuxp.cli.
    try:
        from tmuxp.cli.utils import get_config_dir as get_workspace_dir
    except ImportError:  # pragma: no cover
        from tmuxp.cli import get_config_dir as get_workspace_dir

try:
    from tmuxp.workspace.finders import in_dir as configs_in_dir
except ImportError:  # pragma: no cover
    # In tmuxp < 1.18, `in_dir` was in `tmuxp.config`
    from tmuxp.config import in_dir as configs_in_dir


__all__ = ["ConfigReader", "expand_config", "get_workspace_dir", "configs_in_dir"]
