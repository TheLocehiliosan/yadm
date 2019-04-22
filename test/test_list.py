"""Test list"""

import os
import pytest


@pytest.mark.parametrize(
    'location', [
        'work',
        'outside',
        'subdir',
    ])
@pytest.mark.usefixtures('ds1_copy')
def test_list(runner, yadm_y, paths, ds1, location):
    """List tests"""
    if location == 'work':
        run_dir = paths.work
    elif location == 'outside':
        run_dir = paths.work.join('..')
    elif location == 'subdir':
        # first directory with tracked data
        run_dir = paths.work.join(ds1.tracked_dirs[0])
    with run_dir.as_cwd():
        # test with '-a'
        # should get all tracked files, relative to the work path
        run = runner(command=yadm_y('list', '-a'))
        assert run.success
        assert run.err == ''
        returned_files = set(run.out.splitlines())
        expected_files = set([e.path for e in ds1 if e.tracked])
        assert returned_files == expected_files
        # test without '-a'
        # should get all tracked files, relative to the work path unless in a
        # subdir, then those should be a limited set of files, relative to the
        # subdir
        run = runner(command=yadm_y('list'))
        assert run.success
        assert run.err == ''
        returned_files = set(run.out.splitlines())
        if location == 'subdir':
            basepath = os.path.basename(os.getcwd())
            # only expect files within the subdir
            # names should be relative to subdir
            expected_files = set(
                [e.path[len(basepath)+1:] for e in ds1
                 if e.tracked and e.path.startswith(basepath)])
        assert returned_files == expected_files
