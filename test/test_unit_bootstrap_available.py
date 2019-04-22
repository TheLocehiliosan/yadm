"""Unit tests: bootstrap_available"""


def test_bootstrap_missing(runner, paths):
    """Test result of bootstrap_available, when bootstrap missing"""
    run_test(runner, paths, False)


def test_bootstrap_no_exec(runner, paths):
    """Test result of bootstrap_available, when bootstrap not executable"""
    paths.bootstrap.write('')
    paths.bootstrap.chmod(0o644)
    run_test(runner, paths, False)


def test_bootstrap_exec(runner, paths):
    """Test result of bootstrap_available, when bootstrap executable"""
    paths.bootstrap.write('')
    paths.bootstrap.chmod(0o775)
    run_test(runner, paths, True)


def run_test(runner, paths, success):
    """Run bootstrap_available, and test result"""
    script = f"""
        YADM_TEST=1 source {paths.pgm}
        YADM_BOOTSTRAP='{paths.bootstrap}'
        bootstrap_available
    """
    run = runner(command=['bash'], inp=script)
    assert run.success == success
    assert run.err == ''
    assert run.out == ''
