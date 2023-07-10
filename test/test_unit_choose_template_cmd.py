"""Unit tests: choose_template_cmd"""
import pytest


@pytest.mark.parametrize("label", ["", "default", "other"])
@pytest.mark.parametrize("awk", [True, False], ids=["awk", "no-awk"])
def test_kind_default(runner, yadm, awk, label):
    """Test kind: default"""

    expected = "template_default"
    awk_avail = "true"

    if not awk:
        awk_avail = "false"
        expected = ""

    if label == "other":
        expected = ""

    script = f"""
        YADM_TEST=1 source {yadm}
        function awk_available {{ { awk_avail}; }}
        template="$(choose_template_cmd "{label}")"
        echo "TEMPLATE:$template"
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    assert f"TEMPLATE:{expected}\n" in run.out


@pytest.mark.parametrize("label", ["envtpl", "j2cli", "j2", "other"])
@pytest.mark.parametrize("envtpl", [True, False], ids=["envtpl", "no-envtpl"])
@pytest.mark.parametrize("j2cli", [True, False], ids=["j2cli", "no-j2cli"])
def test_kind_j2cli_envtpl(runner, yadm, envtpl, j2cli, label):
    """Test kind: j2 (both j2cli & envtpl)

    j2cli is preferred over envtpl if available.
    """

    envtpl_avail = "true" if envtpl else "false"
    j2cli_avail = "true" if j2cli else "false"

    if label in ("j2cli", "j2") and j2cli:
        expected = "template_j2cli"
    elif label in ("envtpl", "j2") and envtpl:
        expected = "template_envtpl"
    else:
        expected = ""

    script = f"""
        YADM_TEST=1 source {yadm}
        function envtpl_available {{ { envtpl_avail}; }}
        function j2cli_available {{ { j2cli_avail}; }}
        template="$(choose_template_cmd "{label}")"
        echo "TEMPLATE:$template"
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    assert f"TEMPLATE:{expected}\n" in run.out
