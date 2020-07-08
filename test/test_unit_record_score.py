"""Unit tests: record_score"""
import pytest

INIT_VARS = """
    score=0
    local_class=testclass
    local_system=testsystem
    local_host=testhost
    local_user=testuser
    alt_scores=()
    alt_targets=()
    alt_sources=()
    alt_template_cmds=()
"""

REPORT_RESULTS = """
    echo "SIZE:${#alt_scores[@]}"
    echo "SCORES:${alt_scores[@]}"
    echo "TARGETS:${alt_targets[@]}"
    echo "SOURCES:${alt_sources[@]}"
"""


def test_dont_record_zeros(runner, yadm):
    """Record nothing if the score is zero"""

    script = f"""
        YADM_TEST=1 source {yadm}
        {INIT_VARS}
        record_score "0" "testtgt" "testsrc"
        {REPORT_RESULTS}
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert 'SIZE:0\n' in run.out
    assert 'SCORES:\n' in run.out
    assert 'TARGETS:\n' in run.out
    assert 'SOURCES:\n' in run.out


def test_new_scores(runner, yadm):
    """Test new scores"""

    script = f"""
        YADM_TEST=1 source {yadm}
        {INIT_VARS}
        record_score "1" "tgt_one"   "src_one"
        record_score "2" "tgt_two"   "src_two"
        record_score "4" "tgt_three" "src_three"
        {REPORT_RESULTS}
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert 'SIZE:3\n' in run.out
    assert 'SCORES:1 2 4\n' in run.out
    assert 'TARGETS:tgt_one tgt_two tgt_three\n' in run.out
    assert 'SOURCES:src_one src_two src_three\n' in run.out


@pytest.mark.parametrize('difference', ['lower', 'equal', 'higher'])
def test_existing_scores(runner, yadm, difference):
    """Test existing scores"""

    expected_score = '2'
    expected_src = 'existing_src'
    if difference == 'lower':
        score = '1'
    elif difference == 'equal':
        score = '2'
    else:
        score = '4'
        expected_score = '4'
        expected_src = 'new_src'

    script = f"""
        YADM_TEST=1 source {yadm}
        {INIT_VARS}
        alt_scores=(2)
        alt_targets=("testtgt")
        alt_sources=("existing_src")
        record_score "{score}" "testtgt" "new_src"
        {REPORT_RESULTS}
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert 'SIZE:1\n' in run.out
    assert f'SCORES:{expected_score}\n' in run.out
    assert 'TARGETS:testtgt\n' in run.out
    assert f'SOURCES:{expected_src}\n' in run.out


def test_existing_template(runner, yadm):
    """Record nothing if a template command is registered for this target"""

    script = f"""
        YADM_TEST=1 source {yadm}
        {INIT_VARS}
        alt_scores=(1)
        alt_targets=("testtgt")
        alt_sources=()
        alt_template_cmds=("existing_template")
        record_score "2" "testtgt" "new_src"
        {REPORT_RESULTS}
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert 'SIZE:1\n' in run.out
    assert 'SCORES:1\n' in run.out
    assert 'TARGETS:testtgt\n' in run.out
    assert 'SOURCES:\n' in run.out


def test_config_first(runner, yadm):
    """Verify YADM_CONFIG is always processed first"""

    config = 'yadm_config_file'
    script = f"""
        YADM_TEST=1 source {yadm}
        {INIT_VARS}
        YADM_CONFIG={config}
        record_score "1" "tgt_before" "src_before"
        record_template "tgt_tmp" "cmd_tmp" "src_tmp"
        record_score "2" "{config}"   "src_config"
        record_score "3" "tgt_after"  "src_after"
        {REPORT_RESULTS}
        echo "CMD_VALUE:${{alt_template_cmds[@]}}"
        echo "CMD_INDEX:${{!alt_template_cmds[@]}}"
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert 'SIZE:3\n' in run.out
    assert 'SCORES:2 1 3\n' in run.out
    assert f'TARGETS:{config} tgt_before tgt_tmp tgt_after\n' in run.out
    assert 'SOURCES:src_config src_before src_tmp src_after\n' in run.out
    assert 'CMD_VALUE:cmd_tmp\n' in run.out
    assert 'CMD_INDEX:2\n' in run.out
