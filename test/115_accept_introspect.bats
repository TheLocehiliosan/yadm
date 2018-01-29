load common
load_fixtures
status=;output=; #; populated by bats run()

function count_introspect() {
  local category="$1"
  local expected_status="$2"
  local expected_words="$3"
  local expected_regex="$4"

  run "${T_YADM_Y[@]}" introspect "$category"
  local output_words
  output_words=$(wc -w <<< "$output")

  if [ "$status" -ne "$expected_status" ]; then
    echo "ERROR: Unexpected exit code (expected $expected_status, got $status)"
    return 1;
  fi

  if [ "$output_words" -ne "$expected_words" ]; then
    echo "ERROR: Unexpected number of output words (expected $expected_words, got $output_words)"
    return 1;
  fi

  if [ -n "$expected_regex" ]; then
    if [[ ! "$output" =~ $expected_regex ]]; then
      echo "OUTPUT:$output"
      echo "ERROR: Output does not match regex: $expected_regex"
      return 1;
    fi
  fi

}

@test "Command 'introspect' (no category)" {
  echo "
    When 'introspect' command is provided,
      And no category is provided
        Produce no output
        Exit with 0
  "

  count_introspect "" 0 0
}

@test "Command 'introspect' (invalid category)" {
  echo "
    When 'introspect' command is provided,
      And an invalid category is provided
        Produce no output
        Exit with 0
  "

  count_introspect "invalid_cat" 0 0
}

@test "Command 'introspect' (commands)" {
  echo "
    When 'introspect' command is provided,
      And category 'commands' is provided
        Produce command list
        Exit with 0
  "

  count_introspect "commands" 0 15 'version'
}

@test "Command 'introspect' (configs)" {
  echo "
    When 'introspect' command is provided,
      And category 'configs' is provided
        Produce switch list
        Exit with 0
  "

  count_introspect "configs" 0 13 'yadm\.auto-alt'
}

@test "Command 'introspect' (repo)" {
  echo "
    When 'introspect' command is provided,
      And category 'repo' is provided
        Output repo
        Exit with 0
  "

  count_introspect "repo" 0 1 "$T_DIR_REPO"
}

@test "Command 'introspect' (switches)" {
  echo "
    When 'introspect' command is provided,
      And category 'switches' is provided
        Produce switch list
        Exit with 0
  "

  count_introspect "switches" 0 7 '--yadm-dir'
}
