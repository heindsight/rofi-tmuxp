import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Protocol, TypedDict
from unittest.mock import Mock

import pytest
import yaml
from pytest_mock import MockerFixture

import rofi_tmuxp
from rofi_tmuxp.tmuxp_client import Config

from . import match_logs


ENCODERS: Dict[str, Callable[[Any], str]] = {"json": json.dumps, "yaml": yaml.safe_dump}


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    cfg_dir = tmp_path / "tmuxp"
    cfg_dir.mkdir(parents=True)
    return cfg_dir


@pytest.fixture
def write_config(config_dir: Path) -> Callable[[str, str], Path]:
    def _write_config(filename: str, data: str) -> Path:
        file_path = config_dir / filename
        file_path.write_text(data)
        return file_path

    return _write_config


class SessionInfo(TypedDict):
    filename: str
    filetype: str
    data: Config


class ConfigWriter(Protocol):
    def __call__(
        self, *, filename: str, filetype: str, data: Config
    ) -> Path:  # pragma: no cover
        ...


@pytest.fixture
def config_file(write_config: Callable[[str, str], Path]) -> ConfigWriter:
    def _config_file(filename: str, filetype: str, data: Config) -> Path:
        return write_config(filename, ENCODERS[filetype](data))

    return _config_file


@pytest.fixture(autouse=True)
def mock_get_config_dir(mocker: MockerFixture, config_dir: Path) -> MockerFixture:
    m = mocker.patch("rofi_tmuxp.tmuxp_client.get_workspace_dir")
    m.return_value = str(config_dir)
    return m


@pytest.fixture
def session_cfg() -> Config:
    return {"windows": []}


@pytest.fixture
def session_info(session_cfg: Config) -> List[SessionInfo]:
    return [
        SessionInfo(
            filename="test1.yml",
            filetype="yaml",
            data={**session_cfg, "session_name": "test session 1"},
        ),
        SessionInfo(
            filename="( ͡° ͜ʖ ͡°).json",
            filetype="json",
            data={**session_cfg, "session_name": "田中さんにあげて下さい"},
        ),
        SessionInfo(
            filename="session.yaml",
            filetype="yaml",
            data={**session_cfg, "session_name": "Session 💩"},
        ),
        SessionInfo(
            filename="expand.yaml",
            filetype="yaml",
            data={**session_cfg, "session_name": "${EXPAND_ENV} session"},
        ),
    ]


@pytest.fixture
def configs(
    config_file: ConfigWriter,
    session_info: List[SessionInfo],
) -> List[Path]:
    return [config_file(**session) for session in session_info]


