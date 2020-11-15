"""Unit tests: set_yadm_dirs"""
import pytest


@pytest.mark.parametrize(
    'condition',
    ['basic', 'override', 'xdg_config_home'],
    )
def test_set_yadm_dirs(runner, yadm, condition):
    """Test set_yadm_dirs"""
    setup = ''
    if condition == 'override':
        setup = 'YADM_DIR=/override'
    elif condition == 'xdg_config_home':
        setup = 'XDG_CONFIG_HOME=/xdg'
    script = f"""
        HOME=/testhome
        YADM_TEST=1 source {yadm}
        {setup}
        set_yadm_dirs
        echo "$YADM_DIR"
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    if condition == 'basic':
        assert run.out.rstrip() == '/testhome/.config/yadm'
    elif condition == 'override':
        assert run.out.rstrip() == '/override'
    elif condition == 'xdg_config_home':
        assert run.out.rstrip() == '/xdg/yadm'
