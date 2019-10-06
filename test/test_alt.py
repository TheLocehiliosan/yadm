"""Test alt"""
import os
import string
import py
import pytest
import utils

TEST_PATHS = [utils.ALT_FILE1, utils.ALT_FILE2, utils.ALT_DIR]


@pytest.mark.usefixtures('ds1_copy')
@pytest.mark.parametrize(
    'tracked,encrypt,exclude', [
        (False, False, False),
        (True, False, False),
        (False, True, False),
        (False, True, True),
    ], ids=['untracked', 'tracked', 'encrypted', 'excluded'])
def test_alt_source(
        runner, yadm_y, paths,
        tracked, encrypt, exclude):
    """Test yadm alt operates on all expected sources of alternates"""

    utils.create_alt_files(
        paths, '##default', tracked=tracked, encrypt=encrypt, exclude=exclude)
    run = runner(yadm_y('alt'))
    assert run.success
    assert run.err == ''
    linked = utils.parse_alt_output(run.out)

    for link_path in TEST_PATHS:
        source_file = link_path + '##default'
        if tracked or (encrypt and not exclude):
            assert paths.work.join(link_path).islink()
            target = py.path.local(paths.work.join(link_path).readlink())
            if target.isfile():
                assert paths.work.join(link_path).read() == source_file
                assert str(paths.work.join(source_file)) in linked
            else:
                assert paths.work.join(link_path).join(
                    utils.CONTAINED).read() == source_file
                assert str(paths.work.join(source_file)) in linked
        else:
            assert not paths.work.join(link_path).exists()
            assert str(paths.work.join(source_file)) not in linked


@pytest.mark.usefixtures('ds1_copy')
@pytest.mark.parametrize('suffix', [
    '##default',
    '##o.$tst_sys', '##os.$tst_sys',
    '##d.$tst_distro', '##distro.$tst_distro',
    '##c.$tst_class', '##class.$tst_class',
    '##h.$tst_host', '##hostname.$tst_host',
    '##u.$tst_user', '##user.$tst_user',
    ])
def test_alt_conditions(
        runner, yadm_y, paths,
        tst_sys, tst_distro, tst_host, tst_user, suffix):
    """Test conditions supported by yadm alt"""

    # set the class
    tst_class = 'testclass'
    utils.set_local(paths, 'class', tst_class)

    suffix = string.Template(suffix).substitute(
        tst_sys=tst_sys,
        tst_distro=tst_distro,
        tst_class=tst_class,
        tst_host=tst_host,
        tst_user=tst_user,
    )

    utils.create_alt_files(paths, suffix)
    run = runner(yadm_y('alt'))
    assert run.success
    assert run.err == ''
    linked = utils.parse_alt_output(run.out)

    for link_path in TEST_PATHS:
        source_file = link_path + suffix
        assert paths.work.join(link_path).islink()
        target = py.path.local(paths.work.join(link_path).readlink())
        if target.isfile():
            assert paths.work.join(link_path).read() == source_file
            assert str(paths.work.join(source_file)) in linked
        else:
            assert paths.work.join(link_path).join(
                utils.CONTAINED).read() == source_file
            assert str(paths.work.join(source_file)) in linked


@pytest.mark.usefixtures('ds1_copy')
@pytest.mark.parametrize('kind', ['builtin', '', 'envtpl', 'j2cli', 'j2'])
@pytest.mark.parametrize('label', ['t', 'template', 'yadm', ])
def test_alt_templates(
        runner, yadm_y, paths, kind, label):
    """Test templates supported by yadm alt"""

    suffix = f'##{label}.{kind}'
    utils.create_alt_files(paths, suffix)
    run = runner(yadm_y('alt'))
    assert run.success
    assert run.err == ''
    created = utils.parse_alt_output(run.out, linked=False)

    for created_path in TEST_PATHS:
        if created_path != utils.ALT_DIR:
            source_file = created_path + suffix
            assert paths.work.join(created_path).isfile()
            assert paths.work.join(created_path).read().strip() == source_file
            assert str(paths.work.join(source_file)) in created


@pytest.mark.usefixtures('ds1_copy')
@pytest.mark.parametrize('autoalt', [None, 'true', 'false'])
def test_auto_alt(runner, yadm_y, paths, autoalt):
    """Test auto alt"""

    # set the value of auto-alt
    if autoalt:
        os.system(' '.join(yadm_y('config', 'yadm.auto-alt', autoalt)))

    utils.create_alt_files(paths, '##default')
    run = runner(yadm_y('status'))
    assert run.success
    assert run.err == ''
    linked = utils.parse_alt_output(run.out)

    for link_path in TEST_PATHS:
        source_file = link_path + '##default'
        if autoalt == 'false':
            assert not paths.work.join(link_path).exists()
        else:
            assert paths.work.join(link_path).islink()
            target = py.path.local(paths.work.join(link_path).readlink())
            if target.isfile():
                assert paths.work.join(link_path).read() == source_file
                # no linking output when run via auto-alt
                assert str(paths.work.join(source_file)) not in linked
            else:
                assert paths.work.join(link_path).join(
                    utils.CONTAINED).read() == source_file
                # no linking output when run via auto-alt
                assert str(paths.work.join(source_file)) not in linked


@pytest.mark.usefixtures('ds1_copy')
def test_stale_link_removal(runner, yadm_y, paths):
    """Stale links to alternative files are removed

    This test ensures that when an already linked alternative becomes invalid
    due to a change in class, the alternate link is removed.
    """

    # set the class
    tst_class = 'testclass'
    utils.set_local(paths, 'class', tst_class)

    # create files which match the test class
    utils.create_alt_files(paths, f'##class.{tst_class}')

    # run alt to trigger linking
    run = runner(yadm_y('alt'))
    assert run.success
    assert run.err == ''
    linked = utils.parse_alt_output(run.out)

    # assert the proper linking has occurred
    for stale_path in TEST_PATHS:
        source_file = stale_path + '##class.' + tst_class
        assert paths.work.join(stale_path).islink()
        target = py.path.local(paths.work.join(stale_path).readlink())
        if target.isfile():
            assert paths.work.join(stale_path).read() == source_file
            assert str(paths.work.join(source_file)) in linked
        else:
            assert paths.work.join(stale_path).join(
                utils.CONTAINED).read() == source_file
            assert str(paths.work.join(source_file)) in linked

    # change the class so there are no valid alternates
    utils.set_local(paths, 'class', 'changedclass')

    # run alt to trigger linking
    run = runner(yadm_y('alt'))
    assert run.success
    assert run.err == ''
    linked = utils.parse_alt_output(run.out)

    # assert the linking is removed
    for stale_path in TEST_PATHS:
        source_file = stale_path + '##class.' + tst_class
        assert not paths.work.join(stale_path).exists()
        assert str(paths.work.join(source_file)) not in linked
