"""Test help"""


def test_missing_command(runner, yadm_cmd):
    """Run without any command"""
    run = runner(command=yadm_cmd())
    assert run.failure
    assert run.err == ''
    assert run.out.startswith('Usage: yadm')


def test_help_command(runner, yadm_cmd):
    """Run with help command"""
    run = runner(command=yadm_cmd('help'))
    assert run.failure
    assert run.err == ''
    assert run.out.startswith('Usage: yadm')
