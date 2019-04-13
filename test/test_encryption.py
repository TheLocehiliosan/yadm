"""Test encryption"""

import os
import pipes
import pytest

KEY_FILE = 'test/test_key'
KEY_FINGERPRINT = 'F8BBFC746C58945442349BCEBA54FFD04C599B1A'
KEY_NAME = 'yadm-test1'
KEY_TRUST = 'test/ownertrust.txt'
PASSPHRASE = 'ExamplePassword'

pytestmark = pytest.mark.usefixtures('config_git')


def add_asymmetric_key():
    """Add asymmetric key"""
    os.system(f'gpg --import {pipes.quote(KEY_FILE)}')
    os.system(f'gpg --import-ownertrust < {pipes.quote(KEY_TRUST)}')


def remove_asymmetric_key():
    """Remove asymmetric key"""
    os.system(
        f'gpg --batch --yes '
        f'--delete-secret-keys {pipes.quote(KEY_FINGERPRINT)}')
    os.system(f'gpg --batch --yes --delete-key {pipes.quote(KEY_FINGERPRINT)}')


@pytest.fixture
def asymmetric_key():
    """Fixture for asymmetric key, removed in teardown"""
    add_asymmetric_key()
    yield KEY_NAME
    remove_asymmetric_key()


@pytest.fixture
def encrypt_targets(yadm_y, paths):
    """Fixture for setting up data to encrypt

    This fixture:
      * inits an empty repo
      * creates test files in the work tree
      * creates a ".yadm/encrypt" file for testing:
        * standard files
        * standard globs
        * directories
        * comments
        * empty lines and lines with just space
        * exclusions
      * returns a list of expected encrypted files
    """

    # init empty yadm repo
    os.system(' '.join(yadm_y('init', '-w', str(paths.work), '-f')))

    expected = []

    # standard files w/ dirs & spaces
    paths.work.join('inc file1').write('inc file1')
    expected.append('inc file1')
    paths.encrypt.write('inc file1\n')
    paths.work.join('inc dir').mkdir()
    paths.work.join('inc dir/inc file2').write('inc file2')
    expected.append('inc dir/inc file2')
    paths.encrypt.write('inc dir/inc file2\n', mode='a')

    # standard globs w/ dirs & spaces
    paths.work.join('globs file1').write('globs file1')
    expected.append('globs file1')
    paths.work.join('globs dir').mkdir()
    paths.work.join('globs dir/globs file2').write('globs file2')
    expected.append('globs dir/globs file2')
    paths.encrypt.write('globs*\n', mode='a')

    # blank lines
    paths.encrypt.write('\n        \n\t\n', mode='a')

    # comments
    paths.work.join('commentfile1').write('commentfile1')
    paths.encrypt.write('#commentfile1\n', mode='a')
    paths.encrypt.write('        #commentfile1\n', mode='a')

    # exclusions
    paths.work.join('extest').mkdir()
    paths.encrypt.write('extest/*\n', mode='a')  # include within extest
    paths.work.join('extest/inglob1').write('inglob1')
    paths.work.join('extest/exglob1').write('exglob1')
    paths.work.join('extest/exglob2').write('exglob2')
    paths.encrypt.write('!extest/ex*\n', mode='a')  # exclude the ex*
    expected.append('extest/inglob1')  # should be left with only in*

    return expected


@pytest.fixture(scope='session')
def decrypt_targets(tmpdir_factory, runner):
    """Fixture for setting data to decrypt

    This fixture:
      * creates symmetric/asymmetric encrypted archives
      * creates a list of expected decrypted files
    """

    tmpdir = tmpdir_factory.mktemp('decrypt_targets')
    symmetric = tmpdir.join('symmetric.tar.gz.gpg')
    asymmetric = tmpdir.join('asymmetric.tar.gz.gpg')

    expected = []

    tmpdir.join('decrypt1').write('decrypt1')
    expected.append('decrypt1')
    tmpdir.join('decrypt2').write('decrypt2')
    expected.append('decrypt2')
    tmpdir.join('subdir').mkdir()
    tmpdir.join('subdir/decrypt3').write('subdir/decrypt3')
    expected.append('subdir/decrypt3')

    run = runner(
        ['tar', 'cvf', '-'] +
        expected +
        ['|', 'gpg', '--batch', '--yes', '-c'] +
        ['--passphrase', pipes.quote(PASSPHRASE)] +
        ['--output', pipes.quote(str(symmetric))],
        cwd=tmpdir,
        shell=True)
    assert run.success

    add_asymmetric_key()
    run = runner(
        ['tar', 'cvf', '-'] +
        expected +
        ['|', 'gpg', '--batch', '--yes', '-e'] +
        ['-r', pipes.quote(KEY_NAME)] +
        ['--output', pipes.quote(str(asymmetric))],
        cwd=tmpdir,
        shell=True)
    assert run.success
    remove_asymmetric_key()

    return {
        'asymmetric': asymmetric,
        'expected': expected,
        'symmetric': symmetric,
    }


