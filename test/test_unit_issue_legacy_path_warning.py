"""Unit tests: issue_legacy_path_warning"""
import pytest


@pytest.mark.parametrize(
    'legacy_path', [
        None,
        'repo.git',
        'files.gpg',
        ],
    )
@pytest.mark.parametrize(
    'override', [True, False], ids=['override', 'no-override'])
@pytest.mark.parametrize(
    'upgrade', [True, False], ids=['upgrade', 'no-upgrade'])
def test_legacy_warning(tmpdir, runner, yadm, upgrade, override, legacy_path):
    """Use issue_legacy_path_warning"""
    home = tmpdir.mkdir('home')

    if legacy_path:
        home.ensure(f'.config/yadm/{str(legacy_path)}')

    override = 'YADM_OVERRIDE_REPO=override' if override else ''
    main_args = 'MAIN_ARGS=("upgrade")' if upgrade else ''
    script = f"""
        XDG_CONFIG_HOME=
        XDG_DATA_HOME=
        HOME={home}
        YADM_TEST=1 source {yadm}
        {main_args}
        {override}
        set_yadm_dirs
        issue_legacy_path_warning
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    if legacy_path and (not upgrade) and (not override):
        assert 'Legacy paths have been detected' in run.out
    else:
        assert 'Legacy paths have been detected' not in run.out
