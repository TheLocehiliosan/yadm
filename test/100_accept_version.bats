load common
load_fixtures

@test "Command 'version'" {
  echo "
    When 'version' command is provided,
      Print the current version with format 'yadm x.xx'
      Exit with 0
  "

  #; run yadm with 'version' command
  run $T_YADM version

  #; load yadm variables (including VERSION)
  YADM_TEST=1 source $T_YADM

  #; validate status and output
  [ $status -eq 0 ]
  [ "$output" = "yadm $VERSION" ]
  version_regex="^yadm [[:digit:]\.]+$"
  [[ "$output" =~ $version_regex ]]
}