@pytest.mark.parametrize(
    'mismatched_phrase', [False, True],
    ids=['matching_phrase', 'mismatched_phrase'])
@pytest.mark.parametrize(
    'missing_encrypt', [False, True],
    ids=['encrypt_exists', 'encrypt_missing'])
@pytest.mark.parametrize(
    'overwrite', [False, True],
    ids=['clean', 'overwrite'])
def test_symmetric_encrypt(
        runner, yadm_y, paths, encrypt_targets,
        overwrite, missing_encrypt, mismatched_phrase):
    """Test symmetric encryption"""

    if missing_encrypt:
        paths.encrypt.remove()

    matched_phrase = PASSPHRASE
    if mismatched_phrase:
        matched_phrase = 'mismatched'

    if overwrite:
        paths.archive.write('existing archive')

    run = runner(yadm_y('encrypt'), expect=[
        ('passphrase:', PASSPHRASE),
        ('passphrase:', matched_phrase),
        ])

    if missing_encrypt or mismatched_phrase:
        assert run.failure
    else:
        assert run.success
        assert run.err == ''

    if missing_encrypt:
        assert 'does not exist' in run.out
    elif mismatched_phrase:
        assert 'invalid passphrase' in run.out
    else:
        assert encrypted_data_valid(runner, paths.archive, encrypt_targets)


@pytest.mark.parametrize(
    'wrong_phrase', [False, True],
    ids=['correct_phrase', 'wrong_phrase'])
@pytest.mark.parametrize(
    'archive_exists', [True, False],
    ids=['archive_exists', 'archive_missing'])
@pytest.mark.parametrize(
    'dolist', [False, True],
    ids=['decrypt', 'list'])
def test_symmetric_decrypt(
        runner, yadm_y, paths, decrypt_targets,
        dolist, archive_exists, wrong_phrase):
    """Test decryption"""

    # init empty yadm repo
    os.system(' '.join(yadm_y('init', '-w', str(paths.work), '-f')))

    phrase = PASSPHRASE
    if wrong_phrase:
        phrase = 'wrong-phrase'

    if archive_exists:
        decrypt_targets['symmetric'].copy(paths.archive)

    # to test overwriting
    paths.work.join('decrypt1').write('pre-existing file')

    args = []

    if dolist:
        args.append('-l')
    run = runner(yadm_y('decrypt') + args, expect=[('passphrase:', phrase)])

    if archive_exists and not wrong_phrase:
        assert run.success
        assert run.err == ''
        if dolist:
            for filename in decrypt_targets['expected']:
                if filename != 'decrypt1':  # this one should exist
                    assert not paths.work.join(filename).exists()
                assert filename in run.out
        else:
            for filename in decrypt_targets['expected']:
                assert paths.work.join(filename).read() == filename
    else:
        assert run.failure


@pytest.mark.usefixtures('asymmetric_key')
@pytest.mark.parametrize(
    'ask', [False, True],
    ids=['no_ask', 'ask'])
@pytest.mark.parametrize(
    'key_exists', [True, False],
    ids=['key_exists', 'key_missing'])
@pytest.mark.parametrize(
    'overwrite', [False, True],
    ids=['clean', 'overwrite'])
