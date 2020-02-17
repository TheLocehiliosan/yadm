"""Unit tests: query_distro"""
import pytest


@pytest.mark.parametrize(
    'condition', ['lsb_release', 'os-release', 'os-release-quotes', 'missing'])
def test_query_distro(runner, yadm, tst_distro, tmp_path, condition):
    """Match lsb_release -si when present"""
    test_release = 'testrelease'
    lsb_release = ''
    os_release = tmp_path.joinpath('os-release')
    if 'os-release' in condition:
        quotes = '"' if 'quotes' in condition else ''
        os_release.write_text(
            f"testing\nID={quotes}{test_release}{quotes}\nrelease")
    if condition != 'lsb_release':
        lsb_release = 'LSB_RELEASE_PROGRAM="missing_lsb_release"'
    script = f"""
        YADM_TEST=1 source {yadm}
        {lsb_release}
        OS_RELEASE="{os_release}"
        query_distro
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    if condition == 'lsb_release':
        assert run.out.rstrip() == tst_distro
    elif 'os-release' in condition:
        assert run.out.rstrip() == test_release
    else:
        assert run.out.rstrip() == ''
