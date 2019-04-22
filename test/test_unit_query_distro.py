"""Unit tests: query_distro"""


def test_lsb_release_present(runner, yadm, tst_distro):
    """Match lsb_release -si when present"""
    script = f"""
        YADM_TEST=1 source {yadm}
        query_distro
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert run.out.rstrip() == tst_distro


def test_lsb_release_missing(runner, yadm):
    """Empty value when missing"""
    script = f"""
        YADM_TEST=1 source {yadm}
        LSB_RELEASE_PROGRAM="missing_lsb_release"
        query_distro
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert run.out.rstrip() == ''
