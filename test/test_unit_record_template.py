"""Unit tests: record_template"""

INIT_VARS = """
    alt_targets=()
    alt_template_cmds=()
    alt_sources=()
"""

REPORT_RESULTS = """
    echo "SIZE:${#alt_targets[@]}"
    echo "TARGETS:${alt_targets[@]}"
    echo "CMDS:${alt_template_cmds[@]}"
    echo "SOURCES:${alt_sources[@]}"
"""


def test_new_template(runner, yadm):
    """Test new template"""

    script = f"""
        YADM_TEST=1 source {yadm}
        {INIT_VARS}
        record_template "tgt_one"   "cmd_one"   "src_one"
        record_template "tgt_two"   "cmd_two"   "src_two"
        record_template "tgt_three" "cmd_three" "src_three"
        {REPORT_RESULTS}
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    assert "SIZE:3\n" in run.out
    assert "TARGETS:tgt_one tgt_two tgt_three\n" in run.out
    assert "CMDS:cmd_one cmd_two cmd_three\n" in run.out
    assert "SOURCES:src_one src_two src_three\n" in run.out


def test_existing_template(runner, yadm):
    """Overwrite existing templates"""

    script = f"""
        YADM_TEST=1 source {yadm}
        {INIT_VARS}
        alt_targets=("testtgt")
        alt_template_cmds=("existing_cmd")
        alt_sources=("existing_src")
        record_template "testtgt" "new_cmd" "new_src"
        {REPORT_RESULTS}
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    assert "SIZE:1\n" in run.out
    assert "TARGETS:testtgt\n" in run.out
    assert "CMDS:new_cmd\n" in run.out
    assert "SOURCES:new_src\n" in run.out
