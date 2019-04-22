"""Test enter"""

import os
import warnings
import pytest


@pytest.mark.parametrize(
    'shell, success', [
        ('delete', True),
        ('', False),
        ('/usr/bin/env', True),
        ('noexec', False),
    ], ids=[
        'shell-missing',
        'shell-empty',
        'shell-env',
        'shell-noexec',
    ])
@pytest.mark.usefixtures('ds1_copy')
def test_enter(runner, yadm_y, paths, shell, success):
    """Enter tests"""
    env = os.environ.copy()
    if shell == 'delete':
        # remove shell
        if 'SHELL' in env:
            del env['SHELL']
    elif shell == 'noexec':
        # specify a non-executable path
        noexec = paths.root.join('noexec')
        noexec.write('')
        noexec.chmod(0o664)
        env['SHELL'] = str(noexec)
    else:
        env['SHELL'] = shell
    run = runner(command=yadm_y('enter'), env=env)
    assert run.success == success
    assert run.err == ''
    prompt = f'yadm shell ({paths.repo})'
    if success:
        assert run.out.startswith('Entering yadm repo')
        assert run.out.rstrip().endswith('Leaving yadm repo')
        if shell == 'delete':
            # When SHELL is empty (unlikely), it is attempted to be run anyway.
            # This is a but which must be fixed.
            warnings.warn('Unhandled bug: SHELL executed when empty', Warning)
        else:
            assert f'PROMPT={prompt}' in run.out
            assert f'PS1={prompt}' in run.out
            assert f'GIT_DIR={paths.repo}' in run.out
    if not success:
        assert 'does not refer to an executable' in run.out
    if 'env' in shell:
        assert f'GIT_DIR={paths.repo}' in run.out
        assert 'PROMPT=yadm shell' in run.out
        assert 'PS1=yadm shell' in run.out


@pytest.mark.parametrize(
    'shell, opts, path', [
        ('bash', '--norc', '\\w'),
        ('csh', '-f', '%~'),
        ('zsh', '-f', '%~'),
    ], ids=[
        'bash',
        'csh',
        'zsh',
    ])
@pytest.mark.usefixtures('ds1_copy')
def test_enter_shell_ops(runner, yadm_y, paths, shell, opts, path):
    """Enter tests for specific shell options"""

    # Create custom shell to detect options passed
    custom_shell = paths.root.join(shell)
    custom_shell.write('#!/bin/sh\necho OPTS=$*\necho PROMPT=$PROMPT')
    custom_shell.chmod(0o775)

    env = os.environ.copy()
    env['SHELL'] = custom_shell

    run = runner(command=yadm_y('enter'), env=env)
    assert run.success
    assert run.err == ''
    assert f'OPTS={opts}' in run.out
    assert f'PROMPT=yadm shell ({paths.repo}) {path} >' in run.out
