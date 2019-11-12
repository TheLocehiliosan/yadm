"""Unit tests: record_score"""
import pytest

INIT_VARS = """
    score=0
    local_class=testclass
    local_system=testsystem
    local_host=testhost
    local_user=testuser
    alt_scores=()
    alt_filenames=()
    alt_targets=()
    alt_template_cmds=()
"""

REPORT_RESULTS = """
    echo "SIZE:${#alt_scores[@]}"
    echo "SCORES:${alt_scores[@]}"
    echo "FILENAMES:${alt_filenames[@]}"
    echo "TARGETS:${alt_targets[@]}"
"""


def test_dont_record_zeros(runner, yadm):
    """Record nothing if the score is zero"""

    script = f"""
        YADM_TEST=1 source {yadm}
        {INIT_VARS}
        record_score "0" "testfile" "testtarget"
        {REPORT_RESULTS}
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert 'SIZE:0\n' in run.out
    assert 'SCORES:\n' in run.out
    assert 'FILENAMES:\n' in run.out
    assert 'TARGETS:\n' in run.out


def test_new_scores(runner, yadm):
    """Test new scores"""

    script = f"""
        YADM_TEST=1 source {yadm}
        {INIT_VARS}
        record_score "1" "file_one"   "targ_one"
        record_score "2" "file_two"   "targ_two"
        record_score "4" "file_three" "targ_three"
        {REPORT_RESULTS}
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert 'SIZE:3\n' in run.out
    assert 'SCORES:1 2 4\n' in run.out
    assert 'FILENAMES:file_one file_two file_three\n' in run.out
    assert 'TARGETS:targ_one targ_two targ_three\n' in run.out


@pytest.mark.parametrize('difference', ['lower', 'equal', 'higher'])
def test_existing_scores(runner, yadm, difference):
    """Test existing scores"""

    expected_score = '2'
    expected_target = 'existing_target'
    if difference == 'lower':
        score = '1'
    elif difference == 'equal':
        score = '2'
    else:
        score = '4'
        expected_score = '4'
        expected_target = 'new_target'

    script = f"""
        YADM_TEST=1 source {yadm}
        {INIT_VARS}
        alt_scores=(2)
        alt_filenames=("testfile")
        alt_targets=("existing_target")
        record_score "{score}" "testfile" "new_target"
        {REPORT_RESULTS}
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert 'SIZE:1\n' in run.out
    assert f'SCORES:{expected_score}\n' in run.out
    assert 'FILENAMES:testfile\n' in run.out
    assert f'TARGETS:{expected_target}\n' in run.out


def test_existing_template(runner, yadm):
    """Record nothing if a template command is registered for this file"""

    script = f"""
        YADM_TEST=1 source {yadm}
        {INIT_VARS}
        alt_scores=(1)
        alt_filenames=("testfile")
        alt_targets=()
        alt_template_cmds=("existing_template")
        record_score "2" "testfile" "new_target"
        {REPORT_RESULTS}
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert 'SIZE:1\n' in run.out
    assert 'SCORES:1\n' in run.out
    assert 'FILENAMES:testfile\n' in run.out
    assert 'TARGETS:\n' in run.out
