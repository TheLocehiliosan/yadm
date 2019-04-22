"""Unit tests: configure_paths"""

import pytest

ARCHIVE = 'files.gpg'
BOOTSTRAP = 'bootstrap'
CONFIG = 'config'
ENCRYPT = 'encrypt'
HOME = '/testhome'
REPO = 'repo.git'
YDIR = '.yadm'


@pytest.mark.parametrize(
    'override, expect', [
        (None, {}),
        ('-Y', {}),
        ('--yadm-repo', {'repo': 'YADM_REPO', 'git': 'GIT_DIR'}),
        ('--yadm-config', {'config': 'YADM_CONFIG'}),
        ('--yadm-encrypt', {'encrypt': 'YADM_ENCRYPT'}),
        ('--yadm-archive', {'archive': 'YADM_ARCHIVE'}),
        ('--yadm-bootstrap', {'bootstrap': 'YADM_BOOTSTRAP'}),
    ], ids=[
        'default',
        'override yadm dir',
        'override repo',
        'override config',
        'override encrypt',
        'override archive',
        'override bootstrap',
    ])
def test_config(runner, paths, override, expect):
    """Test configure_paths"""
    opath = 'override'
    matches = match_map()
    args = []
    if override == '-Y':
        matches = match_map('/' + opath)

    if override:
        args = [override, '/' + opath]
        for ekey in expect.keys():
            matches[ekey] = f'{expect[ekey]}="/{opath}"'
        run_test(
            runner, paths,
            [override, opath],
            ['must specify a fully qualified'], 1)

    run_test(runner, paths, args, matches.values(), 0)


def match_map(yadm_dir=None):
    """Create a dictionary of matches, relative to yadm_dir"""
    if not yadm_dir:
        yadm_dir = '/'.join([HOME, YDIR])
    return {
        'yadm': f'YADM_DIR="{yadm_dir}"',
        'repo': f'YADM_REPO="{yadm_dir}/{REPO}"',
        'config': f'YADM_CONFIG="{yadm_dir}/{CONFIG}"',
        'encrypt': f'YADM_ENCRYPT="{yadm_dir}/{ENCRYPT}"',
        'archive': f'YADM_ARCHIVE="{yadm_dir}/{ARCHIVE}"',
        'bootstrap': f'YADM_BOOTSTRAP="{yadm_dir}/{BOOTSTRAP}"',
        'git': f'GIT_DIR="{yadm_dir}/{REPO}"',
        }


def run_test(runner, paths, args, expected_matches, expected_code=0):
    """Run proces global args, and run configure_paths"""
    argstring = ' '.join(['"'+a+'"' for a in args])
    script = f"""
        YADM_TEST=1 HOME="{HOME}" source {paths.pgm}
        process_global_args {argstring}
        configure_paths
        declare -p | grep -E '(YADM|GIT)_'
    """
    run = runner(command=['bash'], inp=script)
    assert run.code == expected_code
    assert run.err == ''
    for match in expected_matches:
        assert match in run.out
