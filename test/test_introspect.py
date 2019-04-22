"""Test introspect"""

import pytest


@pytest.mark.parametrize(
    'name', [
        '',
        'invalid',
        'commands',
        'configs',
        'repo',
        'switches',
    ])
def test_introspect_category(
        runner, yadm_y, paths, name,
        supported_commands, supported_configs, supported_switches):
    """Validate introspection category"""
    if name:
        run = runner(command=yadm_y('introspect', name))
    else:
        run = runner(command=yadm_y('introspect'))

    assert run.success
    assert run.err == ''

    expected = []
    if name == 'commands':
        expected = supported_commands
    elif name == 'config':
        expected = supported_configs
    elif name == 'switches':
        expected = supported_switches

    # assert values
    if name in ('', 'invalid'):
        assert run.out == ''
    if name == 'repo':
        assert run.out.rstrip() == paths.repo

    # make sure every expected value is present
    for value in expected:
        assert value in run.out
    # make sure nothing extra is present
    if expected:
        assert len(run.out.split()) == len(expected)
