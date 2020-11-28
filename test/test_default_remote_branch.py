"""Unit tests: _default_remote_branch()"""
import pytest


@pytest.mark.parametrize('condition', ['found', 'missing'])
def test(runner, paths, condition):
    """Test _default_remote_branch()"""
    test_branch = 'test/branch'
    output = f'ref: refs/heads/{test_branch}\\tHEAD\\n'
    if condition == 'missing':
        output = 'output that is missing ref'
    script = f"""
        YADM_TEST=1 source {paths.pgm}
        function git() {{
          printf '{output}';
          printf 'mock stderr\\n' 1>&2
        }}
        _default_remote_branch URL
    """
    print(condition)
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    if condition == 'found':
        assert run.out.strip() == test_branch
    else:
        assert run.out.strip() == 'master'
