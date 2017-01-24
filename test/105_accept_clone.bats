load common
load_fixtures
status=;output=; #; populated by bats run()

IN_REPO=(.bash_profile .vimrc)
T_DIR_REMOTE="$T_TMP/remote"
REMOTE_URL="file:///$T_TMP/remote"

setup() {
  destroy_tmp
  build_repo "${IN_REPO[@]}"
  cp -rp "$T_DIR_REPO" "$T_DIR_REMOTE"
}

create_bootstrap() {
  make_parents "$T_YADM_BOOTSTRAP"
  {
    echo "#!/bin/bash"
    echo "echo Bootstrap successful"
    echo "exit 123"
  } > "$T_YADM_BOOTSTRAP"
  chmod a+x "$T_YADM_BOOTSTRAP"
}

@test "Command 'clone' (bad remote)" {
  echo "
    When 'clone' command is provided,
    and the remote is bad,
      Report error
      Remove the YADM_REPO
      Exit with 1
  "

  #; remove existing worktree and repo
  rm -rf "$T_DIR_WORK"
  mkdir -p "$T_DIR_WORK"
  rm -rf "$T_DIR_REPO"

  #; run clone
  run "${T_YADM_Y[@]}" clone -w "$T_DIR_WORK" "file:///bogus-repo"

  #; validate status and output
  [ "$status" -eq 1 ]
  [[ "$output" =~ Unable\ to\ fetch\ origin ]]

  #; confirm repo directory is removed
  [ ! -d "$T_DIR_REPO" ]
}

@test "Command 'clone'" {
  echo "
    When 'clone' command is provided,
      Create new repo with attributes:
        - 0600 permissions
        - not bare
        - worktree = \$YADM_WORK
        - showUntrackedFiles = no
        - yadm.managed = true
      Report the repo as cloned
      A remote named origin exists
      Exit with 0
  "

  #; remove existing worktree and repo
  rm -rf "$T_DIR_WORK"
  mkdir -p "$T_DIR_WORK"
  rm -rf "$T_DIR_REPO"

  #; run clone
  run "${T_YADM_Y[@]}" clone -w "$T_DIR_WORK" "$REMOTE_URL"

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Initialized ]]

  #; validate repo attributes
  test_perms "$T_DIR_REPO" "drw.--.--."
  test_repo_attribute "$T_DIR_REPO" core.bare false
  test_repo_attribute "$T_DIR_REPO" core.worktree "$T_DIR_WORK"
  test_repo_attribute "$T_DIR_REPO" status.showUntrackedFiles no
  test_repo_attribute "$T_DIR_REPO" yadm.managed true

  #; test the remote
  local remote_output
  remote_output=$(GIT_DIR="$T_DIR_REPO" git remote show)
  [ "$remote_output" = "origin" ]
}

@test "Command 'clone' (existing repo)" {
  echo "
    When 'clone' command is provided,
    and a repo already exists,
      Report error
      Exit with 1
  "

  #; run clone
  run "${T_YADM_Y[@]}" clone -w "$T_DIR_WORK" "$REMOTE_URL"

  #; validate status and output
  [ "$status" -eq 1 ]
  [[ "$output" =~ Git\ repo\ already\ exists ]]
}

@test "Command 'clone' -f (force overwrite)" {
  echo "
    When 'clone' command is provided,
    and '-f' is provided,
    and a repo already exists,
      Overwrite the repo with attributes:
        - 0600 permissions
        - not bare
        - worktree = \$YADM_WORK
        - showUntrackedFiles = no
        - yadm.managed = true
      Report the repo as cloned
      A remote named origin exists
      Exit with 0
  "

  #; remove existing worktree
  rm -rf "$T_DIR_WORK"
  mkdir -p "$T_DIR_WORK"

  #; run clone
  run "${T_YADM_Y[@]}" clone -w "$T_DIR_WORK" -f "$REMOTE_URL"

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Initialized ]]

  #; validate repo attributes
  test_perms "$T_DIR_REPO" "drw.--.--."
  test_repo_attribute "$T_DIR_REPO" core.bare false
  test_repo_attribute "$T_DIR_REPO" core.worktree "$T_DIR_WORK"
  test_repo_attribute "$T_DIR_REPO" status.showUntrackedFiles no
  test_repo_attribute "$T_DIR_REPO" yadm.managed true

  #; test the remote
  local remote_output
  remote_output=$(GIT_DIR="$T_DIR_REPO" git remote show)
  [ "$remote_output" = "origin" ]
}

