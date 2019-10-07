"""Unit tests: is_valid_branch_name"""
import pytest

# Git branches do not allow:
#  * path component that begins with "."
#  * double dot
#  * "~", "^", ":", "\", space
#  * end with a "/"
#  * end with ".lock"


@pytest.mark.parametrize(
    'branch, expected', [
        ('master', 'valid'),
        ('path/branch', 'valid'),
        ('path/.branch', 'invalid'),
        ('path..branch', 'invalid'),
        ('path~branch', 'invalid'),
        ('path^branch', 'invalid'),
        ('path:branch', 'invalid'),
        ('path\\branch', 'invalid'),
        ('path branch', 'invalid'),
        ('path/branch/', 'invalid'),
        ('branch.lock', 'invalid'),
    ])
def test_is_valid_branch_name(runner, yadm, branch, expected):
    """Test function is_valid_branch_name()"""

    script = f"""
        YADM_TEST=1 source {yadm}
        if is_valid_branch_name "{branch}"; then
            echo valid
        else
            echo invalid
        fi
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert run.out.strip() == expected
