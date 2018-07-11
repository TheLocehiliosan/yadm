"""Test perms"""

import os
import warnings
import pytest


@pytest.mark.parametrize('autoperms', ['notest', 'unset', 'true', 'false'])
@pytest.mark.usefixtures('ds1_copy')
def test_perms(runner, yadm_y, paths, ds1, autoperms):
    """Test perms"""
    # set the value of auto-perms
    if autoperms != 'notest':
        if autoperms != 'unset':
            os.system(' '.join(yadm_y('config', 'yadm.auto-perms', autoperms)))

    # privatepaths will hold all paths that should become secured
    privatepaths = [paths.work.join('.ssh'), paths.work.join('.gnupg')]
    privatepaths += [paths.work.join(private.path) for private in ds1.private]

    # create an archive file
    os.system(f'touch "{str(paths.archive)}"')
    privatepaths.append(paths.archive)

    # create encrypted file test data
    efile1 = paths.work.join('efile1')
    efile1.write('efile1')
    efile2 = paths.work.join('efile2')
    efile2.write('efile2')
    paths.encrypt.write('efile1\nefile2\n!efile1\n')
    insecurepaths = [efile1]
    privatepaths.append(efile2)

    # assert these paths begin unsecured
    for private in privatepaths + insecurepaths:
        assert not oct(private.stat().mode).endswith('00'), (
            'Path started secured')

    cmd = 'perms'
    if autoperms != 'notest':
        cmd = 'status'
    run = runner(yadm_y(cmd))
    assert run.success
    assert run.err == ''
    if cmd == 'perms':
        assert run.out == ''

    # these paths should be secured if processing perms
    for private in privatepaths:
        if '.p2' in private.basename or '.p4' in private.basename:
            # Dot files within .ssh/.gnupg are not protected.
            # This is a but which must be fixed
            warnings.warn('Unhandled bug: private dot files', Warning)
            continue
        if autoperms == 'false':
            assert not oct(private.stat().mode).endswith('00'), (
                'Path should not be secured')
        else:
            assert oct(private.stat().mode).endswith('00'), (
                'Path has not been secured')

    # these paths should never be secured
    for private in insecurepaths:
        assert not oct(private.stat().mode).endswith('00'), (
            'Path should not be secured')


@pytest.mark.parametrize('sshperms', [None, 'true', 'false'])
@pytest.mark.parametrize('gpgperms', [None, 'true', 'false'])
@pytest.mark.usefixtures('ds1_copy')
def test_perms_control(runner, yadm_y, paths, ds1, sshperms, gpgperms):
    """Test fine control of perms"""
    # set the value of ssh-perms
    if sshperms:
        os.system(' '.join(yadm_y('config', 'yadm.ssh-perms', sshperms)))

    # set the value of gpg-perms
    if gpgperms:
        os.system(' '.join(yadm_y('config', 'yadm.gpg-perms', gpgperms)))

    # privatepaths will hold all paths that should become secured
    privatepaths = [paths.work.join('.ssh'), paths.work.join('.gnupg')]
    privatepaths += [paths.work.join(private.path) for private in ds1.private]

    # assert these paths begin unsecured
    for private in privatepaths:
        assert not oct(private.stat().mode).endswith('00'), (
            'Path started secured')

    run = runner(yadm_y('perms'))
    assert run.success
    assert run.err == ''
    assert run.out == ''

    # these paths should be secured if processing perms
    for private in privatepaths:
        if '.p2' in private.basename or '.p4' in private.basename:
            # Dot files within .ssh/.gnupg are not protected.
            # This is a but which must be fixed
            warnings.warn('Unhandled bug: private dot files', Warning)
            continue
        if (
                (sshperms == 'false' and 'ssh' in str(private))
                or
                (gpgperms == 'false' and 'gnupg' in str(private))
        ):
            assert not oct(private.stat().mode).endswith('00'), (
                'Path should not be secured')
        else:
            assert oct(private.stat().mode).endswith('00'), (
                'Path has not been secured')
