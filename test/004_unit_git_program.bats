load common
T_YADM_CONFIG=; # populated by load_fixtures
load_fixtures
status=;output=; # populated by bats run()

setup() {
  destroy_tmp
  make_parents "$T_YADM_CONFIG"
}

teardown() {
  destroy_tmp
}

function configuration_test() {
  # shellcheck source=/dev/null
  YADM_TEST=1 source "$T_YADM"
  # shellcheck disable=SC2034
  YADM_CONFIG="$T_YADM_CONFIG"
  status=0
  { output=$( require_git ) && require_git; } || {
    status=$?
    true
  }

  echo -e "STATUS:$status\nGIT_PROGRAM:$GIT_PROGRAM\nOUTPUT:$output"

}

@test "Default git program" {
  echo "
    Default git program should be 'git'
  "

  configuration_test

  [ "$status" == 0 ]
  [ "$GIT_PROGRAM" = "git" ]
}

@test "Override git program (valid program)" {
  echo "
    Override git using yadm.git-program
    Program should be 'cat'
  "

  git config --file="$T_YADM_CONFIG" "yadm.git-program" "cat"

  configuration_test

  [ "$status" == 0 ]
  [ "$GIT_PROGRAM" = "cat" ]
}

@test "Override git program (invalid program)" {
  echo "
    Override git using yadm.git-program
    Program should be 'badprogram'
  "

  git config --file="$T_YADM_CONFIG" "yadm.git-program" "badprogram"

  configuration_test

  [ "$status" == 1 ]
  [[ "$output" =~ badprogram ]]
}
