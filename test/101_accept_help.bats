load common
load_fixtures
status=;lines=; #; populated by bats run()

@test "Missing command" {
  echo "
    When no command is provided,
      Produce usage instructions
      Exit with 1
  "

  #; run yadm with no command
  run "$T_YADM"

  #; validate status and output
  [ $status -eq 1 ]
  [[ "${lines[0]}" =~ ^Usage: ]]
}

@test "Command 'help'" {
  echo "
    When 'help' command is provided,
      Produce usage instructions
      Exit with value 1
  "

  #; run yadm with 'help' command
  run "$T_YADM" help

  #; validate status and output
  [ $status -eq 1 ]
  [[ "${lines[0]}" =~ ^Usage: ]]
}
