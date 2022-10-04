import json
import logging
import subprocess

import pytest
import yaml

import rofi_tmuxp

from . import match_logs


ENCODERS = {"json": json.dumps, "yaml": yaml.safe_dump}


@pytest.fixture
def config_dir(tmp_path):
    cfg_dir = tmp_path / "tmuxp"
    cfg_dir.mkdir(parents=True)
    return cfg_dir


@pytest.fixture
def write_config(config_dir):
    def _write_config(filename, data):
        file_path = config_dir / filename
        file_path.write_text(data)
        return file_path

    return _write_config


@pytest.fixture
def config_file(write_config):
    def _config_file(filename, filetype, data):
        return write_config(filename, ENCODERS[filetype](data))

    return _config_file


@pytest.fixture(autouse=True)
def mock_get_config_dir(mocker, config_dir):
    m = mocker.patch("rofi_tmuxp.get_config_dir")
    m.return_value = str(config_dir)
    return m


@pytest.fixture
def session_cfg():
    return {"windows": []}


@pytest.fixture
def session_info(session_cfg):
    return [
        {
            "filename": "test1.yml",
            "filetype": "yaml",
            "data": {**session_cfg, "session_name": "test session 1"},
        },
        {
            "filename": "( ͡° ͜ʖ ͡°).json",
            "filetype": "json",
            "data": {**session_cfg, "session_name": "田中さんにあげて下さい"},
        },
        {
            "filename": "session.yaml",
            "filetype": "yaml",
            "data": {**session_cfg, "session_name": "Session 💩"},
        },
        {
            "filename": "expand.yaml",
            "filetype": "yaml",
            "data": {**session_cfg, "session_name": "${EXPAND_ENV} session"},
        },
    ]


@pytest.fixture
def configs(config_file, session_info):
    return [config_file(**session) for session in session_info]


class TestPrintsSessions:
    @pytest.fixture(autouse=True)
    def _patch_argv(self, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr("sys.argv", ["rofi-tmuxp"])
            yield

    @pytest.mark.usefixtures("configs")
    def test_prints_sessions(self, monkeypatch, config_dir, capsys):
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
        self, session_info, config_dir, config_file, caplog, capsys
    ):
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
            "rofi_tmuxp",
            logging.WARNING,
            r"Invalid config \'{}\': No session name configured".format(
                config_dir / "invalid.yaml"
            ),
            caplog.record_tuples,
        )

    @pytest.mark.parametrize("bad_filename", ["bad.json", "bad.yaml"])
    def test_ignore_invalid_session_configs(
        self,
        session_info,
        config_dir,
        config_file,
        write_config,
        caplog,
        capsys,
        bad_filename,
    ):
        config_file(**session_info[0])
        write_config(bad_filename, "[")

        rofi_tmuxp.main()

        captured = capsys.readouterr()
        assert captured.out == "test session 1\n"
        match_logs(
            "rofi_tmuxp",
            logging.WARNING,
            r"Error loading config '{}'".format(config_dir / bad_filename),
            caplog.record_tuples,
        )

    def test_ignore_invalid_filenames(
        self, session_info, config_dir, config_file, capsys
    ):
        config_file(**session_info[0])
        ignored = {**session_info[1], "filename": "foo.conf"}
        config_file(**ignored)

        rofi_tmuxp.main()

        captured = capsys.readouterr()
        assert captured.out == "test session 1\n"

    def test_no_session_configs(self, config_dir, capsys):
        rofi_tmuxp.main()

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_safe_yaml(self, config_dir, write_config, caplog, capsys):
        write_config("danger.yaml", "session_name: !!python/object/apply:object []")

        rofi_tmuxp.main()

        captured = capsys.readouterr()
        assert captured.out == ""

        match_logs(
            "rofi_tmuxp",
            logging.WARNING,
            r"Error loading config '{}': ConstructorError".format(
                config_dir / "danger.yaml"
            ),
            caplog.record_tuples,
        )


class TestLaunchSession:
    @pytest.fixture
    def mock_popen(self, mocker):
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
        self, monkeypatch, mocker, mock_popen, config_dir, session_name, config_filename
    ):
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
    def test_session_not_found(self, monkeypatch, mocker, mock_popen, caplog):
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
            "rofi_tmuxp",
            logging.WARNING,
            r"No such session: I don't exist",
            caplog.record_tuples,
        )

    @pytest.mark.usefixtures("configs")
    def test_ignore_extra_args(self, monkeypatch, mocker, mock_popen, config_dir):
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
