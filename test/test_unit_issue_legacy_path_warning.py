"""Unit tests: issue_legacy_path_warning"""
import pytest


@pytest.mark.parametrize(
    'legacy_path', [
        None,
        'repo.git',
        'config',
        'encrypt',
        'files.gpg',
        'bootstrap',
        'hooks/pre_command',
        'hooks/post_command',
        ],
    )
@pytest.mark.parametrize(
    'upgrade', [True, False], ids=['upgrade', 'no-upgrade'])
def test_legacy_warning(tmpdir, runner, yadm, upgrade, legacy_path):
    """Use issue_legacy_path_warning"""
    home = tmpdir.mkdir('home')

    if legacy_path:
        home.mkdir(f'.yadm').ensure(legacy_path)

    main_args = 'MAIN_ARGS=("upgrade")' if upgrade else ''
    script = f"""
        HOME={home}
        YADM_TEST=1 source {yadm}
        {main_args}
        issue_legacy_path_warning
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    if legacy_path and not upgrade:
        assert 'Legacy configuration paths have been detected' in run.out
    else:
        assert run.out.rstrip() == ''
