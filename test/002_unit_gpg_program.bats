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
  { output=$( require_gpg ) && require_gpg; } || {
    status=$?
    true
  }

  echo -e "STATUS:$status\nGPG_PROGRAM:$GPG_PROGRAM\nOUTPUT:$output"

}

@test "Default gpg program" {
  echo "
    Default gpg program should be 'gpg'
  "

  configuration_test

  [ "$status" == 0 ]
  [ "$GPG_PROGRAM" = "gpg" ]
}

@test "Override gpg program (valid program)" {
  echo "
    Override gpg using yadm.gpg-program
    Program should be 'cat'
  "

  git config --file="$T_YADM_CONFIG" "yadm.gpg-program" "cat"

  configuration_test

  [ "$status" == 0 ]
  [ "$GPG_PROGRAM" = "cat" ]
}

@test "Override gpg program (invalid program)" {
  echo "
    Override gpg using yadm.gpg-program
    Program should be 'badprogram'
  "

  git config --file="$T_YADM_CONFIG" "yadm.gpg-program" "badprogram"

  configuration_test

  [ "$status" == 1 ]
  [[ "$output" =~ badprogram ]]
}
