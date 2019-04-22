"""Test init"""

import pytest


@pytest.mark.parametrize(
    'alt_work, repo_present, force', [
        (False, False, False),
        (True, False, False),
        (False, True, False),
        (False, True, True),
        (True, True, True),
    ], ids=[
        'simple',
        '-w',
        'existing repo',
        '-f',
        '-w & -f',
    ])
@pytest.mark.usefixtures('ds1_work_copy')
def test_init(
        runner, yadm_y, paths, repo_config, alt_work, repo_present, force):
    """Test init

    Repos should have attribs:
        - 0600 permissions
        - not bare
        - worktree = $HOME
        - showUntrackedFiles = no
        - yadm.managed = true
    """

    # these tests will assume this for $HOME
    home = str(paths.root.mkdir('HOME'))

    # ds1_work_copy comes WITH an empty repo dir present.
    old_repo = paths.repo.join('old_repo')
    if repo_present:
        # Let's put some data in it, so we can confirm that data is gone when
        # forced to be overwritten.
        old_repo.write('old repo data')
        assert old_repo.isfile()
    else:
        paths.repo.remove()

    # command args
    args = ['init']
    if alt_work:
        args.extend(['-w', paths.work])
    if force:
        args.append('-f')

    # run init
    run = runner(yadm_y(*args), env={'HOME': home})
    assert run.err == ''

    if repo_present and not force:
        assert run.failure
        assert 'repo already exists' in run.out
        assert old_repo.isfile(), 'Missing original repo'
    else:
        assert run.success
        assert 'Initialized empty shared Git repository' in run.out

        if repo_present:
            assert not old_repo.isfile(), 'Original repo still exists'

        if alt_work:
            assert repo_config('core.worktree') == paths.work
        else:
            assert repo_config('core.worktree') == home

        # uniform repo assertions
        assert oct(paths.repo.stat().mode).endswith('00'), (
            'Repo is not secure')
        assert repo_config('core.bare') == 'false'
        assert repo_config('status.showUntrackedFiles') == 'no'
        assert repo_config('yadm.managed') == 'true'
