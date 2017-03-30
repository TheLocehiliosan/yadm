load common
load_fixtures
status=;output=; #; populated by bats run()

setup() {
  build_repo
}

@test "Command 'enter' (SHELL not set)" {
  echo "
    When 'enter' command is provided,
      And SHELL is not set
        Report error
        Exit with 1
  "

  SHELL=
  export SHELL
  run "${T_YADM_Y[@]}" enter

  #; validate status and output
  [ $status -eq 1 ]
  [[ "$output" =~ does.not.refer.to.an.executable ]]
}

@test "Command 'enter' (SHELL not executable)" {
  echo "
    When 'enter' command is provided,
      And SHELL is not executable
        Report error
        Exit with 1
  "

  touch "$T_TMP/badshell"
  SHELL="$T_TMP/badshell"
  export SHELL
  run "${T_YADM_Y[@]}" enter

  #; validate status and output
  [ $status -eq 1 ]
  [[ "$output" =~ does.not.refer.to.an.executable ]]
}

@test "Command 'enter' (SHELL executable)" {
  echo "
    When 'enter' command is provided,
      And SHELL is set
        Execute SHELL command
        Expose GIT variables
        Set prompt variables
        Announce entering/leaving shell
        Exit with 0
  "

  SHELL=$(command -v env)
  export SHELL
  run "${T_YADM_Y[@]}" enter

  #; validate status and output
  [ $status -eq 0 ]
  [[ "$output" =~ GIT_DIR= ]]
  [[ "$output" =~ PROMPT=yadm.shell ]]
  [[ "$output" =~ PS1=yadm.shell ]]
  [[ "$output" =~ Entering.yadm.repo ]]
  [[ "$output" =~ Leaving.yadm.repo ]]
}
