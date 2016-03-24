load common
load_fixtures

IN_REPO=(.bash_profile .vimrc)
T_DIR_REMOTE="$T_TMP/remote"
REMOTE_URL="file:///$T_TMP/remote"

setup() {
  destroy_tmp
  build_repo "${IN_REPO[@]}"
  cp -rp "$T_DIR_REPO" "$T_DIR_REMOTE"
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
  run $T_YADM_Y clone -w "$T_DIR_WORK" "file:///bogus-repo"

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
  run $T_YADM_Y clone -w "$T_DIR_WORK" "$REMOTE_URL"

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Initialized ]]

  #; validate repo attributes
  test_perms $T_DIR_REPO "drw.--.--."
  test_repo_attribute $T_DIR_REPO core.bare false
  test_repo_attribute $T_DIR_REPO core.worktree "$T_DIR_WORK"
  test_repo_attribute $T_DIR_REPO status.showUntrackedFiles no
  test_repo_attribute $T_DIR_REPO yadm.managed true

  #; test the remote
  local remote_output=$(GIT_DIR="$T_DIR_REPO" git remote show)
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
  run $T_YADM_Y clone -w "$T_DIR_WORK" "$REMOTE_URL"

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
  run $T_YADM_Y clone -w "$T_DIR_WORK" -f "$REMOTE_URL"

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Initialized ]]

  #; validate repo attributes
  test_perms $T_DIR_REPO "drw.--.--."
  test_repo_attribute $T_DIR_REPO core.bare false
  test_repo_attribute $T_DIR_REPO core.worktree "$T_DIR_WORK"
  test_repo_attribute $T_DIR_REPO status.showUntrackedFiles no
  test_repo_attribute $T_DIR_REPO yadm.managed true

  #; test the remote
  local remote_output=$(GIT_DIR="$T_DIR_REPO" git remote show)
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
  run $T_YADM_Y clone -w "$T_DIR_WORK" "$REMOTE_URL"

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Initialized ]]

  #; validate merging note
  [[ "$output" =~ Merging\ origin\/master\ failed ]]
  [[ "$output" =~ NOTE ]]

  #; validate repo attributes
  test_perms $T_DIR_REPO "drw.--.--."
  test_repo_attribute $T_DIR_REPO core.bare false
  test_repo_attribute $T_DIR_REPO core.worktree "$T_DIR_WORK"
  test_repo_attribute $T_DIR_REPO status.showUntrackedFiles no
  test_repo_attribute $T_DIR_REPO yadm.managed true

  #; test the remote
  local remote_output=$(GIT_DIR="$T_DIR_REPO" git remote show)
  [ "$remote_output" = "origin" ]
}
