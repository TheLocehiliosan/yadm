"""Unit tests: report_invalid_alts"""
import pytest


@pytest.mark.parametrize('valid', [True, False], ids=['valid', 'no_valid'])
@pytest.mark.parametrize('previous', [True, False], ids=['prev', 'no_prev'])
def test_report_invalid_alts(runner, yadm, valid, previous):
    """Use report_invalid_alts"""

    lwi = ''
    alts = 'INVALID_ALT=()'
    if previous:
        lwi = 'LEGACY_WARNING_ISSUED=1'
    if not valid:
        alts = 'INVALID_ALT=("file##invalid")'

    script = f"""
        YADM_TEST=1 source {yadm}
        {lwi}
        {alts}
        report_invalid_alts
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.out == ''
    if not valid and not previous:
        assert 'WARNING' in run.err
        assert 'file##invalid' in run.err
    else:
        assert run.err == ''
