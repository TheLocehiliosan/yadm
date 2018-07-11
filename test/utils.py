"""Testing Utilities

This module holds values/functions common to multiple tests.
"""

import os

ALT_FILE1 = 'test_alt'
ALT_FILE2 = 'test alt/test alt'


def set_local(paths, variable, value):
    """Set local override"""
    os.system(
        f'GIT_DIR={str(paths.repo)} '
        f'git config --local "local.{variable}" "{value}"'
    )


def create_alt_files(paths, suffix,
                     preserve=False, tracked=True,
                     encrypt=False, exclude=False,
                     content=None):
    """Create new files, and add to the repo

    This is used for testing alternate files. In each case, a suffix is
    appended to two standard file paths. Particulars of the file creation and
    repo handling are dependent upon the function arguments.
    """

    if not preserve:
        if paths.work.join(ALT_FILE1).exists():
            paths.work.join(ALT_FILE1).remove(rec=1, ignore_errors=True)
            assert not paths.work.join(ALT_FILE1).exists()
        if paths.work.join(ALT_FILE2).exists():
            paths.work.join(ALT_FILE2).remove(rec=1, ignore_errors=True)
            assert not paths.work.join(ALT_FILE2).exists()

    new_file1 = paths.work.join(ALT_FILE1 + suffix)
    new_file1.write(ALT_FILE1 + suffix, ensure=True)
    new_file2 = paths.work.join(ALT_FILE2 + suffix)
    new_file2.write(ALT_FILE2 + suffix, ensure=True)
    if content:
        new_file1.write('\n' + content, mode='a', ensure=True)
        new_file2.write('\n' + content, mode='a', ensure=True)
    assert new_file1.exists()
    assert new_file2.exists()

    if tracked:
        for path in (new_file1, new_file2):
            os.system(f'GIT_DIR={str(paths.repo)} git add "{path}"')
        os.system(f'GIT_DIR={str(paths.repo)} git commit -m "Add test files"')

    if encrypt:
        paths.encrypt.write(f'{ALT_FILE1 + suffix}\n', mode='a')
        paths.encrypt.write(f'{ALT_FILE2 + suffix}\n', mode='a')
        if exclude:
            paths.encrypt.write(f'!{ALT_FILE1 + suffix}\n', mode='a')
            paths.encrypt.write(f'!{ALT_FILE2 + suffix}\n', mode='a')
