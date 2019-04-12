"""Testing Utilities

This module holds values/functions common to multiple tests.
"""

import os

ALT_FILE1 = 'test_alt'
ALT_FILE2 = 'test alt/test alt'
ALT_DIR = 'test alt/test alt dir'

# Directory based alternates must have a tracked contained file.
# This will be the test contained file name
CONTAINED = 'contained_file'

# These variables are used for making include files which will be processed
# within jinja templates
INCLUDE_FILE = 'inc_file'
INCLUDE_DIRS = ['', 'test alt']
INCLUDE_CONTENT = '8780846c02e34c930d0afd127906668f'


def set_local(paths, variable, value):
    """Set local override"""
    os.system(
        f'GIT_DIR={str(paths.repo)} '
        f'git config --local "local.{variable}" "{value}"'
    )


def create_alt_files(paths, suffix,
                     preserve=False, tracked=True,
                     encrypt=False, exclude=False,
                     content=None, includefile=False):
    """Create new files, and add to the repo

    This is used for testing alternate files. In each case, a suffix is
    appended to two standard file paths. Particulars of the file creation and
    repo handling are dependent upon the function arguments.
    """

    if not preserve:
        for remove_path in (ALT_FILE1, ALT_FILE2, ALT_DIR):
            if paths.work.join(remove_path).exists():
                paths.work.join(remove_path).remove(rec=1, ignore_errors=True)
                assert not paths.work.join(remove_path).exists()

    new_file1 = paths.work.join(ALT_FILE1 + suffix)
    new_file1.write(ALT_FILE1 + suffix, ensure=True)
    new_file2 = paths.work.join(ALT_FILE2 + suffix)
    new_file2.write(ALT_FILE2 + suffix, ensure=True)
    new_dir = paths.work.join(ALT_DIR + suffix).join(CONTAINED)
    new_dir.write(ALT_DIR + suffix, ensure=True)

    # Do not test directory support for jinja alternates
    test_paths = [new_file1, new_file2]
    test_names = [ALT_FILE1, ALT_FILE2]
    if suffix != '##yadm.j2':
        test_paths += [new_dir]
        test_names += [ALT_DIR]

    for test_path in test_paths:
        if content:
            test_path.write('\n' + content, mode='a', ensure=True)
        assert test_path.exists()

    _create_includefiles(includefile, paths, test_paths)
    _create_tracked(tracked, test_paths, paths)
    _create_encrypt(encrypt, test_names, suffix, paths, exclude)


def _create_includefiles(includefile, paths, test_paths):
    if includefile:
        for dpath in INCLUDE_DIRS:
            incfile = paths.work.join(dpath + '/' + INCLUDE_FILE)
            incfile.write(INCLUDE_CONTENT, ensure=True)
            test_paths += [incfile]


def _create_tracked(tracked, test_paths, paths):
    if tracked:
        for track_path in test_paths:
            os.system(f'GIT_DIR={str(paths.repo)} git add "{track_path}"')
        os.system(f'GIT_DIR={str(paths.repo)} git commit -m "Add test files"')


def _create_encrypt(encrypt, test_names, suffix, paths, exclude):
    if encrypt:
        for encrypt_name in test_names:
            paths.encrypt.write(f'{encrypt_name + suffix}\n', mode='a')
            if exclude:
                paths.encrypt.write(f'!{encrypt_name + suffix}\n', mode='a')
