"""Unit tests: upgrade"""
import pytest


@pytest.mark.parametrize('condition', ['override', 'equal', 'existing_repo'])
def test_upgrade_errors(tmpdir, runner, yadm, condition):
    """Test upgrade() error conditions"""

    home = tmpdir.mkdir('home')
    yadm_dir = home.join('.config/yadm')
    yadm_data = home.join('.local/share/yadm')
    override = ''
    if condition == 'override':
        override = 'override'
    if condition == 'equal':
        yadm_data = yadm_dir
    if condition == 'existing_repo':
        yadm_dir.ensure_dir('repo.git')
        yadm_data.ensure_dir('repo.git')

    script = f"""
        YADM_TEST=1 source {yadm}
        YADM_DIR="{yadm_dir}"
        YADM_DATA="{yadm_data}"
        YADM_REPO="{yadm_data}/repo.git"
        YADM_LEGACY_ARCHIVE="files.gpg"
        YADM_OVERRIDE_REPO="{override}"
        upgrade
    """
    run = runner(command=['bash'], inp=script)
    assert run.failure
    assert run.err == ''
    assert 'Unable to upgrade' in run.out
    if condition in ['override', 'equal']:
        assert 'Paths have been overridden' in run.out
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
    yadm_data = home.join('.local/share/yadm')

    if condition != 'no-paths':
        yadm_dir.join('repo.git/config').write('test-repo', ensure=True)
        yadm_dir.join('files.gpg').write('files.gpg', ensure=True)

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
        YADM_DATA="{yadm_data}"
        YADM_REPO="{yadm_data}/repo.git"
        YADM_ARCHIVE="{yadm_data}/archive"
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
        for (lpath, npath) in [
                ('repo.git', 'repo.git'), ('files.gpg', 'archive')]:
            expected = (
                f'Moving {yadm_dir.join(lpath)} '
                f'to {yadm_data.join(npath)}')
            assert expected in run.out
        if condition == 'untracked':
            assert 'test-repo' in yadm_data.join('repo.git/config').read()
            assert 'files.gpg' in yadm_data.join('archive').read()
        elif condition in ['tracked', 'submodules']:
            expected = (
                f'mv {yadm_dir.join("files.gpg")} '
                f'{yadm_data.join("archive")}')
            assert expected in run.out
            assert 'files tracked by yadm have been renamed' in run.out
            if condition == 'submodules':
                assert 'submodule deinit -f .' in run.out
                assert 'submodule update --init --recursive' in run.out
            else:
                assert 'submodule deinit -f .' not in run.out
                assert 'submodule update --init --recursive' not in run.out