class TestPrintsSessions:
    @pytest.fixture(autouse=True)
    def _patch_argv(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> Generator[None, None, None]:
        with monkeypatch.context() as m:
            m.setattr("sys.argv", ["rofi-tmuxp"])
            yield

    @pytest.mark.usefixtures("configs")
    def test_prints_sessions(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setenv("EXPAND_ENV", "expanded")
        rofi_tmuxp.main()

        captured = capsys.readouterr()
        assert sorted(captured.out.splitlines()) == sorted(
            [
                "Session 💩",
                "test session 1",
                "田中さんにあげて下さい",
                "expanded session",
            ]
        )

    def test_ignore_sessions_without_name(
        self,
        session_info: List[SessionInfo],
        config_dir: Path,
        config_file: ConfigWriter,
        caplog: pytest.LogCaptureFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        config_file(**session_info[0])
        config_file(
            filename="invalid.yaml",
            filetype="yaml",
            data={"windows": [{"panes": [None, None]}]},
        )

        rofi_tmuxp.main()

        captured = capsys.readouterr()

        assert captured.out == "test session 1\n"
        match_logs(
            "rofi_tmuxp.sessions",
            logging.WARNING,
            r"Invalid config \'{}\': No session name configured".format(
                config_dir / "invalid.yaml"
            ),
            caplog.record_tuples,
        )

    @pytest.mark.parametrize("bad_filename", ["bad.json", "bad.yaml"])
    def test_ignore_invalid_session_configs(
        self,
        session_info: List[SessionInfo],
        config_dir: Path,
        config_file: ConfigWriter,
        write_config: Callable[[str, str], Path],
        caplog: pytest.LogCaptureFixture,
        capsys: pytest.CaptureFixture[str],
        bad_filename: str,
    ) -> None:
        config_file(**session_info[0])
        write_config(bad_filename, "[")

        rofi_tmuxp.main()

        captured = capsys.readouterr()
        assert captured.out == "test session 1\n"
        match_logs(
            "rofi_tmuxp.sessions",
            logging.ERROR,
            r"Error loading config '{}'".format(config_dir / bad_filename),
            caplog.record_tuples,
        )

    def test_ignore_invalid_filenames(
        self,
        session_info: List[SessionInfo],
        config_file: ConfigWriter,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        config_file(**session_info[0])
        ignored = session_info[1].copy()
        ignored["filename"] = "foo.conf"
        config_file(**ignored)

        rofi_tmuxp.main()

        captured = capsys.readouterr()
        assert captured.out == "test session 1\n"

    def test_no_session_configs(self, capsys: pytest.CaptureFixture[str]) -> None:
        rofi_tmuxp.main()

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_safe_yaml(
        self,
        config_dir: Path,
        write_config: Callable[[str, str], Path],
        caplog: pytest.LogCaptureFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        write_config("danger.yaml", "session_name: !!python/object/apply:object []")

        rofi_tmuxp.main()

        captured = capsys.readouterr()
        assert captured.out == ""

        match_logs(
            "rofi_tmuxp.sessions",
            logging.ERROR,
            r"Error loading config '{}': ConstructorError".format(
                config_dir / "danger.yaml"
            ),
            caplog.record_tuples,
        )


class TestLaunchSession:
    @pytest.fixture
    def mock_popen(self, mocker: MockerFixture) -> Mock:
        return mocker.patch("subprocess.Popen")

    @pytest.mark.parametrize(
        ("session_name", "config_filename"),
        [
            ("test session 1", "test1.yml"),
            ("田中さんにあげて下さい", "( ͡° ͜ʖ ͡°).json"),
            ("Session 💩", "session.yaml"),
        ],
    )
    @pytest.mark.usefixtures("configs")
    def test_launches_session(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mocker: MockerFixture,
        mock_popen: Mock,
        config_dir: Path,
        session_name: str,
        config_filename: str,
    ) -> None:
        with monkeypatch.context() as monkey:
            monkey.setattr("sys.argv", ["rofi-tmuxp", session_name])
            rofi_tmuxp.main()

        assert mock_popen.call_args_list == [
            mocker.call(
                [
                    "rofi-sensible-terminal",
                    "-e",
                    "tmuxp",
                    "load",
                    str(config_dir / config_filename),
                ],
                stdout=subprocess.DEVNULL,
            )
        ]

    @pytest.mark.usefixtures("configs")
    def test_session_not_found(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mocker: MockerFixture,
        mock_popen: Mock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        with monkeypatch.context() as monkey:
            monkey.setattr("sys.argv", ["rofi-tmuxp", "I don't exist"])
            rofi_tmuxp.main()

        assert mock_popen.call_args_list == [
            mocker.call(
                ["rofi", "-e", "No such session: I don't exist"],
                stdout=subprocess.DEVNULL,
            )
        ]
        match_logs(
            "rofi_tmuxp.cli",
            logging.WARNING,
            r"No such session: I don't exist",
            caplog.record_tuples,
        )

    @pytest.mark.usefixtures("configs")
    def test_ignore_extra_args(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mocker: MockerFixture,
        mock_popen: Mock,
        config_dir: Path,
    ) -> None:
        with monkeypatch.context() as monkey:
            monkey.setattr(
                "sys.argv", ["rofi-tmuxp", "test session 1", "extra", "argument"]
            )
            rofi_tmuxp.main()

        assert mock_popen.call_args_list == [
            mocker.call(
                [
                    "rofi-sensible-terminal",
                    "-e",
                    "tmuxp",
                    "load",
                    str(config_dir / "test1.yml"),
                ],
                stdout=subprocess.DEVNULL,
            )
        ]
