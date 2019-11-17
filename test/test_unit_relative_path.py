"""Unit tests: relative_path"""
import pytest


@pytest.mark.parametrize(
    'base,full_path,expected',
    [
        ("/A/B/C", "/A", "../.."),
        ("/A/B/C", "/A/B", ".."),
        ("/A/B/C", "/A/B/C", ""),
        ("/A/B/C", "/A/B/C/D", "D"),
        ("/A/B/C", "/A/B/C/D/E", "D/E"),
        ("/A/B/C", "/A/B/D", "../D"),
        ("/A/B/C", "/A/B/D/E", "../D/E"),
        ("/A/B/C", "/A/D", "../../D"),
        ("/A/B/C", "/A/D/E", "../../D/E"),
        ("/A/B/C", "/D/E/F", "../../../D/E/F"),
    ],
)
def test_relative_path(runner, paths, base, full_path, expected):
    """Test translate_to_relative"""

    script = f"""
        YADM_TEST=1 source {paths.pgm}
        relative_path "{base}" "{full_path}"
    """

    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert run.out.strip() == expected
