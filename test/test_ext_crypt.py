"""Test external encryption commands"""

import pytest


@pytest.mark.parametrize(
    'crypt',
    [False, 'installed', 'installed-but-failed'],
    ids=['not-installed', 'installed', 'installed-but-failed']
)
@pytest.mark.parametrize(
        'cmd,var', [
            ['git_crypt', 'GIT_CRYPT_PROGRAM'],
            ['transcrypt', 'TRANSCRYPT_PROGRAM'],
        ],
        ids=['git-crypt', 'transcrypt'])
def test_ext_encryption(runner, yadm, paths, tmpdir, crypt, cmd, var):
    """External encryption tests"""

    paths.repo.ensure(dir=True)
    bindir = tmpdir.mkdir('bin')
    pgm = bindir.join('test-ext-crypt')

    if crypt:
        pgm.write('#!/bin/sh\necho ext-crypt ran\n')
        pgm.chmod(0o775)
    if crypt == 'installed-but-failed':
        pgm.write('false\n', mode='a')

    script = f"""
        YADM_TEST=1 source {yadm}
        YADM_REPO={paths.repo}
        {var}="{pgm}"
        {cmd} "param1"
    """

    run = runner(command=['bash'], inp=script)

    if crypt:
        if crypt == 'installed-but-failed':
            assert run.failure
        else:
            assert run.success
        assert run.out.strip() == 'ext-crypt ran'
    else:
        assert run.failure
        assert f"command '{pgm}' cannot be located" in run.out
    assert run.err == ''
