"""Unit tests: set_alt_values"""
import pytest
import utils


@pytest.mark.parametrize(
    'override', [
        False,
        'class',
        'os',
        'hostname',
        'user',
        ],
    ids=[
        'no-override',
        'override-class',
        'override-os',
        'override-hostname',
        'override-user',
        ]
    )
@pytest.mark.usefixtures('ds1_copy')
def test_set_alt_values(
        runner, yadm, paths, tst_sys, tst_host, tst_user, override):
    """Use issue_legacy_path_warning"""
    script = f"""
        YADM_TEST=1 source {yadm} &&
        set_operating_system &&
        YADM_DIR={paths.yadm} YADM_DATA={paths.data} configure_paths &&
        set_alt_values
        echo "class='$YADM_CLASS'"
        echo "os='$YADM_OS'"
        echo "host='$YADM_HOSTNAME'"
        echo "user='$YADM_USER'"
    """

    if override:
        utils.set_local(paths, override, 'override')

    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''

    if override == 'class':
        assert "class='override'" in run.out
    else:
        assert "class=''" in run.out

    if override == 'os':
        assert "os='override'" in run.out
    else:
        assert f"os='{tst_sys}'" in run.out

    if override == 'hostname':
        assert "host='override'" in run.out
    else:
        assert f"host='{tst_host}'" in run.out

    if override == 'user':
        assert "user='override'" in run.out
    else:
        assert f"user='{tst_user}'" in run.out


def test_distro(runner, yadm):
    """Assert that local_distro is set"""

    script = f"""
        YADM_TEST=1 source {yadm}
        function config() {{ echo "$1"; }}
        function query_distro() {{ echo "testdistro"; }}
        set_alt_values
        echo "distro='$YADM_DISTRO'"
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert run.out.strip() == "distro='testdistro'"
