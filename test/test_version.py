"""Test version"""

import re
import pytest


@pytest.fixture(scope='module')
def expected_version(yadm):
    """
    Expected semantic version number. This is taken directly out of yadm,
    searching for the VERSION= string.
    """
    yadm_version = re.findall(
        r'VERSION=([^\n]+)',
        open(yadm).read())
    if yadm_version:
        return yadm_version[0]
    pytest.fail(f'version not found in {yadm}')
    return 'not found'


def test_semantic_version(expected_version):
    """Version is semantic"""
    # semantic version conforms to MAJOR.MINOR.PATCH
    assert re.search(r'^\d+\.\d+\.\d+$', expected_version), (
        'does not conform to MAJOR.MINOR.PATCH')


def test_reported_version(
        runner, yadm_y, expected_version):
    """Report correct version"""
    run = runner(command=yadm_y('version'))
    assert run.success
    assert run.err == ''
    assert run.out == f'yadm {expected_version}\n'
