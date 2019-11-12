"""Test hooks"""

import pytest


@pytest.mark.parametrize(
    'pre, pre_code, post, post_code', [
        (False, 0, False, 0),
        (True, 0, False, 0),
        (True, 5, False, 0),
        (False, 0, True, 0),
        (False, 0, True, 5),
        (True, 0, True, 0),
        (True, 5, True, 5),
    ], ids=[
        'no-hooks',
        'pre-success',
        'pre-fail',
        'post-success',
        'post-fail',
        'pre-post-success',
        'pre-post-fail',
    ])
def test_hooks(
        runner, yadm_y, paths,
        pre, pre_code, post, post_code):
    """Test pre/post hook"""

    # generate hooks
    if pre:
        create_hook(paths, 'pre_version', pre_code)
    if post:
        create_hook(paths, 'post_version', post_code)

    # run yadm
    run = runner(yadm_y('version'))
    # when a pre hook fails, yadm should exit with the hook's code
    assert run.code == pre_code
    assert run.err == ''

    if pre:
        assert 'HOOK:pre_version' in run.out
    # if pre hook is missing or successful, yadm itself should exit 0
    if run.success:
        if post:
            assert 'HOOK:post_version' in run.out
    else:
        # when a pre hook fails, yadm should not run the command
        assert 'version will not be run' in run.out
        # when a pre hook fails, yadm should not run the post hook
        assert 'HOOK:post_version' not in run.out


# repo fixture is needed to test the population of YADM_HOOK_WORK
@pytest.mark.usefixtures('ds1_repo_copy')
def test_hook_env(runner, yadm_y, paths):
    """Test hook environment"""

    # test will be done with a non existent "git" passthru command
    # which should exit with a failing code
    cmd = 'passthrucmd'

    # write the hook
    hook = paths.hooks.join(f'post_{cmd}')
    hook.write('#!/bin/sh\nenv\n')
    hook.chmod(0o755)

    run = runner(yadm_y(cmd, 'extra_args'))

    # expect passthru to fail
    assert run.failure
    assert f"'{cmd}' is not a git command" in run.err

    # verify hook environment
    assert 'YADM_HOOK_EXIT=1\n' in run.out
    assert f'YADM_HOOK_COMMAND={cmd}\n' in run.out
    assert f'YADM_HOOK_FULL_COMMAND={cmd} extra_args\n' in run.out
    assert f'YADM_HOOK_REPO={paths.repo}\n' in run.out
    assert f'YADM_HOOK_WORK={paths.work}\n' in run.out


def create_hook(paths, name, code):
    """Create hook"""
    hook = paths.hooks.join(name)
    hook.write(
        '#!/bin/sh\n'
        f'echo HOOK:{name}\n'
        f'exit {code}\n'
    )
    hook.chmod(0o755)
