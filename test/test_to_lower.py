"""Test to_lower function"""
import pytest


@pytest.mark.parametrize(
    "case",
    [
        {"input": "abcdefghijklmnopqrstuvwxyz", "expected": "abcdefghijklmnopqrstuvwxyz"},
        {"input": "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "expected": "abcdefghijklmnopqrstuvwxyz"},
        {"input": "MixedCase", "expected": "mixedcase"},
        {"input": "MixedCase", "expected": "mixedcase"},
        {"input": "ABC abc Ɛ🤷 1234567890!@#$%^&*()-=+_ XYZ", "expected": "abc abc Ɛ🤷 1234567890!@#$%^&*()-=+_ xyz"},
    ],
)
def test_get_mode(runner, yadm, case):
    """Test function to_lower"""
    script = f"""
        YADM_TEST=1 source {yadm}
        result=$(to_lower "{case["input"]}")
        echo "RESULT:$result"
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    assert f"RESULT:{case['expected']}\n" in run.out
