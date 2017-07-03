load common
load_fixtures

@test "Query distro (lsb_release present)" {
  echo "
    Use value of lsb_release -si
  "

  #shellcheck source=/dev/null
  YADM_TEST=1 source "$T_YADM"
  status=0
  { output=$( query_distro ); } || {
    status=$?
    true
  }

  expected="${T_DISTRO}"

  echo "output=$output"
  echo "expect=$expected"

  [ "$status" == 0 ]
  [ "$output" = "$expected" ]
}

@test "Query distro (lsb_release missing)" {
  echo "
    Empty value if lsb_release is missing
  "

  #shellcheck source=/dev/null
  YADM_TEST=1 source "$T_YADM"
  LSB_RELEASE_PROGRAM="missing_lsb_release"
  echo "Using $LSB_RELEASE_PROGRAM as lsb_release"

  status=0
  { output=$( query_distro ); } || {
    status=$?
    true
  }

  expected=""

  echo "output=$output"
  echo "expect=$expected"

  [ "$status" == 0 ]
  [ "$output" = "$expected" ]
}
