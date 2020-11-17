"""Test yadm.alt-copy"""

import os
import pytest


@pytest.mark.parametrize(
    'cygwin',
    [pytest.param(True, marks=pytest.mark.deprecated), False],
    ids=['cygwin', 'no-cygwin'])
@pytest.mark.parametrize(
    'setting, expect_link, pre_existing', [
        (None, True, None),
        (True, False, None),
        (False, True, None),
        (True, False, 'link'),
        (True, False, 'file'),
    ],
    ids=[
        'unset',
        'true',
        'false',
        'pre-existing symlink',
        'pre-existing file',
    ])
@pytest.mark.usefixtures('ds1_copy')
def test_alt_copy(
        runner, yadm_cmd, paths, tst_sys,
        setting, expect_link, pre_existing,
        cygwin):
    """Test yadm.alt-copy"""

    option = 'yadm.cygwin-copy' if cygwin else 'yadm.alt-copy'

    if setting is not None:
        os.system(' '.join(yadm_cmd('config', option, str(setting))))

    expected_content = f'test_alt_copy##os.{tst_sys}'

    alt_path = paths.work.join('test_alt_copy')
    if pre_existing == 'symlink':
        alt_path.mklinkto(expected_content)
    elif pre_existing == 'file':
        alt_path.write('wrong content')

    run = runner(yadm_cmd('alt'))
    assert run.success
    assert run.err == ''
    assert 'Linking' in run.out

    assert alt_path.read() == expected_content
    assert alt_path.islink() == expect_link
