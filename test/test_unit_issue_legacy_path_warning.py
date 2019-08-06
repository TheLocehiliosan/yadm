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
        'hooks',
        ],
    )
def test_legacy_warning(tmpdir, runner, yadm, legacy_path):
    """Use issue_legacy_path_warning"""
    home = tmpdir.mkdir('home')

    if legacy_path:
        home.mkdir(f'.yadm').mkdir(legacy_path)

    script = f"""
        HOME={home}
        YADM_TEST=1 source {yadm}
        issue_legacy_path_warning
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    if legacy_path:
        assert 'Legacy configuration paths have been detected' in run.out
    else:
        assert run.out.rstrip() == ''
