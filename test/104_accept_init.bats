load common
load_fixtures
status=;output=; #; populated by bats run()

setup() {
  destroy_tmp
  create_worktree "$T_DIR_WORK"
}

@test "Command 'init'" {
  echo "
    When 'init' command is provided,
      Create new repo with attributes:
        - 0600 permissions
        - not bare
        - worktree = \$HOME
        - showUntrackedFiles = no
        - yadm.managed = true
      Report the repo as initialized
      Exit with 0
  "

  #; run init
  run "${T_YADM_Y[@]}" init

  #; validate status and output
  [ $status -eq 0 ]
  [[ "$output" =~ Initialized ]]

  #; validate repo attributes
  test_perms "$T_DIR_REPO" "drw.--.--."
  test_repo_attribute "$T_DIR_REPO" core.bare false
  test_repo_attribute "$T_DIR_REPO" core.worktree "$HOME"
  test_repo_attribute "$T_DIR_REPO" status.showUntrackedFiles no
  test_repo_attribute "$T_DIR_REPO" yadm.managed true
}

@test "Command 'init' -w (alternate worktree)" {
  echo "
    When 'init' command is provided,
    and '-w' is provided,
      Create new repo with attributes:
        - 0600 permissions
        - not bare
        - worktree = \$YADM_WORK
        - showUntrackedFiles = no
        - yadm.managed = true
      Report the repo as initialized
      Exit with 0
  "

  #; run init
  run "${T_YADM_Y[@]}" init -w "$T_DIR_WORK"

  #; validate status and output
  [ $status -eq 0 ]
  [[ "$output" =~ Initialized ]]

  #; validate repo attributes
  test_perms "$T_DIR_REPO" "drw.--.--."
  test_repo_attribute "$T_DIR_REPO" core.bare false
  test_repo_attribute "$T_DIR_REPO" core.worktree "$T_DIR_WORK"
  test_repo_attribute "$T_DIR_REPO" status.showUntrackedFiles no
  test_repo_attribute "$T_DIR_REPO" yadm.managed true
}

@test "Command 'init' (existing repo)" {
  echo "
    When 'init' command is provided,
      and a repo already exists,
        Refuse to create a new repo
        Exit with 1
  "

  #; create existing repo content
  mkdir -p "$T_DIR_REPO"
  local testfile="$T_DIR_REPO/testfile"
  touch "$testfile"

  #; run init
  run "${T_YADM_Y[@]}" init

  #; validate status and output
  [ $status -eq 1 ]
  [[ "$output" =~ already.exists ]]

  #; verify existing repo is intact
  if [ ! -e "$testfile" ]; then
    echo "ERROR: existing repo has been changed"
    return 1
  fi

}

@test "Command 'init' -f (force overwrite repo)" {
  echo "
    When 'init' command is provided,
      and '-f' is provided
      and a repo already exists,
        Remove existing repo
        Create new repo with attributes:
          - 0600 permissions
          - not bare
          - worktree = \$HOME
          - showUntrackedFiles = no
          - yadm.managed = true
        Report the repo as initialized
        Exit with 0
  "

  #; create existing repo content
  mkdir -p "$T_DIR_REPO"
  local testfile="$T_DIR_REPO/testfile"
  touch "$testfile"

  #; run init
  run "${T_YADM_Y[@]}" init -f

  #; validate status and output
  [ $status -eq 0 ]
  [[ "$output" =~ Initialized ]]

  #; verify existing repo is gone
  if [ -e "$testfile" ]; then
    echo "ERROR: existing repo files remain"
    return 1
  fi

  #; validate repo attributes
  test_perms "$T_DIR_REPO" "drw.--.--."
  test_repo_attribute "$T_DIR_REPO" core.bare false
  test_repo_attribute "$T_DIR_REPO" core.worktree "$HOME"
  test_repo_attribute "$T_DIR_REPO" status.showUntrackedFiles no
  test_repo_attribute "$T_DIR_REPO" yadm.managed true
}

@test "Command 'init' -f -w (force overwrite repo with alternate worktree)" {
  echo "
    When 'init' command is provided,
      and '-f' is provided
      and '-w' is provided
      and a repo already exists,
        Remove existing repo
        Create new repo with attributes:
          - 0600 permissions
          - not bare
          - worktree = \$YADM_WORK
          - showUntrackedFiles = no
          - yadm.managed = true
        Report the repo as initialized
        Exit with 0
  "

  #; create existing repo content
  mkdir -p "$T_DIR_REPO"
  local testfile="$T_DIR_REPO/testfile"
  touch "$testfile"

  #; run init
  run "${T_YADM_Y[@]}" init -f -w "$T_DIR_WORK"

  #; validate status and output
  [ $status -eq 0 ]
  [[ "$output" =~ Initialized ]]

  #; verify existing repo is gone
  if [ -e "$testfile" ]; then
    echo "ERROR: existing repo files remain"
    return 1
  fi

  #; validate repo attributes
  test_perms "$T_DIR_REPO" "drw.--.--."
  test_repo_attribute "$T_DIR_REPO" core.bare false
  test_repo_attribute "$T_DIR_REPO" core.worktree "$T_DIR_WORK"
  test_repo_attribute "$T_DIR_REPO" status.showUntrackedFiles no
  test_repo_attribute "$T_DIR_REPO" yadm.managed true
}
