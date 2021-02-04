"""Test clone"""

import os
import re
import pytest

BOOTSTRAP_CODE = 123
BOOTSTRAP_MSG = 'Bootstrap successful'


@pytest.mark.usefixtures('remote')
@pytest.mark.parametrize(
    'good_remote, repo_exists, force, conflicts', [
        (False, False, False, False),
        (True, False, False, False),
        (True, True, False, False),
        (True, True, True, False),
        (True, False, False, True),
    ], ids=[
        'bad remote',
        'simple',
        'existing repo',
        '-f',
        'conflicts',
    ])
def test_clone(
        runner, paths, yadm_cmd, repo_config, ds1,
        good_remote, repo_exists, force, conflicts):
    """Test basic clone operation"""

    # clear out the work path
    paths.work.remove()
    paths.work.mkdir()

    # determine remote url
    remote_url = f'file://{paths.remote}'
    if not good_remote:
        remote_url = 'file://bad_remote'

    old_repo = None
    if repo_exists:
        # put a repo in the way
        paths.repo.mkdir()
        old_repo = paths.repo.join('old_repo')
        old_repo.write('old_repo')

    if conflicts:
        ds1.tracked[0].relative.write('conflict')
        assert ds1.tracked[0].relative.exists()

    # run the clone command
    args = ['clone', '-w', paths.work]
    if force:
        args += ['-f']
    args += [remote_url]
    run = runner(command=yadm_cmd(*args))

    if not good_remote:
        # clone should fail
        assert run.failure
        assert run.out == ''
        assert 'Unable to clone the repository' in run.err
        assert not paths.repo.exists()
    elif repo_exists and not force:
        # can't overwrite data
        assert run.failure
        assert run.out == ''
        assert 'Git repo already exists' in run.err
    else:
        # clone should succeed, and repo should be configured properly
        assert successful_clone(run, paths, repo_config)

        # these clones should have master as HEAD
        verify_head(paths, 'master')

        # ensure conflicts are handled properly
        if conflicts:
            assert 'NOTE' in run.out
            assert 'Local files with content that differs' in run.out

        # confirm correct Git origin
        run = runner(
            command=('git', 'remote', '-v', 'show'),
            env={'GIT_DIR': paths.repo})
        assert run.success
        assert run.err == ''
        assert f'origin\t{remote_url}' in run.out

        # ensure conflicts are really preserved
        if conflicts:
            # test that the conflicts are preserved in the work tree
            run = runner(
                command=yadm_cmd('status', '-uno', '--porcelain'),
                cwd=paths.work)
            assert run.success
            assert run.err == ''
            assert str(ds1.tracked[0].path) in run.out

            # verify content of the conflicts
            run = runner(command=yadm_cmd('diff'), cwd=paths.work)
            assert run.success
            assert run.err == ''
            assert '\n+conflict' in run.out, 'conflict overwritten'

    # another force-related assertion
    if old_repo:
        if force:
            assert not old_repo.exists()
        else:
            assert old_repo.exists()


@pytest.mark.usefixtures('remote')
@pytest.mark.parametrize(
    'bs_exists, bs_param, answer', [
        (False, '--bootstrap', None),
        (True, '--bootstrap', None),
        (True, '--no-bootstrap', None),
        (True, None, 'n'),
        (True, None, 'y'),
    ], ids=[
        'force, missing',
        'force, existing',
        'prevent',
        'existing, answer n',
        'existing, answer y',
    ])
def test_clone_bootstrap(
        runner, paths, yadm_cmd, repo_config, bs_exists, bs_param, answer):
    """Test bootstrap clone features"""

    # establish a bootstrap
    create_bootstrap(paths, bs_exists)

    # run the clone command
    args = ['clone', '-w', paths.work]
    if bs_param:
        args += [bs_param]
    args += [f'file://{paths.remote}']
    expect = []
    if answer:
        expect.append(('Would you like to execute it now', answer))
    run = runner(command=yadm_cmd(*args), expect=expect)

    if answer:
        assert 'Would you like to execute it now' in run.out

    expected_code = 0
    if bs_exists and bs_param != '--no-bootstrap':
        expected_code = BOOTSTRAP_CODE

    if answer == 'y':
        expected_code = BOOTSTRAP_CODE
        assert BOOTSTRAP_MSG in run.out
    elif answer == 'n':
        expected_code = 0
        assert BOOTSTRAP_MSG not in run.out

    assert successful_clone(run, paths, repo_config, expected_code)
    verify_head(paths, 'master')

    if not bs_exists:
        assert BOOTSTRAP_MSG not in run.out


def create_bootstrap(paths, exists):
    """Create bootstrap file for test"""
    if exists:
        paths.bootstrap.write(
            '#!/bin/sh\n'
            f'echo {BOOTSTRAP_MSG}\n'
            f'exit {BOOTSTRAP_CODE}\n')
        paths.bootstrap.chmod(0o775)
        assert paths.bootstrap.exists()
    else:
        assert not paths.bootstrap.exists()


@pytest.mark.usefixtures('remote')
@pytest.mark.parametrize(
    'private_type, in_repo, in_work', [
        ('ssh', False, True),
        ('gnupg', False, True),
        ('ssh', True, True),
        ('gnupg', True, True),
        ('ssh', True, False),
        ('gnupg', True, False),
    ], ids=[
        'open ssh, not tracked',
        'open gnupg, not tracked',
        'open ssh, tracked',
        'open gnupg, tracked',
        'missing ssh, tracked',
        'missing gnupg, tracked',
    ])
