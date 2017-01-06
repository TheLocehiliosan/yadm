load common
load_fixtures
status=;output=;lines=; #; populated by bats run()

IN_REPO=(.bash_profile .vimrc)

function setup_environment() {
  destroy_tmp
  build_repo "${IN_REPO[@]}"
}

@test "Passthru unknown commands to Git" {
  echo "
    When the command 'bogus' is provided
    Report bogus is not a command
    Exit with 1
  "

  #; start fresh
  setup_environment

  #; run bogus
  run "${T_YADM_Y[@]}" bogus

  #; validate status and output
  [ "$status" -eq 1 ]
  [[ "$output" =~ .bogus..is.not.a.git.command ]]
}

@test "Git command 'add' - badfile" {
  echo "
    When the command 'add' is provided
    And the file specified does not exist
      Exit with 128
  "

  #; start fresh
  setup_environment

  #; define a non existig testfile
  local testfile="$T_DIR_WORK/does_not_exist"

  #; run add
  run "${T_YADM_Y[@]}" add -v "$testfile"

  #; validate status and output
  [ "$status" -eq 128 ]
  [[ "$output" =~ pathspec.+did.not.match ]]
}

@test "Git command 'add'" {
  echo "
    When the command 'add' is provided
      Files are added to the index
      Exit with 0
  "

  #; start fresh
  setup_environment

  #; create a testfile
  local testfile="$T_DIR_WORK/testfile"
  echo "$testfile" > "$testfile"

  #; run add
  run "${T_YADM_Y[@]}" add -v "$testfile"

  #; validate status and output
  [ "$status" -eq 0 ]
  [ "$output" = "add 'testfile'" ]
}

@test "Git command 'status'" {
  echo "
    When the command 'status' is provided
      Added files are shown
      Exit with 0
  "

  #; run status
  run "${T_YADM_Y[@]}" status

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ new\ file:[[:space:]]+testfile ]]
}

@test "Git command 'commit'" {
  echo "
    When the command 'commit' is provided
      Index is commited
      Exit with 0
  "

  #; run commit
  run "${T_YADM_Y[@]}" commit -m 'Add testfile'

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "${lines[1]}" =~ 1\ file\ changed ]]
  [[ "${lines[1]}" =~ 1\ insertion ]]
}

@test "Git command 'log'" {
  echo "
    When the command 'log' is provided
      Commits are shown
      Exit with 0
  "

  #; run log
  run "${T_YADM_Y[@]}" log --oneline

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "${lines[0]}" =~ Add\ testfile ]]
}