def test_asymmetric_encrypt(
        runner, yadm_y, paths, encrypt_targets,
        overwrite, key_exists, ask):
    """Test asymmetric encryption"""

    # specify encryption recipient
    if ask:
        os.system(' '.join(yadm_y('config', 'yadm.gpg-recipient', 'ASK')))
        expect = [('Enter the user ID', KEY_NAME), ('Enter the user ID', '')]
    else:
        os.system(' '.join(yadm_y('config', 'yadm.gpg-recipient', KEY_NAME)))
        expect = []

    if overwrite:
        paths.archive.write('existing archive')

    if not key_exists:
        remove_asymmetric_key()

    run = runner(yadm_y('encrypt'), expect=expect)

    if key_exists:
        assert run.success
        assert encrypted_data_valid(runner, paths.archive, encrypt_targets)
    else:
        assert run.failure
        assert 'Unable to write' in run.out

    if ask:
        assert 'Enter the user ID' in run.out


@pytest.mark.usefixtures('asymmetric_key')
@pytest.mark.parametrize(
    'key_exists', [True, False],
    ids=['key_exists', 'key_missing'])
@pytest.mark.parametrize(
    'dolist', [False, True],
    ids=['decrypt', 'list'])
def test_asymmetric_decrypt(
        runner, yadm_y, paths, decrypt_targets,
        dolist, key_exists):
    """Test decryption"""

    # init empty yadm repo
    os.system(' '.join(yadm_y('init', '-w', str(paths.work), '-f')))

    decrypt_targets['asymmetric'].copy(paths.archive)

    # to test overwriting
    paths.work.join('decrypt1').write('pre-existing file')

    if not key_exists:
        remove_asymmetric_key()

    args = []

    if dolist:
        args.append('-l')
    run = runner(yadm_y('decrypt') + args)

    if key_exists:
        assert run.success
        if dolist:
            for filename in decrypt_targets['expected']:
                if filename != 'decrypt1':  # this one should exist
                    assert not paths.work.join(filename).exists()
                assert filename in run.out
        else:
            for filename in decrypt_targets['expected']:
                assert paths.work.join(filename).read() == filename
    else:
        assert run.failure
        assert 'Unable to extract encrypted files' in run.out


@pytest.mark.parametrize(
    'untracked',
    [False, 'y', 'n'],
    ids=['tracked', 'untracked_answer_y', 'untracked_answer_n'])
def test_offer_to_add(runner, yadm_y, paths, encrypt_targets, untracked):
    """Test offer to add encrypted archive

    All the other encryption tests use an archive outside of the work tree.
    However, the archive is often inside the work tree, and if it is, there
    should be an offer to add it to the repo if it is not tracked.
    """

    worktree_archive = paths.work.join('worktree-archive.tar.gpg')
    expect = [
        ('passphrase:', PASSPHRASE),
        ('passphrase:', PASSPHRASE),
        ]

    if untracked:
        expect.append(('add it now', untracked))
    else:
        worktree_archive.write('exists')
        os.system(' '.join(yadm_y('add', str(worktree_archive))))

    run = runner(
        yadm_y('encrypt', '--yadm-archive', str(worktree_archive)),
        expect=expect
        )

    assert run.success
    assert run.err == ''
    assert encrypted_data_valid(runner, worktree_archive, encrypt_targets)

    run = runner(
        yadm_y('status', '--porcelain', '-uall', str(worktree_archive)))
    assert run.success
    assert run.err == ''

    if untracked == 'y':
        # should be added to the index
        assert f'A  {worktree_archive.basename}' in run.out
    elif untracked == 'n':
        # should NOT be added to the index
        assert f'?? {worktree_archive.basename}' in run.out
    else:
        # should appear modified in the index
        assert f'AM {worktree_archive.basename}' in run.out


def encrypted_data_valid(runner, encrypted, expected):
    """Verify encrypted data matches expectations"""
    run = runner([
        'gpg',
        '--passphrase', pipes.quote(PASSPHRASE),
        '-d', pipes.quote(str(encrypted)),
        '2>/dev/null',
        '|', 'tar', 't'], shell=True, report=False)
    file_count = 0
    for filename in run.out.splitlines():
        if filename.endswith('/'):
            continue
        file_count += 1
        assert filename in expected, (
            f'Unexpected file in archive: {filename}')
    assert file_count == len(expected), (
        'Number of files in archive does not match expected')
    return True