@test "Command 'clone' (existing conflicts)" {
  echo "
    When 'clone' command is provided,
    and '-f' is provided,
    and a repo already exists,
      Overwrite the repo with attributes:
        - 0600 permissions
        - not bare
        - worktree = \$YADM_WORK
        - showUntrackedFiles = no
        - yadm.managed = true
      Report the repo as cloned
      A remote named origin exists
      Exit with 0
  "

  #; remove existing repo
  rm -rf "$T_DIR_REPO"

  #; cause a conflict
  echo "conflict" >> "$T_DIR_WORK/.bash_profile"

  #; run clone
  run "${T_YADM_Y[@]}" clone -w "$T_DIR_WORK" "$REMOTE_URL"

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Initialized ]]

  #; validate merging note
  [[ "$output" =~ Merging\ origin/master\ failed ]]
  [[ "$output" =~ NOTE ]]

  #; validate repo attributes
  test_perms "$T_DIR_REPO" "drw.--.--."
  test_repo_attribute "$T_DIR_REPO" core.bare false
  test_repo_attribute "$T_DIR_REPO" core.worktree "$T_DIR_WORK"
  test_repo_attribute "$T_DIR_REPO" status.showUntrackedFiles no
  test_repo_attribute "$T_DIR_REPO" yadm.managed true

  #; test the remote
  local remote_output
  remote_output=$(GIT_DIR="$T_DIR_REPO" git remote show)
  [ "$remote_output" = "origin" ]

  #; confirm yadm repo is clean
  cd "$T_DIR_WORK" ||:
  clean_status=$("${T_YADM_Y[@]}" status -uno --porcelain)
  echo "clean_status:'$clean_status'"
  [ -z "$clean_status" ]

  #; confirm conflicts are stashed
  existing_stash=$("${T_YADM_Y[@]}" stash list)
  echo "existing_stash:'$existing_stash'"
  [[ "$existing_stash" =~ Conflicts\ preserved ]]

  stashed_conflicts=$("${T_YADM_Y[@]}" stash show -p)
  echo "stashed_conflicts:'$stashed_conflicts'"
  [[ "$stashed_conflicts" =~ \+conflict ]]

}

@test "Command 'clone' (force bootstrap, missing)" {
  echo "
    When 'clone' command is provided,
    with the --bootstrap parameter
    and bootstrap does not exists
      Create new repo with attributes:
        - 0600 permissions
        - not bare
        - worktree = \$YADM_WORK
        - showUntrackedFiles = no
        - yadm.managed = true
      Report the repo as cloned
      A remote named origin exists
      Exit with 0
  "

  #; remove existing worktree and repo
  rm -rf "$T_DIR_WORK"
  mkdir -p "$T_DIR_WORK"
  rm -rf "$T_DIR_REPO"

  #; run clone
  run "${T_YADM_Y[@]}" clone --bootstrap -w "$T_DIR_WORK" "$REMOTE_URL"

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Initialized ]]

  #; validate repo attributes
  test_perms "$T_DIR_REPO" "drw.--.--."
  test_repo_attribute "$T_DIR_REPO" core.bare false
  test_repo_attribute "$T_DIR_REPO" core.worktree "$T_DIR_WORK"
  test_repo_attribute "$T_DIR_REPO" status.showUntrackedFiles no
  test_repo_attribute "$T_DIR_REPO" yadm.managed true

  #; test the remote
  local remote_output
  remote_output=$(GIT_DIR="$T_DIR_REPO" git remote show)
  [ "$remote_output" = "origin" ]
}

@test "Command 'clone' (force bootstrap, existing)" {
  echo "
    When 'clone' command is provided,
    with the --bootstrap parameter
    and bootstrap exists
      Create new repo with attributes:
        - 0600 permissions
        - not bare
        - worktree = \$YADM_WORK
        - showUntrackedFiles = no
        - yadm.managed = true
      Report the repo as cloned
      A remote named origin exists
      Run the bootstrap
      Exit with bootstrap's exit code
  "

  #; remove existing worktree and repo
  rm -rf "$T_DIR_WORK"
  mkdir -p "$T_DIR_WORK"
  rm -rf "$T_DIR_REPO"

  #; create the bootstrap
  create_bootstrap

  #; run clone
  run "${T_YADM_Y[@]}" clone --bootstrap -w "$T_DIR_WORK" "$REMOTE_URL"

  #; validate status and output
  [ "$status" -eq 123 ]
  [[ "$output" =~ Initialized ]]
  [[ "$output" =~ Bootstrap\ successful ]]

  #; validate repo attributes
  test_perms "$T_DIR_REPO" "drw.--.--."
  test_repo_attribute "$T_DIR_REPO" core.bare false
  test_repo_attribute "$T_DIR_REPO" core.worktree "$T_DIR_WORK"
  test_repo_attribute "$T_DIR_REPO" status.showUntrackedFiles no
  test_repo_attribute "$T_DIR_REPO" yadm.managed true

  #; test the remote
  local remote_output
  remote_output=$(GIT_DIR="$T_DIR_REPO" git remote show)
  [ "$remote_output" = "origin" ]
}

