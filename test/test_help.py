"""Test help"""
import pytest


def test_missing_command(runner, yadm_cmd):
    """Run without any command"""
    run = runner(command=yadm_cmd())
    assert run.failure
    assert run.err == ""
    assert run.out.startswith("Usage: yadm")


@pytest.mark.parametrize("cmd", ["--help", "help"])
def test_help_command(runner, yadm_cmd, cmd):
    """Run with help command"""
    run = runner(command=yadm_cmd(cmd))
    assert run.failure
    assert run.err == ""
    assert run.out.startswith("Usage: yadm")
