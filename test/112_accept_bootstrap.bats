load common
load_fixtures
status=;output=; #; populated by bats run()

setup() {
  destroy_tmp
  build_repo
}

@test "Command 'bootstrap' (missing file)" {
  echo "
    When 'bootstrap' command is provided,
    and the bootstrap file is missing
      Report error
      Exit with 1
  "

  #; run clone
  run "${T_YADM_Y[@]}" bootstrap
  echo "STATUS:$status"
  echo "OUTPUT:$output"

  #; validate status and output
  [[ "$output" =~ Cannot\ execute\ bootstrap ]]
  [ "$status" -eq 1 ]

}

@test "Command 'bootstrap' (not executable)" {
  echo "
    When 'bootstrap' command is provided,
    and the bootstrap file is present
    but is not executable
      Report error
      Exit with 1
  "

  touch "$T_YADM_BOOTSTRAP"

  #; run clone
  run "${T_YADM_Y[@]}" bootstrap
  echo "STATUS:$status"
  echo "OUTPUT:$output"

  #; validate status and output
  [[ "$output" =~ is\ not\ an\ executable\ program ]]
  [ "$status" -eq 1 ]

}

@test "Command 'bootstrap' (bootstrap run)" {
  echo "
    When 'bootstrap' command is provided,
    and the bootstrap file is present
    and is executable
      Announce the execution
      Execute bootstrap
      Exit with the exit code of bootstrap
  "

  {
    echo "#!/bin/bash" 
    echo "echo Bootstrap successful"
    echo "exit 123"
  } > "$T_YADM_BOOTSTRAP"
  chmod a+x "$T_YADM_BOOTSTRAP"

  #; run clone
  run "${T_YADM_Y[@]}" bootstrap
  echo "STATUS:$status"
  echo "OUTPUT:$output"

  #; validate status and output
  [[ "$output" =~ Executing\ $T_YADM_BOOTSTRAP ]]
  [[ "$output" =~ Bootstrap\ successful ]]
  [ "$status" -eq 123 ]

}
