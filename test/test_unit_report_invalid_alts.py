"""Unit tests: report_invalid_alts"""
import pytest


@pytest.mark.parametrize(
    'condition', [
        'compat',
        'previous-message',
        'invalid-alts',
        'no-invalid-alts',
    ])
def test_report_invalid_alts(runner, yadm, condition):
    """Use report_invalid_alts"""

    compat = ''
    previous = ''
    alts = 'INVALID_ALT=()'
    if condition == 'compat':
        compat = 'YADM_COMPATIBILITY=1'
    if condition == 'previous-message':
        previous = 'LEGACY_WARNING_ISSUED=1'
    if condition == 'invalid-alts':
        alts = 'INVALID_ALT=("file##invalid")'

    script = f"""
        YADM_TEST=1 source {yadm}
        {compat}
        {previous}
        {alts}
        report_invalid_alts
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    if condition == 'invalid-alts':
        assert 'WARNING' in run.out
        assert 'file##invalid' in run.out
    else:
        assert run.out == ''
