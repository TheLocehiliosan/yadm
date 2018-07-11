"""Test alt"""

import os
import re
import string
import pytest
import utils

# These test IDs are broken. During the writing of these tests, problems have
# been discovered in the way yadm orders matching files.
BROKEN_TEST_IDS = [
    'test_wild[tracked-##C.S.H.U-C-S%-H%-U]',
    'test_wild[tracked-##C.S.H.U-C-S-H%-U]',
    'test_wild[encrypted-##C.S.H.U-C-S%-H%-U]',
    'test_wild[encrypted-##C.S.H.U-C-S-H%-U]',
    ]

PRECEDENCE = [
    '##',
    '##$tst_sys',
    '##$tst_sys.$tst_host',
    '##$tst_sys.$tst_host.$tst_user',
    '##$tst_class',
    '##$tst_class.$tst_sys',
    '##$tst_class.$tst_sys.$tst_host',
    '##$tst_class.$tst_sys.$tst_host.$tst_user',
    ]

WILD_TEMPLATES = [
    '##$tst_class',
    '##$tst_class.$tst_sys',
    '##$tst_class.$tst_sys.$tst_host',
    '##$tst_class.$tst_sys.$tst_host.$tst_user',
    ]

WILD_TESTED = set()


@pytest.mark.parametrize('precedence_index', range(len(PRECEDENCE)))
@pytest.mark.parametrize(
    'tracked, encrypt, exclude', [
        (False, False, False),
        (True, False, False),
        (False, True, False),
        (False, True, True),
    ], ids=[
        'untracked',
        'tracked',
        'encrypted',
        'excluded',
    ])
@pytest.mark.usefixtures('ds1_copy')
def test_alt(runner, yadm_y, paths,
             tst_sys, tst_host, tst_user,
             tracked, encrypt, exclude,
             precedence_index):
    """Test alternate linking

    This test is done by iterating for the number of templates in PRECEDENCE.
    With each iteration, another file is left off the list. So with each
    iteration, the template with the "highest precedence" is left out. The file
    using the highest precedence should be the one linked.
    """

    # set the class
    tst_class = 'testclass'
    utils.set_local(paths, 'class', tst_class)

    # process the templates in PRECEDENCE
    precedence = list()
    for template in PRECEDENCE:
        precedence.append(
            string.Template(template).substitute(
                tst_class=tst_class,
                tst_host=tst_host,
                tst_sys=tst_sys,
                tst_user=tst_user,
            )
        )

    # create files using a subset of files
    for suffix in precedence[0:precedence_index+1]:
        utils.create_alt_files(paths, suffix, tracked=tracked,
                               encrypt=encrypt, exclude=exclude)

    # run alt to trigger linking
    run = runner(yadm_y('alt'))
    assert run.success
    assert run.err == ''
    linked = linked_list(run.out)

    # assert the proper linking has occurred
    for file_path in (utils.ALT_FILE1, utils.ALT_FILE2):
        source_file = file_path + precedence[precedence_index]
        if tracked or (encrypt and not exclude):
            assert paths.work.join(file_path).islink()
            assert paths.work.join(file_path).read() == source_file
            assert str(paths.work.join(source_file)) in linked
        else:
            assert not paths.work.join(file_path).exists()
            assert str(paths.work.join(source_file)) not in linked


def short_template(template):
    """Translate template into something short for test IDs"""
    return string.Template(template).substitute(
        tst_class='C',
        tst_host='H',
        tst_sys='S',
        tst_user='U',
    )


@pytest.mark.parametrize('wild_user', [True, False], ids=['U%', 'U'])
@pytest.mark.parametrize('wild_host', [True, False], ids=['H%', 'H'])
@pytest.mark.parametrize('wild_sys', [True, False], ids=['S%', 'S'])
@pytest.mark.parametrize('wild_class', [True, False], ids=['C%', 'C'])
@pytest.mark.parametrize('template', WILD_TEMPLATES, ids=short_template)
@pytest.mark.parametrize(
    'tracked, encrypt', [
        (True, False),
        (False, True),
    ], ids=[
        'tracked',
        'encrypted',
    ])
