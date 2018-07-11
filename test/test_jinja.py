"""Test jinja"""

import os
import re
import pytest
import utils


@pytest.fixture(scope='module')
def envtpl_present(runner):
    """Is envtpl present and working?"""
    try:
        run = runner(command=['envtpl', '-h'])
        if run.success:
            return True
    except BaseException:
        pass
    return False


@pytest.mark.usefixtures('ds1_copy')
def test_local_override(runner, yadm_y, paths,
                        tst_distro, envtpl_present):
    """Test local overrides"""
    if not envtpl_present:
        pytest.skip('Unable to test without envtpl.')

    # define local overrides
    utils.set_local(paths, 'class', 'or-class')
    utils.set_local(paths, 'hostname', 'or-hostname')
    utils.set_local(paths, 'os', 'or-os')
    utils.set_local(paths, 'user', 'or-user')

    template = (
        'j2-{{ YADM_CLASS }}-'
        '{{ YADM_OS }}-{{ YADM_HOSTNAME }}-'
        '{{ YADM_USER }}-{{ YADM_DISTRO }}'
    )
    expected = f'j2-or-class-or-os-or-hostname-or-user-{tst_distro}'

    utils.create_alt_files(paths, '##yadm.j2', content=template)

    # run alt to trigger linking
    run = runner(yadm_y('alt'))
    assert run.success
    assert run.err == ''
    created = created_list(run.out)

    # assert the proper creation has occurred
    for file_path in (utils.ALT_FILE1, utils.ALT_FILE2):
        source_file = file_path + '##yadm.j2'
        assert paths.work.join(file_path).isfile()
        lines = paths.work.join(file_path).readlines(cr=False)
        assert lines[0] == source_file
        assert lines[1] == expected
        assert str(paths.work.join(source_file)) in created


@pytest.mark.parametrize('autoalt', [None, 'true', 'false'])
@pytest.mark.usefixtures('ds1_copy')
def test_auto_alt(runner, yadm_y, paths, autoalt, tst_sys,
                  envtpl_present):
    """Test setting auto-alt"""

    if not envtpl_present:
        pytest.skip('Unable to test without envtpl.')

    # set the value of auto-alt
    if autoalt:
        os.system(' '.join(yadm_y('config', 'yadm.auto-alt', autoalt)))

    # create file
    jinja_suffix = '##yadm.j2'
    utils.create_alt_files(paths, jinja_suffix, content='{{ YADM_OS }}')

    # run status to possibly trigger linking
    run = runner(yadm_y('status'))
    assert run.success
    assert run.err == ''
    created = created_list(run.out)

    # assert the proper creation has occurred
    for file_path in (utils.ALT_FILE1, utils.ALT_FILE2):
        source_file = file_path + jinja_suffix
        if autoalt == 'false':
            assert not paths.work.join(file_path).exists()
        else:
            assert paths.work.join(file_path).isfile()
            lines = paths.work.join(file_path).readlines(cr=False)
            assert lines[0] == source_file
            assert lines[1] == tst_sys
            # no created output when run via auto-alt
            assert str(paths.work.join(source_file)) not in created


@pytest.mark.usefixtures('ds1_copy')
def test_jinja_envtpl_missing(runner, paths):
    """Test operation when envtpl is missing"""

    script = f"""
        YADM_TEST=1 source {paths.pgm}
        process_global_args -Y "{paths.yadm}"
        set_operating_system
        configure_paths
        ENVTPL_PROGRAM='envtpl_missing' main alt
    """

    utils.create_alt_files(paths, '##yadm.j2')

    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert f'envtpl not available, not creating' in run.out


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
def test_jinja(runner, yadm_y, paths,
               tst_sys, tst_host, tst_user, tst_distro,
               tracked, encrypt, exclude,
               envtpl_present):
    """Test jinja processing"""

    if not envtpl_present:
        pytest.skip('Unable to test without envtpl.')

    jinja_suffix = '##yadm.j2'

    # set the class
    tst_class = 'testclass'
    utils.set_local(paths, 'class', tst_class)

    template = (
        'j2-{{ YADM_CLASS }}-'
        '{{ YADM_OS }}-{{ YADM_HOSTNAME }}-'
        '{{ YADM_USER }}-{{ YADM_DISTRO }}'
    )
    expected = (
        f'j2-{tst_class}-'
        f'{tst_sys}-{tst_host}-'
        f'{tst_user}-{tst_distro}'
    )

    utils.create_alt_files(paths, jinja_suffix, content=template,
                           tracked=tracked, encrypt=encrypt, exclude=exclude)

    # run alt to trigger linking
    run = runner(yadm_y('alt'))
    assert run.success
    assert run.err == ''
    created = created_list(run.out)

    # assert the proper creation has occurred
    for file_path in (utils.ALT_FILE1, utils.ALT_FILE2):
        source_file = file_path + jinja_suffix
        if tracked or (encrypt and not exclude):
            assert paths.work.join(file_path).isfile()
            lines = paths.work.join(file_path).readlines(cr=False)
            assert lines[0] == source_file
            assert lines[1] == expected
            assert str(paths.work.join(source_file)) in created
        else:
            assert not paths.work.join(file_path).exists()
            assert str(paths.work.join(source_file)) not in created


def created_list(output):
    """Parse output, and return list of created files"""

    created = dict()
    for line in output.splitlines():
        match = re.match('Creating (.+) from template (.+)$', line)
        if match:
            created[match.group(1)] = match.group(2)
    return created.values()
