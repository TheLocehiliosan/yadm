"""Test clean"""


def test_clean_command(runner, yadm_y):
    """Run with clean command"""
    run = runner(command=yadm_y('clean'))
    # do nothing, this is a dangerous Git command when managing dot files
    # report the command as disabled and exit as a failure
    assert run.failure
    assert run.err == ''
    assert 'disabled' in run.out
