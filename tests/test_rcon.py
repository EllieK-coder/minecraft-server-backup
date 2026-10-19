from unittest.mock import call, patch

import pytest

from mcbackup.rcon import paused_saving


@patch("mcbackup.rcon.MCRcon")
def test_pauses_and_resumes_saving(mock_rcon):
    client = mock_rcon.return_value.__enter__.return_value

    with paused_saving("127.0.0.1", "pw"):
        pass

    assert client.command.call_args_list == [
        call("save-off"),
        call("save-all flush"),
        call("save-on"),
    ]


@patch("mcbackup.rcon.MCRcon")
def test_resumes_saving_even_if_backup_fails(mock_rcon):
    client = mock_rcon.return_value.__enter__.return_value

    with pytest.raises(RuntimeError):
        with paused_saving("127.0.0.1", "pw"):
            raise RuntimeError("archive failed")

    client.command.assert_called_with("save-on")


@patch("mcbackup.rcon.MCRcon")
def test_uses_given_port(mock_rcon):
    with paused_saving("127.0.0.1", "pw", port=25580):
        pass

    mock_rcon.assert_called_once_with("127.0.0.1", "pw", port=25580)