def test_clone_perms(
        runner, yadm_cmd, paths, repo_config,
        private_type, in_repo, in_work):
    """Test clone permission-related functions"""

    # update remote repo to include private data
    if in_repo:
        rpath = paths.work.mkdir(f'.{private_type}').join('related')
        rpath.write('related')
        os.system(f'GIT_DIR="{paths.remote}" git add {rpath}')
        os.system(f'GIT_DIR="{paths.remote}" git commit -m "{rpath}"')
        rpath.remove()

    # ensure local private data is insecure at the start
    if in_work:
        pdir = paths.work.join(f'.{private_type}')
        if not pdir.exists():
            pdir.mkdir()
        pfile = pdir.join('existing')
        pfile.write('existing')
        pdir.chmod(0o777)
        pfile.chmod(0o777)
    else:
        paths.work.remove()
        paths.work.mkdir()

    env = {'HOME': paths.work}
    run = runner(
        yadm_cmd('clone', '-d', '-w', paths.work, f'file://{paths.remote}'),
        env=env
    )

    assert successful_clone(run, paths, repo_config)
    verify_head(paths, 'master')
    if in_work:
        # private directories which already exist, should be left as they are,
        # which in this test is "insecure".
        assert re.search(
            f'initial private dir perms drwxrwxrwx.+.{private_type}',
            run.out)
        assert re.search(
            f'pre-checkout private dir perms drwxrwxrwx.+.{private_type}',
            run.out)
        assert re.search(
            f'post-checkout private dir perms drwxrwxrwx.+.{private_type}',
            run.out)
    else:
        # private directories which are created, should be done prior to
        # checkout, and with secure permissions.
        assert 'initial private dir perms' not in run.out
        assert re.search(
            f'pre-checkout private dir perms drwx------.+.{private_type}',
            run.out)
        assert re.search(
            f'post-checkout private dir perms drwx------.+.{private_type}',
            run.out)

    # standard perms still apply afterwards unless disabled with auto.perms
    assert oct(
        paths.work.join(f'.{private_type}').stat().mode).endswith('00'), (
            f'.{private_type} has not been secured by auto.perms')


@pytest.mark.usefixtures('remote')
@pytest.mark.parametrize(
    'branch', ['master', 'default', 'valid', 'invalid'])
def test_alternate_branch(runner, paths, yadm_cmd, repo_config, branch):
    """Test cloning a branch other than master"""

    # add a "valid" branch to the remote
    os.system(f'GIT_DIR="{paths.remote}" git checkout -b valid')
    os.system(
        f'GIT_DIR="{paths.remote}" git commit '
        f'--allow-empty -m "This branch is valid"')
    if branch != 'default':
        # When branch == 'default', the "default" branch of the remote repo
        # will remain "valid" to validate identification the correct default
        # branch by inspecting the repo. Otherwise it will be set back to
        # "master"
        os.system(f'GIT_DIR="{paths.remote}" git checkout master')

    # clear out the work path
    paths.work.remove()
    paths.work.mkdir()

    remote_url = f'file://{paths.remote}'

    # run the clone command
    args = ['clone', '-w', paths.work]
    if branch not in ['master', 'default']:
        args += ['-b', branch]
    args += [remote_url]
    run = runner(command=yadm_cmd(*args))

    if branch == 'invalid':
        assert run.failure
        assert 'ERROR: Unable to clone the repository' in run.err
        assert f"Remote branch {branch} not found in upstream" in run.err
    else:
        assert successful_clone(run, paths, repo_config)

        # confirm correct Git origin
        run = runner(
            command=('git', 'remote', '-v', 'show'),
            env={'GIT_DIR': paths.repo})
        assert run.success
        assert run.err == ''
        assert f'origin\t{remote_url}' in run.out
        run = runner(command=yadm_cmd('show'))
        if branch == 'master':
            assert 'Initial commit' in run.out
            verify_head(paths, 'master')
        else:
            assert 'This branch is valid' in run.out
            verify_head(paths, 'valid')


def successful_clone(run, paths, repo_config, expected_code=0):
    """Assert clone is successful"""
    assert run.code == expected_code
    assert oct(paths.repo.stat().mode).endswith('00'), 'Repo is not secured'
    assert repo_config('core.bare') == 'false'
    assert repo_config('status.showUntrackedFiles') == 'no'
    assert repo_config('yadm.managed') == 'true'
    return True


@pytest.fixture()
def remote(paths, ds1_repo_copy):
    """Function scoped remote (based on ds1)"""
    # pylint: disable=unused-argument
    # This is ignored because
    # @pytest.mark.usefixtures('ds1_remote_copy')
    # cannot be applied to another fixture.
    paths.remote.remove()
    paths.repo.move(paths.remote)


def test_no_repo(runner, yadm_cmd, ):
    """Test cloning without specifying a repo"""
    run = runner(command=yadm_cmd('clone', '-f'))
    assert run.failure
    assert run.out == ''
    assert 'ERROR: Unable to clone the repository' in run.err
    assert 'repository \'repo.git\' does not exist' in run.err


def verify_head(paths, branch):
    """Assert the local repo has the correct head branch"""
    assert paths.repo.join('HEAD').read() == f'ref: refs/heads/{branch}\n'
