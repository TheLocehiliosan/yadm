load common
load_fixtures

@test "Default OS" {
  echo "
    By default, the value of OPERATING_SYSTEM should be reported by uname -s
  "

  # shellcheck source=/dev/null
  YADM_TEST=1 source "$T_YADM"
  status=0
  output=$( set_operating_system; echo "$OPERATING_SYSTEM" ) || {
    status=$?
    true
  }

  expected=$(uname -s 2>/dev/null)

  echo "output=$output"
  echo "expect=$expected"

  [ "$status" == 0 ]
  [ "$output" = "$expected" ]
}

@test "Detect no WSL" {
  echo "
    When /proc/version does not contain Microsoft, report uname -s
  "

  echo "proc version exists" > "$BATS_TMPDIR/proc_version"

  # shellcheck source=/dev/null
  YADM_TEST=1 source "$T_YADM"
  # shellcheck disable=SC2034
  PROC_VERSION="$BATS_TMPDIR/proc_version"
  status=0
  output=$( set_operating_system; echo "$OPERATING_SYSTEM" ) || {
    status=$?
    true
  }

  expected=$(uname -s 2>/dev/null)

  echo "output=$output"
  echo "expect=$expected"

  [ "$status" == 0 ]
  [ "$output" = "$expected" ]
}

@test "Detect WSL" {
  echo "
    When /proc/version contains Microsoft, report WSL
  "

  echo "proc version contains Microsoft in it" > "$BATS_TMPDIR/proc_version"

  # shellcheck source=/dev/null
  YADM_TEST=1 source "$T_YADM"
  # shellcheck disable=SC2034
  PROC_VERSION="$BATS_TMPDIR/proc_version"
  status=0
  output=$( set_operating_system; echo "$OPERATING_SYSTEM" ) || {
    status=$?
    true
  }

  expected="WSL"

  echo "output=$output"
  echo "expect=$expected"

  [ "$status" == 0 ]
  [ "$output" = "$expected" ]
}
