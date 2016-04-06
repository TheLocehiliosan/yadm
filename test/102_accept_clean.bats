load common
load_fixtures
status=;lines=; #; populated by bats run()

@test "Command 'clean'" {
  echo "
    When 'clean' command is provided,
      Do nothing, this is a dangerous Git command when managing dot files
      Report the command as disabled
      Exit with 1
  "

  #; run yadm with 'clean' command
  run "$T_YADM" clean

  #; validate status and output
  [ $status -eq 1 ]
  [[ "${lines[0]}" =~ disabled ]]
}
