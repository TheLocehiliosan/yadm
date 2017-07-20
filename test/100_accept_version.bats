load common
load_fixtures
status=;output=; #; populated by bats run()

@test "Command 'version'" {
  echo "
    When 'version' command is provided,
      Print the current version with format 'yadm x.x.x'
      Exit with 0
  "

  #; run yadm with 'version' command
  run "$T_YADM" version

  # shellcheck source=/dev/null

  #; load yadm variables (including VERSION)
  YADM_TEST=1 source "$T_YADM"

  #; validate status and output
  [ $status -eq 0 ]
  [ "$output" = "yadm $VERSION" ]
  version_regex="^yadm [[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+$"
  [[ "$output" =~ $version_regex ]]
}
