"""Test git-crypt"""

import pytest


@pytest.mark.parametrize(
    'crypt',
    [False, 'installed', 'installed-but-failed'],
    ids=['not-installed', 'installed', 'installed-but-failed']
)
def test_git_crypt(runner, yadm, paths, tmpdir, crypt):
    """git-crypt tests"""

    paths.repo.ensure(dir=True)
    bindir = tmpdir.mkdir('bin')
    pgm = bindir.join('test-git-crypt')

    if crypt:
        pgm.write(f'#!/bin/sh\necho git-crypt ran\n')
        pgm.chmod(0o775)
    if crypt == 'installed-but-failed':
        pgm.write('false\n', mode='a')

    script = f"""
        YADM_TEST=1 source {yadm}
        YADM_REPO={paths.repo}
        GIT_CRYPT_PROGRAM="{pgm}"
        git_crypt "param1"
    """

    run = runner(command=['bash'], inp=script)

    if crypt:
        if crypt == 'installed-but-failed':
            assert run.failure
        else:
            assert run.success
        assert run.out.strip() == 'git-crypt ran'
    else:
        assert run.failure
        assert f"command '{pgm}' cannot be located" in run.out
    assert run.err == ''