@pytest.mark.usefixtures('ds1_copy')
def test_wild(request, runner, yadm_y, paths,
              tst_sys, tst_host, tst_user,
              tracked, encrypt,
              wild_class, wild_host, wild_sys, wild_user,
              template):
    """Test wild linking

    These tests are done by creating permutations of the possible files using
    WILD_TEMPLATES. Each case is then tested (while skipping the already tested
    permutations for efficiency).
    """

    if request.node.name in BROKEN_TEST_IDS:
        pytest.xfail(
            'This test is known to be broken. '
            'This bug needs to be fixed.')

    tst_class = 'testclass'

    # determine the "wild" version of the suffix
    str_class = '%' if wild_class else tst_class
    str_host = '%' if wild_host else tst_host
    str_sys = '%' if wild_sys else tst_sys
    str_user = '%' if wild_user else tst_user
    wild_suffix = string.Template(template).substitute(
        tst_class=str_class,
        tst_host=str_host,
        tst_sys=str_sys,
        tst_user=str_user,
    )

    # determine the "standard" version of the suffix
    std_suffix = string.Template(template).substitute(
        tst_class=tst_class,
        tst_host=tst_host,
        tst_sys=tst_sys,
        tst_user=tst_user,
    )

    # skip over duplicate tests (this seems to be the simplest way to cover the
    # permutations of tests, while skipping duplicates.)
    test_key = f'{tracked}{encrypt}{wild_suffix}{std_suffix}'
    if test_key in WILD_TESTED:
        return
    else:
        WILD_TESTED.add(test_key)

    # set the class
    utils.set_local(paths, 'class', tst_class)

    # create files using the wild suffix
    utils.create_alt_files(paths, wild_suffix, tracked=tracked,
                           encrypt=encrypt, exclude=False)

    # run alt to trigger linking
    run = runner(yadm_y('alt'))
    assert run.success
    assert run.err == ''
    linked = linked_list(run.out)

    # assert the proper linking has occurred
    for file_path in (utils.ALT_FILE1, utils.ALT_FILE2):
        source_file = file_path + wild_suffix
        assert paths.work.join(file_path).islink()
        assert paths.work.join(file_path).read() == source_file
        assert str(paths.work.join(source_file)) in linked

    # create files using the standard suffix
    utils.create_alt_files(paths, std_suffix, tracked=tracked,
                           encrypt=encrypt, exclude=False)

    # run alt to trigger linking
    run = runner(yadm_y('alt'))
    assert run.success
    assert run.err == ''
    linked = linked_list(run.out)

    # assert the proper linking has occurred
    for file_path in (utils.ALT_FILE1, utils.ALT_FILE2):
        source_file = file_path + std_suffix
        assert paths.work.join(file_path).islink()
        assert paths.work.join(file_path).read() == source_file
        assert str(paths.work.join(source_file)) in linked


@pytest.mark.usefixtures('ds1_copy')
def test_local_override(runner, yadm_y, paths,
                        tst_sys, tst_host, tst_user):
    """Test local overrides"""

    # define local overrides
    utils.set_local(paths, 'class', 'or-class')
    utils.set_local(paths, 'hostname', 'or-hostname')
    utils.set_local(paths, 'os', 'or-os')
    utils.set_local(paths, 'user', 'or-user')

    # create files, the first would normally be the most specific version
    # however, the second is the overridden version which should be preferred.
    utils.create_alt_files(
        paths, f'##or-class.{tst_sys}.{tst_host}.{tst_user}')
    utils.create_alt_files(
        paths, '##or-class.or-os.or-hostname.or-user')

    # run alt to trigger linking
    run = runner(yadm_y('alt'))
    assert run.success
    assert run.err == ''
    linked = linked_list(run.out)

    # assert the proper linking has occurred
    for file_path in (utils.ALT_FILE1, utils.ALT_FILE2):
        source_file = file_path + '##or-class.or-os.or-hostname.or-user'
        assert paths.work.join(file_path).islink()
        assert paths.work.join(file_path).read() == source_file
        assert str(paths.work.join(source_file)) in linked


