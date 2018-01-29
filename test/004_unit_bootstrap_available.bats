load common
T_YADM_BOOTSTRAP=; # populated by load_fixtures
load_fixtures
status=; # populated by bats run()

setup() {
  destroy_tmp
  make_parents "$T_YADM_BOOTSTRAP"
}

teardown() {
  destroy_tmp
}

function available_test() {
  # shellcheck source=/dev/null
  YADM_TEST=1 source "$T_YADM"
  # shellcheck disable=SC2034
  YADM_BOOTSTRAP="$T_YADM_BOOTSTRAP"
  status=0
  { bootstrap_available; } || {
    status=$?
    true
  }

  echo -e "STATUS:$status"

}

@test "Bootstrap missing" {
  echo "
    When bootstrap command is missing
    return 1
  "

  available_test
  [ "$status" == 1 ]

}

@test "Bootstrap not executable" {
  echo "
    When bootstrap command is not executable
    return 1
  "

  touch "$T_YADM_BOOTSTRAP"

  available_test
  [ "$status" == 1 ]

}

@test "Bootstrap executable" {
  echo "
    When bootstrap command is not executable
    return 0
  "

  touch "$T_YADM_BOOTSTRAP"
  chmod a+x "$T_YADM_BOOTSTRAP"

  available_test
  [ "$status" == 0 ]

}
