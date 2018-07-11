"""Syntax checks"""

import os
import pytest


def test_yadm_syntax(runner, yadm):
    """Is syntactically valid"""
    run = runner(command=['bash', '-n', yadm])
    assert run.success


def test_shellcheck(runner, yadm, shellcheck_version):
    """Passes shellcheck"""
    run = runner(command=['shellcheck', '-V'], report=False)
    if f'version: {shellcheck_version}' not in run.out:
        pytest.skip('Unsupported shellcheck version')
    run = runner(command=['shellcheck', '-s', 'bash', yadm])
    assert run.success


def test_pylint(runner, pylint_version):
    """Passes pylint"""
    run = runner(command=['pylint', '--version'], report=False)
    if f'pylint {pylint_version}' not in run.out:
        pytest.skip('Unsupported pylint version')
    pyfiles = list()
    for tfile in os.listdir('test'):
        if tfile.endswith('.py'):
            pyfiles.append(f'test/{tfile}')
    run = runner(command=['pylint'] + pyfiles)
    assert run.success


def test_flake8(runner, flake8_version):
    """Passes flake8"""
    run = runner(command=['flake8', '--version'], report=False)
    if not run.out.startswith(flake8_version):
        pytest.skip('Unsupported flake8 version')
    run = runner(command=['flake8', 'test'])
    assert run.success
