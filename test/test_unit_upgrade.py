"""Unit tests: upgrade"""
import pytest

LEGACY_PATHS = [
    'config',
    'encrypt',
    'files.gpg',
    'bootstrap',
    'hooks/pre_command',
    'hooks/post_command',
]

# used:
# YADM_COMPATIBILITY
# YADM_DIR
# YADM_LEGACY_DIR
# GIT_PROGRAM
@pytest.mark.parametrize('condition', ['compat', 'equal', 'existing_repo'])
def test_upgrade_errors(tmpdir, runner, yadm, condition):
    """Test upgrade() error conditions"""

    compatibility = 'YADM_COMPATIBILITY=1' if condition == 'compat' else ''

    home = tmpdir.mkdir('home')
    yadm_dir = home.join('.config/yadm')
    legacy_dir = home.join('.yadm')
    if condition == 'equal':
        legacy_dir = yadm_dir
    if condition == 'existing_repo':
        yadm_dir.ensure_dir('repo.git')
        legacy_dir.ensure_dir('repo.git')

    script = f"""
        YADM_TEST=1 source {yadm}
        {compatibility}
        YADM_DIR="{yadm_dir}"
        YADM_REPO="{yadm_dir}/repo.git"
        YADM_LEGACY_DIR="{legacy_dir}"
        upgrade
    """
    run = runner(command=['bash'], inp=script)
    assert run.failure
    assert run.err == ''
    assert 'Unable to upgrade' in run.out
    if condition == 'compat':
        assert 'YADM_COMPATIBILITY' in run.out
    if condition == 'equal':
        assert 'has been resolved as' in run.out
    if condition == 'existing_repo':
        assert 'already exists' in run.out


@pytest.mark.parametrize(
    'condition', ['no-paths', 'untracked', 'tracked', 'submodules'])
def test_upgrade(tmpdir, runner, yadm, condition):
    """Test upgrade()

    When testing the condition of git-tracked data, "echo" will be used as a
    mock for git. echo will return true, simulating a positive result from "git
    ls-files". Also echo will report the parameters for "git mv".
    """
    home = tmpdir.mkdir('home')
    yadm_dir = home.join('.config/yadm')
    legacy_dir = home.join('.yadm')

    if condition != 'no-paths':
        legacy_dir.join('repo.git/config').write('test-repo', ensure=True)
        for lpath in LEGACY_PATHS:
            legacy_dir.join(lpath).write(lpath, ensure=True)

    mock_git = ""
    if condition in ['tracked', 'submodules']:
        mock_git = f'''
            function git() {{
                echo "$@"
                if [[ "$*" == *.gitmodules* ]]; then
                    return { '0' if condition == 'submodules' else '1' }
                fi
                return 0
            }}
        '''

    script = f"""
        YADM_TEST=1 source {yadm}
        YADM_DIR="{yadm_dir}"
        YADM_REPO="{yadm_dir}/repo.git"
        YADM_LEGACY_DIR="{legacy_dir}"
        GIT_PROGRAM="git"
        {mock_git}
        function cd {{ echo "$@";}}
        upgrade
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    if condition == 'no-paths':
        assert 'Upgrade is not necessary' in run.out
    else:
        for lpath in LEGACY_PATHS + ['repo.git']:
            expected = (
                f'Moving {legacy_dir.join(lpath)} '
                f'to {yadm_dir.join(lpath)}')
            assert expected in run.out
        if condition == 'untracked':
            assert 'test-repo' in yadm_dir.join('repo.git/config').read()
            for lpath in LEGACY_PATHS:
                assert lpath in yadm_dir.join(lpath).read()
        elif condition in ['tracked', 'submodules']:
            for lpath in LEGACY_PATHS:
                expected = (
                    f'mv {legacy_dir.join(lpath)} '
                    f'{yadm_dir.join(lpath)}')
                assert expected in run.out
            assert 'files tracked by yadm have been renamed' in run.out
            if condition == 'submodules':
                assert 'submodule deinit -f .' in run.out
                assert 'submodule update --init --recursive' in run.out
            else:
                assert 'submodule deinit -f .' not in run.out
                assert 'submodule update --init --recursive' not in run.out
