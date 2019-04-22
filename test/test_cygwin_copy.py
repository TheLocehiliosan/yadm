"""Test yadm.cygwin_copy"""

import os
import pytest


@pytest.mark.parametrize(
    'setting, is_cygwin, expect_link, pre_existing', [
        (None, False, True, None),
        (True, False, True, None),
        (False, False, True, None),
        (None, True, True, None),
        (True, True, False, None),
        (False, True, True, None),
        (True, True, False, 'link'),
        (True, True, False, 'file'),
    ],
    ids=[
        'unset, non-cygwin',
        'true, non-cygwin',
        'false, non-cygwin',
        'unset, cygwin',
        'true, cygwin',
        'false, cygwin',
        'pre-existing symlink',
        'pre-existing file',
    ])
@pytest.mark.usefixtures('ds1_copy')
def test_cygwin_copy(
        runner, yadm_y, paths, cygwin_sys, tst_sys,
        setting, is_cygwin, expect_link, pre_existing):
    """Test yadm.cygwin_copy"""

    if setting is not None:
        os.system(' '.join(yadm_y('config', 'yadm.cygwin-copy', str(setting))))

    expected_content = f'test_cygwin_copy##{tst_sys}'
    alt_path = paths.work.join('test_cygwin_copy')
    if pre_existing == 'symlink':
        alt_path.mklinkto(expected_content)
    elif pre_existing == 'file':
        alt_path.write('wrong content')

    uname_path = paths.root.join('tmp').mkdir()
    if is_cygwin:
        uname = uname_path.join('uname')
        uname.write(f'#!/bin/sh\necho "{cygwin_sys}"\n')
        uname.chmod(0o777)
        expected_content = f'test_cygwin_copy##{cygwin_sys}'
    env = os.environ.copy()
    env['PATH'] = ':'.join([str(uname_path), env['PATH']])

    run = runner(yadm_y('alt'), env=env)
    assert run.success
    assert run.err == ''
    assert 'Linking' in run.out

    assert alt_path.read() == expected_content
    assert alt_path.islink() == expect_link
