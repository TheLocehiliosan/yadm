"""Test upgrade"""

import os

import pytest


@pytest.mark.parametrize(
    'versions', [
        ('1.12.0', '2.5.0'),
        ('1.12.0',),
        ('2.5.0',),
    ], ids=[
        '1.12.0 -> 2.5.0 -> latest',
        '1.12.0 -> latest',
        '2.5.0 -> latest',
    ])
@pytest.mark.parametrize(
    'submodule', [False, True],
    ids=['no submodule', 'with submodules'])
def test_upgrade(tmpdir, runner, versions, submodule):
    """Upgrade tests"""
    # pylint: disable=too-many-statements
    home = tmpdir.mkdir('HOME')
    env = {'HOME': str(home)}
    runner(['git', 'config', '--global', 'init.defaultBranch', 'master'],
           env=env)
    runner(['git', 'config', '--global', 'protocol.file.allow', 'always'],
           env=env)

    if submodule:
        ext_repo = tmpdir.mkdir('ext_repo')
        ext_repo.join('afile').write('some data')

        for cmd in (('init',), ('add', 'afile'), ('commit', '-m', 'test')):
            run = runner(['git', '-C', str(ext_repo), *cmd])
            assert run.success

    os.environ.pop('XDG_CONFIG_HOME', None)
    os.environ.pop('XDG_DATA_HOME', None)

    def run_version(version, *args, check_stderr=True):
        yadm = f'yadm-{version}' if version else '/yadm/yadm'
        run = runner([yadm, *args], shell=True, cwd=str(home), env=env)
        assert run.success
        if check_stderr:
            assert run.err == ''
        return run

    # Initialize the repo with the first version
    first = versions[0]
    run_version(first, 'init')

    home.join('file').write('some data')
    run_version(first, 'add', 'file')
    run_version(first, 'commit', '-m', '"First commit"')

    if submodule:
        # When upgrading via 2.5.0 we can't have a submodule that's been added
        # after being cloned as 2.5.0 fails the upgrade in that case.
        can_upgrade_cloned_submodule = '2.5.0' not in versions[1:]
        if can_upgrade_cloned_submodule:
            # Check out a repo and then add it as a submodule
            run = runner(['git', '-C', str(home), 'clone', str(ext_repo), 'b'])
            assert run.success
            run_version(first, 'submodule', 'add', str(ext_repo), 'b')

        # Add submodule without first checking it out
        run_version(first, 'submodule', 'add', str(ext_repo), 'a',
                    check_stderr=False)
        run_version(first, 'submodule', 'add', str(ext_repo), 'c',
                    check_stderr=False)

        run_version(first, 'commit', '-m', '"Add submodules"')

    for path in ('.yadm', '.config/yadm'):
        yadm_dir = home.join(path)
        if yadm_dir.exists():
            break

    yadm_dir.join('bootstrap').write('init stuff')
    run_version(first, 'add', yadm_dir.join('bootstrap'))
    run_version(first, 'commit', '-m', 'bootstrap')

    yadm_dir.join('encrypt').write('secret')

    hooks_dir = yadm_dir.mkdir('hooks')
    hooks_dir.join('pre_status').write('status')
    hooks_dir.join('post_commit').write('commit')

    run_version(first, 'config', 'local.class', 'test')
    run_version(first, 'config', 'foo.bar', 'true')

    # Run upgrade with intermediate versions and latest
    latest = None
    for version in versions[1:] + (latest,):
        run = run_version(version, 'upgrade', check_stderr=not submodule)
        if submodule:
            lines = run.err.splitlines()
            if can_upgrade_cloned_submodule:
                assert 'Migrating git directory of' in lines[0]
                assert str(home.join('b/.git')) in lines[1]
                assert str(yadm_dir.join('repo.git/modules/b')) in lines[2]
                del lines[:3]
            for line in lines:
                assert line.startswith('Submodule')
                assert 'registered for path' in line

    # Verify result for the final upgrade
    run_version(latest, 'status')

    run = run_version(latest, 'show', 'HEAD:file')
    assert run.out == 'some data'

    if submodule:
        if can_upgrade_cloned_submodule:
            assert home.join('b/afile').read() == 'some data'
        assert home.join('a/afile').read() == 'some data'
        assert home.join('c/afile').read() == 'some data'

    yadm_dir = home.join('.config/yadm')

    assert yadm_dir.join('bootstrap').read() == 'init stuff'
    assert yadm_dir.join('encrypt').read() == 'secret'

    hooks_dir = yadm_dir.join('hooks')
    assert hooks_dir.join('pre_status').read() == 'status'
    assert hooks_dir.join('post_commit').read() == 'commit'

    run = run_version(latest, 'config', 'local.class')
    assert run.out.rstrip() == 'test'

    run = run_version(latest, 'config', 'foo.bar')
    assert run.out.rstrip() == 'true'
