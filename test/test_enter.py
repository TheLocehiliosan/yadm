"""Test enter"""

import os

import pytest


@pytest.mark.parametrize(
    'shell, success', [
        ('delete', True),  # if there is no shell variable, bash creates it
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
def test_enter(runner, yadm_cmd, paths, shell, success):
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

    run = runner(command=yadm_cmd('enter'), env=env)
    assert run.success == success
    prompt = f'yadm shell ({paths.repo})'
    if success:
        assert run.out.startswith('Entering yadm repo')
        assert run.out.rstrip().endswith('Leaving yadm repo')
        assert run.err == ''
    else:
        assert 'does not refer to an executable' in run.err
    if 'env' in shell:
        assert f'GIT_DIR={paths.repo}' in run.out
        assert f'GIT_WORK_TREE={paths.work}' in run.out
        assert f'PROMPT={prompt}' in run.out
        assert f'PS1={prompt}' in run.out


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
@pytest.mark.parametrize(
    'cmd',
    [False, 'cmd', 'cmd-bad-exit'],
    ids=['no-cmd', 'cmd', 'cmd-bad-exit'])
@pytest.mark.parametrize(
    'term', ['', 'dumb'],
    ids=['term-empty', 'term-dumb'])
@pytest.mark.usefixtures('ds1_copy')
def test_enter_shell_ops(runner, yadm_cmd, paths, shell,
                         opts, path, cmd, term):
    """Enter tests for specific shell options"""

    change_exit = '\nfalse' if cmd == 'cmd-bad-exit' else ''

    # Create custom shell to detect options passed
    custom_shell = paths.root.join(shell)
    custom_shell.write(
        f'#!/bin/sh\necho OPTS=$*\necho PROMPT=$PROMPT{change_exit}'
    )
    custom_shell.chmod(0o775)

    test_cmd = ['test1', 'test2', 'test3']

    enter_cmd = ['enter']
    if cmd:
        enter_cmd += test_cmd

    env = os.environ.copy()
    env['TERM'] = term
    env['SHELL'] = custom_shell

    if shell == 'zsh' and term == 'dumb':
        opts += ' --no-zle'

    run = runner(command=yadm_cmd(*enter_cmd), env=env)
    if cmd == 'cmd-bad-exit':
        assert run.failure
    else:
        assert run.success
    assert run.err == ''
    assert f'OPTS={opts}' in run.out
    assert f'PROMPT=yadm shell ({paths.repo}) {path} >' in run.out
    if cmd:
        assert '-c ' + ' '.join(test_cmd) in run.out
        assert 'Entering yadm repo' not in run.out
        assert 'Leaving yadm repo' not in run.out
    else:
        assert 'Entering yadm repo' in run.out
        assert 'Leaving yadm repo' in run.out
