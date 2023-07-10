"""Unit tests: configure_paths"""

import pytest

ARCHIVE = "archive"
BOOTSTRAP = "bootstrap"
CONFIG = "config"
ENCRYPT = "encrypt"
HOME = "/testhome"
REPO = "repo.git"
YDIR = ".config/yadm"
YDATA = ".local/share/yadm"


@pytest.mark.parametrize(
    "override, expect",
    [
        (None, {}),
        ("-Y", {"yadm": "YADM_DIR"}),
        ("--yadm-data", {"data": "YADM_DATA"}),
        ("--yadm-repo", {"repo": "YADM_REPO", "git": "GIT_DIR"}),
        ("--yadm-config", {"config": "YADM_CONFIG"}),
        ("--yadm-encrypt", {"encrypt": "YADM_ENCRYPT"}),
        ("--yadm-archive", {"archive": "YADM_ARCHIVE"}),
        ("--yadm-bootstrap", {"bootstrap": "YADM_BOOTSTRAP"}),
    ],
    ids=[
        "default",
        "override yadm dir",
        "override yadm data",
        "override repo",
        "override config",
        "override encrypt",
        "override archive",
        "override bootstrap",
    ],
)
@pytest.mark.parametrize(
    "path",
    [".", "./override", "override", ".override", "/override"],
    ids=["cwd", "./relative", "relative", "hidden relative", "absolute"],
)
def test_config(runner, paths, override, expect, path):
    """Test configure_paths"""
    if path.startswith("/"):
        expected_path = path
    else:
        expected_path = str(paths.root.join(path))

    args = [override, path] if override else []

    if override == "-Y":
        matches = match_map(expected_path)
    elif override == "--yadm-data":
        matches = match_map(None, expected_path)
    else:
        matches = match_map()

    for ekey in expect.keys():
        matches[ekey] = f'{expect[ekey]}="{expected_path}"'

    run_test(runner, paths, args, matches.values(), cwd=str(paths.root))


def match_map(yadm_dir=None, yadm_data=None):
    """Create a dictionary of matches, relative to yadm_dir"""
    if not yadm_dir:
        yadm_dir = "/".join([HOME, YDIR])
    if not yadm_data:
        yadm_data = "/".join([HOME, YDATA])
    return {
        "yadm": f'YADM_DIR="{yadm_dir}"',
        "repo": f'YADM_REPO="{yadm_data}/{REPO}"',
        "config": f'YADM_CONFIG="{yadm_dir}/{CONFIG}"',
        "encrypt": f'YADM_ENCRYPT="{yadm_dir}/{ENCRYPT}"',
        "archive": f'YADM_ARCHIVE="{yadm_data}/{ARCHIVE}"',
        "bootstrap": f'YADM_BOOTSTRAP="{yadm_dir}/{BOOTSTRAP}"',
        "git": f'GIT_DIR="{yadm_data}/{REPO}"',
    }


def run_test(runner, paths, args, expected_matches, cwd=None):
    """Run proces global args, and run configure_paths"""
    argstring = " ".join(['"' + a + '"' for a in args])
    script = f"""
        YADM_TEST=1 HOME="{HOME}" source {paths.pgm}
        process_global_args {argstring}
        XDG_CONFIG_HOME=
        XDG_DATA_HOME=
        HOME="{HOME}" set_yadm_dirs
        configure_paths
        declare -p | grep -E '(YADM|GIT)_'
    """
    run = runner(command=["bash"], inp=script, cwd=cwd)
    assert run.success
    assert run.err == ""
    for match in expected_matches:
        assert match in run.out