@test "Command 'clone' (prevent bootstrap)" {
  echo "
    When 'clone' command is provided,
    with the --no-bootstrap parameter
    and bootstrap exists
      Create new repo with attributes:
        - 0600 permissions
        - not bare
        - worktree = \$YADM_WORK
        - showUntrackedFiles = no
        - yadm.managed = true
      Report the repo as cloned
      A remote named origin exists
      Do NOT run bootstrap
      Exit with 0
  "

  #; remove existing worktree and repo
  rm -rf "$T_DIR_WORK"
  mkdir -p "$T_DIR_WORK"
  rm -rf "$T_DIR_REPO"

  #; create the bootstrap
  create_bootstrap

  #; run clone
  run "${T_YADM_Y[@]}" clone --no-bootstrap -w "$T_DIR_WORK" "$REMOTE_URL"

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ $output =~ Initialized ]]
  [[ ! $output =~ Bootstrap\ successful ]]

  #; validate repo attributes
  test_perms "$T_DIR_REPO" "drw.--.--."
  test_repo_attribute "$T_DIR_REPO" core.bare false
  test_repo_attribute "$T_DIR_REPO" core.worktree "$T_DIR_WORK"
  test_repo_attribute "$T_DIR_REPO" status.showUntrackedFiles no
  test_repo_attribute "$T_DIR_REPO" yadm.managed true

  #; test the remote
  local remote_output
  remote_output=$(GIT_DIR="$T_DIR_REPO" git remote show)
  [ "$remote_output" = "origin" ]
}

@test "Command 'clone' (existing bootstrap, answer n)" {
  echo "
    When 'clone' command is provided,
    and bootstrap exists
      Create new repo with attributes:
        - 0600 permissions
        - not bare
        - worktree = \$YADM_WORK
        - showUntrackedFiles = no
        - yadm.managed = true
      Report the repo as cloned
      A remote named origin exists
      Do NOT run bootstrap
      Exit with 0
  "

  #; remove existing worktree and repo
  rm -rf "$T_DIR_WORK"
  mkdir -p "$T_DIR_WORK"
  rm -rf "$T_DIR_REPO"

  #; create the bootstrap
  create_bootstrap

  #; run clone
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} clone -w "$T_DIR_WORK" "$REMOTE_URL";
    expect "Would you like to execute it now" {send "n\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
    exit \$value
EOF

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Initialized ]]
  [[ ! "$output" =~ Bootstrap\ successful ]]

  #; validate repo attributes
  test_perms "$T_DIR_REPO" "drw.--.--."
  test_repo_attribute "$T_DIR_REPO" core.bare false
  test_repo_attribute "$T_DIR_REPO" core.worktree "$T_DIR_WORK"
  test_repo_attribute "$T_DIR_REPO" status.showUntrackedFiles no
  test_repo_attribute "$T_DIR_REPO" yadm.managed true

  #; test the remote
  local remote_output
  remote_output=$(GIT_DIR="$T_DIR_REPO" git remote show)
  [ "$remote_output" = "origin" ]
}

@test "Command 'clone' (existing bootstrap, answer y)" {
  echo "
    When 'clone' command is provided,
    and bootstrap exists
      Create new repo with attributes:
        - 0600 permissions
        - not bare
        - worktree = \$YADM_WORK
        - showUntrackedFiles = no
        - yadm.managed = true
      Report the repo as cloned
      A remote named origin exists
      Run the bootstrap
      Exit with bootstrap's exit code
  "

  #; remove existing worktree and repo
  rm -rf "$T_DIR_WORK"
  mkdir -p "$T_DIR_WORK"
  rm -rf "$T_DIR_REPO"

  #; create the bootstrap
  create_bootstrap

  #; run clone
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} clone -w "$T_DIR_WORK" "$REMOTE_URL";
    expect "Would you like to execute it now" {send "y\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
    exit \$value
EOF

  #; validate status and output
  [ "$status" -eq 123 ]
  [[ "$output" =~ Initialized ]]
  [[ "$output" =~ Bootstrap\ successful ]]

  #; validate repo attributes
  test_perms "$T_DIR_REPO" "drw.--.--."
  test_repo_attribute "$T_DIR_REPO" core.bare false
  test_repo_attribute "$T_DIR_REPO" core.worktree "$T_DIR_WORK"
  test_repo_attribute "$T_DIR_REPO" status.showUntrackedFiles no
  test_repo_attribute "$T_DIR_REPO" yadm.managed true

  #; test the remote
  local remote_output
  remote_output=$(GIT_DIR="$T_DIR_REPO" git remote show)
  [ "$remote_output" = "origin" ]
}