@pytest.mark.parametrize('suffix', ['AAA', 'ZZZ', 'aaa', 'zzz'])
@pytest.mark.usefixtures('ds1_copy')
def test_class_case(runner, yadm_y, paths, tst_sys, suffix):
    """Test range of class cases"""

    # set the class
    utils.set_local(paths, 'class', suffix)

    # create files
    endings = [suffix]
    if tst_sys == 'Linux':
        # Only create all of these side-by-side on Linux, which is
        # unquestionably case-sensitive. This would break tests on
        # case-insensitive systems.
        endings = ['AAA', 'ZZZ', 'aaa', 'zzz']
    for ending in endings:
        utils.create_alt_files(paths, f'##{ending}')

    # run alt to trigger linking
    run = runner(yadm_y('alt'))
    assert run.success
    assert run.err == ''
    linked = linked_list(run.out)

    # assert the proper linking has occurred
    for file_path in (utils.ALT_FILE1, utils.ALT_FILE2):
        source_file = file_path + f'##{suffix}'
        assert paths.work.join(file_path).islink()
        assert paths.work.join(file_path).read() == source_file
        assert str(paths.work.join(source_file)) in linked


@pytest.mark.parametrize('autoalt', [None, 'true', 'false'])
@pytest.mark.usefixtures('ds1_copy')
def test_auto_alt(runner, yadm_y, paths, autoalt):
    """Test setting auto-alt"""

    # set the value of auto-alt
    if autoalt:
        os.system(' '.join(yadm_y('config', 'yadm.auto-alt', autoalt)))

    # create file
    suffix = '##'
    utils.create_alt_files(paths, suffix)

    # run status to possibly trigger linking
    run = runner(yadm_y('status'))
    assert run.success
    assert run.err == ''
    linked = linked_list(run.out)

    # assert the proper linking has occurred
    for file_path in (utils.ALT_FILE1, utils.ALT_FILE2):
        source_file = file_path + suffix
        if autoalt == 'false':
            assert not paths.work.join(file_path).exists()
        else:
            assert paths.work.join(file_path).islink()
            assert paths.work.join(file_path).read() == source_file
            # no linking output when run via auto-alt
            assert str(paths.work.join(source_file)) not in linked


@pytest.mark.parametrize('delimiter', ['.', '_'])
@pytest.mark.usefixtures('ds1_copy')
def test_delimiter(runner, yadm_y, paths,
                   tst_sys, tst_host, tst_user, delimiter):
    """Test delimiters used"""

    suffix = '##' + delimiter.join([tst_sys, tst_host, tst_user])

    # create file
    utils.create_alt_files(paths, suffix)

    # run alt to trigger linking
    run = runner(yadm_y('alt'))
    assert run.success
    assert run.err == ''
    linked = linked_list(run.out)

    # assert the proper linking has occurred
    # only a delimiter of '.' is valid
    for file_path in (utils.ALT_FILE1, utils.ALT_FILE2):
        source_file = file_path + suffix
        if delimiter == '.':
            assert paths.work.join(file_path).islink()
            assert paths.work.join(file_path).read() == source_file
            assert str(paths.work.join(source_file)) in linked
        else:
            assert not paths.work.join(file_path).exists()
            assert str(paths.work.join(source_file)) not in linked


def linked_list(output):
    """Parse output, and return list of linked files"""
    linked = dict()
    for line in output.splitlines():
        match = re.match('Linking (.+) to (.+)$', line)
        if match:
            linked[match.group(2)] = match.group(1)
    return linked.values()
