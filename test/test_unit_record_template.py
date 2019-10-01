"""Unit tests: record_template"""

INIT_VARS = """
    alt_filenames=()
    alt_template_cmds=()
    alt_targets=()
"""

REPORT_RESULTS = """
    echo "SIZE:${#alt_filenames[@]}"
    echo "FILENAMES:${alt_filenames[@]}"
    echo "CMDS:${alt_template_cmds[@]}"
    echo "TARGS:${alt_targets[@]}"
"""


def test_new_template(runner, yadm):
    """Test new template"""

    script = f"""
        YADM_TEST=1 source {yadm}
        {INIT_VARS}
        record_template "file_one"   "cmd_one"   "targ_one"
        record_template "file_two"   "cmd_two"   "targ_two"
        record_template "file_three" "cmd_three" "targ_three"
        {REPORT_RESULTS}
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert 'SIZE:3\n' in run.out
    assert 'FILENAMES:file_one file_two file_three\n' in run.out
    assert 'CMDS:cmd_one cmd_two cmd_three\n' in run.out
    assert 'TARGS:targ_one targ_two targ_three\n' in run.out


def test_existing_template(runner, yadm):
    """Overwrite existing templates"""

    script = f"""
        YADM_TEST=1 source {yadm}
        {INIT_VARS}
        alt_filenames=("testfile")
        alt_template_cmds=("existing_cmd")
        alt_targets=("existing_targ")
        record_template "testfile" "new_cmd" "new_targ"
        {REPORT_RESULTS}
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert 'SIZE:1\n' in run.out
    assert 'FILENAMES:testfile\n' in run.out
    assert 'CMDS:new_cmd\n' in run.out
    assert 'TARGS:new_targ\n' in run.out
