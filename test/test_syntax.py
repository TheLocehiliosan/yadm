"""Syntax checks"""

import os

import pytest


def test_yadm_syntax(runner, yadm):
    """Is syntactically valid"""
    run = runner(command=['bash', '-n', yadm])
    assert run.success


def test_shellcheck(pytestconfig, runner, yadm, shellcheck_version):
    """Passes shellcheck"""
    if not pytestconfig.getoption("--force-linters"):
        run = runner(command=['shellcheck', '-V'], report=False)
        if f'version: {shellcheck_version}' not in run.out:
            pytest.skip('Unsupported shellcheck version')
    run = runner(command=['shellcheck', '-s', 'bash', yadm])
    assert run.success


def test_pylint(pytestconfig, runner, pylint_version):
    """Passes pylint"""
    if not pytestconfig.getoption("--force-linters"):
        run = runner(command=['pylint', '--version'], report=False)
        if f'pylint {pylint_version}' not in run.out:
            pytest.skip('Unsupported pylint version')
    pyfiles = []
    for tfile in os.listdir('test'):
        if tfile.endswith('.py'):
            pyfiles.append(f'test/{tfile}')
    run = runner(command=['pylint'] + pyfiles)
    assert run.success


def test_isort(pytestconfig, runner, isort_version):
    """Passes isort"""
    if not pytestconfig.getoption("--force-linters"):
        run = runner(command=['isort', '--version'], report=False)
        if isort_version not in run.out:
            pytest.skip('Unsupported isort version')
    run = runner(command=['isort', '-c', 'test'])
    assert run.success


def test_flake8(pytestconfig, runner, flake8_version):
    """Passes flake8"""
    if not pytestconfig.getoption("--force-linters"):
        run = runner(command=['flake8', '--version'], report=False)
        if not run.out.startswith(flake8_version):
            pytest.skip('Unsupported flake8 version')
    run = runner(command=['flake8', 'test'])
    assert run.success


def test_yamllint(pytestconfig, runner, yamllint_version):
    """Passes yamllint"""
    if not pytestconfig.getoption("--force-linters"):
        run = runner(command=['yamllint', '--version'], report=False)
        if not run.out.strip().endswith(yamllint_version):
            pytest.skip('Unsupported yamllint version')
    run = runner(
        command=['yamllint', '-s', '$(find . -name \\*.yml)'],
        shell=True)
    assert run.success


def test_man(runner):
    """Check for warnings from man"""
    run = runner(
        command=['man.REAL', '--warnings', './yadm.1'])
    assert run.success
    assert run.err == ''
    assert 'yadm - Yet Another Dotfiles Manager' in run.out
