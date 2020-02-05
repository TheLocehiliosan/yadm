"""Unit tests: set_yadm_dir"""
import pytest


@pytest.mark.parametrize(
    'condition',
    ['basic', 'override', 'xdg_config_home', 'legacy'],
    )
def test_set_yadm_dir(runner, yadm, condition):
    """Test set_yadm_dir"""
    setup = ''
    if condition == 'override':
        setup = 'YADM_DIR=/override'
    elif condition == 'xdg_config_home':
        setup = 'XDG_CONFIG_HOME=/xdg'
    elif condition == 'legacy':
        setup = 'YADM_COMPATIBILITY=1'
    script = f"""
        HOME=/testhome
        YADM_TEST=1 source {yadm}
        {setup}
        set_yadm_dir
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
    elif condition == 'legacy':
        assert run.out.rstrip() == '/testhome/.yadm'
