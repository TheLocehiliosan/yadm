"""Unit tests: set_yadm_dirs"""
import pytest


@pytest.mark.parametrize(
    'condition', [
        'basic',
        'override',
        'override_data',
        'xdg_config_home',
        'xdg_data_home'
        ],
    )
def test_set_yadm_dirs(runner, yadm, condition):
    """Test set_yadm_dirs"""
    setup = ''
    if condition == 'override':
        setup = 'YADM_DIR=/override'
    elif condition == 'override_data':
        setup = 'YADM_DATA=/override'
    elif condition == 'xdg_config_home':
        setup = 'XDG_CONFIG_HOME=/xdg'
    elif condition == 'xdg_data_home':
        setup = 'XDG_DATA_HOME=/xdg'
    script = f"""
        HOME=/testhome
        YADM_TEST=1 source {yadm}
        XDG_CONFIG_HOME=
        XDG_DATA_HOME=
        {setup}
        set_yadm_dirs
        echo "YADM_DIR=$YADM_DIR"
        echo "YADM_DATA=$YADM_DATA"
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    if condition == 'basic':
        assert 'YADM_DIR=/testhome/.config/yadm' in run.out
        assert 'YADM_DATA=/testhome/.local/share/yadm' in run.out
    elif condition == 'override':
        assert 'YADM_DIR=/override' in run.out
    elif condition == 'override_data':
        assert 'YADM_DATA=/override' in run.out
    elif condition == 'xdg_config_home':
        assert 'YADM_DIR=/xdg/yadm' in run.out
    elif condition == 'xdg_data_home':
        assert 'YADM_DATA=/xdg/yadm' in run.out
