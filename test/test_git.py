"""Test git"""

import re
import pytest


@pytest.mark.usefixtures('ds1_copy')
def test_git(runner, yadm_y, paths):
    """Test series of passthrough git commands

    Passthru unknown commands to Git
    Git command 'add' - badfile
    Git command 'add'
    Git command 'status'
    Git command 'commit'
    Git command 'log'
    """

    # passthru unknown commands to Git
    run = runner(command=yadm_y('bogus'))
    assert run.failure
    assert "git: 'bogus' is not a git command." in run.err
    assert "See 'git --help'" in run.err
    assert run.out == ''

    # git command 'add' - badfile
    run = runner(command=yadm_y('add', '-v', 'does_not_exist'))
    assert run.code == 128
    assert "pathspec 'does_not_exist' did not match any files" in run.err
    assert run.out == ''

    # git command 'add'
    newfile = paths.work.join('test_git')
    newfile.write('test_git')
    run = runner(command=yadm_y('add', '-v', str(newfile)))
    assert run.success
    assert run.err == ''
    assert "add 'test_git'" in run.out

    # git command 'status'
    run = runner(command=yadm_y('status'))
    assert run.success
    assert run.err == ''
    assert re.search(r'new file:\s+test_git', run.out)

    # git command 'commit'
    run = runner(command=yadm_y('commit', '-m', 'Add test_git'))
    assert run.success
    assert run.err == ''
    assert '1 file changed' in run.out
    assert '1 insertion' in run.out
    assert re.search(r'create mode .+ test_git', run.out)

    # git command 'log'
    run = runner(command=yadm_y('log', '--oneline'))
    assert run.success
    assert run.err == ''
    assert 'Add test_git' in run.out
