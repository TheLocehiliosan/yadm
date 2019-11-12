"""Test bootstrap"""

import pytest


@pytest.mark.parametrize(
    'exists, executable, code, expect', [
        (False, False, 1, 'Cannot execute bootstrap'),
        (True, False, 1, 'is not an executable program'),
        (True, True, 123, 'Bootstrap successful'),
    ], ids=[
        'missing',
        'not executable',
        'executable',
    ])
def test_bootstrap(
        runner, yadm_y, paths, exists, executable, code, expect):
    """Test bootstrap command"""
    if exists:
        paths.bootstrap.write('')
    if executable:
        paths.bootstrap.write(
            '#!/bin/bash\n'
            f'echo {expect}\n'
            f'exit {code}\n'
        )
        paths.bootstrap.chmod(0o775)
    run = runner(command=yadm_y('bootstrap'))
    assert run.code == code
    assert run.err == ''
    assert expect in run.out
