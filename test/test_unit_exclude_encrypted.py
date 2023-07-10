"""Unit tests: exclude_encrypted"""
import pytest


@pytest.mark.parametrize("exclude", ["missing", "outdated", "up-to-date"])
@pytest.mark.parametrize("encrypt_exists", [True, False], ids=["encrypt", "no-encrypt"])
@pytest.mark.parametrize("auto_exclude", [True, False], ids=["enabled", "disabled"])
def test_exclude_encrypted(runner, tmpdir, yadm, encrypt_exists, auto_exclude, exclude):
    """Test exclude_encrypted()"""

    header = "# yadm-auto-excludes\n# This section is managed by yadm.\n# Any edits below will be lost.\n"

    config_function = 'function config() { echo "false";}'
    if auto_exclude:
        config_function = "function config() { return; }"

    encrypt_file = tmpdir.join("encrypt_file")
    repo_dir = tmpdir.join("repodir")
    exclude_file = repo_dir.join("info/exclude")

    if encrypt_exists:
        encrypt_file.write("test-encrypt-data\n", ensure=True)
    if exclude == "outdated":
        exclude_file.write(f"original-exclude\n{header}outdated\n", ensure=True)
    elif exclude == "up-to-date":
        exclude_file.write(f"original-exclude\n{header}test-encrypt-data\n", ensure=True)

    script = f"""
        YADM_TEST=1 source {yadm}
        {config_function}
        DEBUG=1
        YADM_ENCRYPT="{encrypt_file}"
        YADM_REPO="{repo_dir}"
        exclude_encrypted
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""

    if auto_exclude:
        if encrypt_exists:
            assert exclude_file.exists()
            if exclude == "missing":
                assert exclude_file.read() == f"{header}test-encrypt-data\n"
            else:
                assert exclude_file.read() == ("original-exclude\n" f"{header}test-encrypt-data\n")
            if exclude != "up-to-date":
                assert f"Updating {exclude_file}" in run.out
            else:
                assert run.out == ""
        else:
            assert run.out == ""
    else:
        assert run.out == ""
