"""Test yadm.alt-copy"""

import os
import pytest


@pytest.mark.parametrize(
    'cygwin',
    [pytest.param(True, marks=pytest.mark.deprecated), False],
    ids=['cygwin', 'no-cygwin'])
@pytest.mark.parametrize(
    'compatibility', [True, False], ids=['compat', 'no-compat'])
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
        runner, yadm_y, paths, tst_sys,
        setting, expect_link, pre_existing,
        compatibility, cygwin):
    """Test yadm.alt-copy"""

    option = 'yadm.cygwin-copy' if cygwin else 'yadm.alt-copy'

    if setting is not None:
        os.system(' '.join(yadm_y('config', option, str(setting))))

    if compatibility:
        expected_content = f'test_alt_copy##{tst_sys}'
    else:
        expected_content = f'test_alt_copy##os.{tst_sys}'

    alt_path = paths.work.join('test_alt_copy')
    if pre_existing == 'symlink':
        alt_path.mklinkto(expected_content)
    elif pre_existing == 'file':
        alt_path.write('wrong content')

    env = os.environ.copy()
    if compatibility:
        env['YADM_COMPATIBILITY'] = '1'

    run = runner(yadm_y('alt'), env=env)
    assert run.success
    assert run.err == ''
    assert 'Linking' in run.out

    assert alt_path.read() == expected_content
    assert alt_path.islink() == expect_link
