load common
load_fixtures
status=;lines=; #; populated by bats run()

IN_REPO=(.bash_profile .hammerspoon/init.lua .vimrc)
SUBDIR=".hammerspoon"
IN_SUBDIR=(init.lua)

function setup() {
  destroy_tmp
  build_repo "${IN_REPO[@]}"
}

@test "Command 'list' -a" {
  echo "
    When 'list' command is provided,
    and '-a' is provided,
    List tracked files
    Exit with 0
  "

  #; run list -a
  run "${T_YADM_Y[@]}" list -a

  #; validate status and output
  [ "$status" -eq 0 ]
  local line=0
  for f in "${IN_REPO[@]}"; do
    [ "${lines[$line]}" = "$f" ]
    ((line++)) || true
  done
}

@test "Command 'list' (outside of worktree)" {
  echo "
    When 'list' command is provided,
    and while outside of the worktree
    List tracked files
    Exit with 0
  "

  #; run list
  run "${T_YADM_Y[@]}" list

  #; validate status and output
  [ "$status" -eq 0 ]
  local line=0
  for f in "${IN_REPO[@]}"; do
    [ "${lines[$line]}" = "$f" ]
    ((line++)) || true
  done
}

@test "Command 'list' (in root of worktree)" {
  echo "
    When 'list' command is provided,
    and while in root of the worktree
    List tracked files
    Exit with 0
  "

  #; run list
  run bash -c "(cd '$T_DIR_WORK'; ${T_YADM_Y[*]} list)"

  #; validate status and output
  [ "$status" -eq 0 ]
  local line=0
  for f in "${IN_REPO[@]}"; do
    [ "${lines[$line]}" = "$f" ]
    ((line++)) || true
  done
}

@test "Command 'list' (in subdirectory of worktree)" {
  echo "
    When 'list' command is provided,
    and while in subdirectory of the worktree
    List tracked files for current directory
    Exit with 0
  "

  #; run list
  run bash -c "(cd '$T_DIR_WORK/$SUBDIR'; ${T_YADM_Y[*]} list)"

  #; validate status and output
  [ "$status" -eq 0 ]
  local line=0
  for f in "${IN_SUBDIR[@]}"; do
    echo "'${lines[$line]}' = '$f'"
    [ "${lines[$line]}" = "$f" ]
    ((line++)) || true
  done
}
