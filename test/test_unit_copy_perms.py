"""Unit tests: copy_perms"""
import os
import pytest

OCTAL = '7654'
NON_OCTAL = '9876'


@pytest.mark.parametrize(
    'stat_broken', [True, False], ids=['normal', 'stat broken'])
def test_copy_perms(runner, yadm, tmpdir, stat_broken):
    """Test function copy_perms"""
    src_mode = 0o754
    dst_mode = 0o644
    source = tmpdir.join('source')
    source.write('test', ensure=True)
    source.chmod(src_mode)

    dest = tmpdir.join('dest')
    dest.write('test', ensure=True)
    dest.chmod(dst_mode)

    override_stat = ''
    if stat_broken:
        override_stat = 'function stat() { echo broken; }'
    script = f"""
        YADM_TEST=1 source {yadm}
        {override_stat}
        copy_perms "{source}" "{dest}"
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert run.out == ''
    expected = dst_mode if stat_broken else src_mode
    assert oct(os.stat(dest).st_mode)[-3:] == oct(expected)[-3:]


@pytest.mark.parametrize(
    'stat_output', [OCTAL, NON_OCTAL], ids=['octal', 'non-octal'])
def test_get_mode(runner, yadm, stat_output):
    """Test function get_mode"""
    script = f"""
        YADM_TEST=1 source {yadm}
        function stat() {{ echo {stat_output}; }}
        mode=$(get_mode abc)
        echo "MODE:$mode"
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    expected = OCTAL if stat_output == OCTAL else ""
    assert f'MODE:{expected}\n' in run.out
