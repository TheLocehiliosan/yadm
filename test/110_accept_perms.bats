load common
load_fixtures
status=;output=; #; populated by bats run()

setup() {
  destroy_tmp
  build_repo
}

function is_restricted() {
  local p
  for p in "${restricted[@]}"; do [ "$p" = "$1" ] && return 0; done
  return 1
}

function validate_perms() {
  local perms="$*"

  #; determine which paths should have restricted permissions
  restricted=()
  local p
  for p in $perms; do
    case $p in
      ssh)
        restricted=("${restricted[@]}" $T_DIR_WORK/.ssh $T_DIR_WORK/.ssh/*)
      ;;
      gpg)
        restricted=("${restricted[@]}" $T_DIR_WORK/.gnupg $T_DIR_WORK/.gnupg/*)
      ;;
      *)
        restricted=("${restricted[@]}" $T_DIR_WORK/$p)
      ;;
    esac
  done

  #; validate permissions of each path in the worktere
  local testpath
  while IFS= read -r -d '' testpath; do
    local perm_regex="....rwxrwx"
    if is_restricted "$testpath"; then
      perm_regex="....------"
    fi
    test_perms "$testpath" "$perm_regex" || return 1
  done <   <(find "$T_DIR_WORK" -print0)

}

@test "Command 'perms'" {
  echo "
    When the command 'perms' is provided
    Update permissions for ssh/gpg
    Verify correct permissions
    Exit with 0
  "

  #; run perms
  run "${T_YADM_Y[@]}" perms

  #; validate status and output
  [ "$status" -eq 0 ]
  [ "$output" = "" ]

  #; validate permissions
  validate_perms ssh gpg
}

@test "Command 'perms' (with encrypt)" {
  echo "
    When the command 'perms' is provided
    And YADM_ENCRYPT is present
    Update permissions for ssh/gpg/encrypt
    Support comments in YADM_ENCRYPT
    Verify correct permissions
    Exit with 0
  "

  #; this version has a comment in it
  echo -e "#.vimrc\n.tmux.conf\n.hammerspoon/*\n!.tmux.conf" > "$T_YADM_ENCRYPT"

  #; run perms
  run "${T_YADM_Y[@]}" perms

  #; validate status and output
  [ "$status" -eq 0 ]
  [ "$output" = "" ]

  #; validate permissions
  validate_perms ssh gpg ".hammerspoon/*"
}

@test "Command 'perms' (ssh-perms=false)" {
  echo "
    When the command 'perms' is provided
    And yadm.ssh-perms=false
    Update permissions for gpg only
    Verify correct permissions
    Exit with 0
  "

  #; configure yadm.ssh-perms
  git config --file="$T_YADM_CONFIG" "yadm.ssh-perms" "false"

  #; run perms
  run "${T_YADM_Y[@]}" perms

  #; validate status and output
  [ "$status" -eq 0 ]
  [ "$output" = "" ]

  #; validate permissions
  validate_perms gpg
}

@test "Command 'perms' (gpg-perms=false)" {
  echo "
    When the command 'perms' is provided
    And yadm.gpg-perms=false
    Update permissions for ssh only
    Verify correct permissions
    Exit with 0
  "

  #; configure yadm.gpg-perms
  git config --file="$T_YADM_CONFIG" "yadm.gpg-perms" "false"

  #; run perms
  run "${T_YADM_Y[@]}" perms

  #; validate status and output
  [ "$status" -eq 0 ]
  [ "$output" = "" ]

  #; validate permissions
  validate_perms ssh
}

@test "Command 'auto-perms' (enabled)" {
  echo "
    When a command possibly changes the repo
    Update permissions for ssh/gpg
    Verify correct permissions
  "

  #; run status
  run "${T_YADM_Y[@]}" status

  #; validate status
  [ "$status" -eq 0 ]

  #; validate permissions
  validate_perms ssh gpg
}

@test "Command 'auto-perms' (disabled)" {
  echo "
    When a command possibly changes the repo
    And yadm.auto-perms=false
    Take no action
    Verify permissions are intact
  "

  #; configure yadm.auto-perms
  git config --file="$T_YADM_CONFIG" "yadm.auto-perms" "false"

  #; run status
  run "${T_YADM_Y[@]}" status

  #; validate status
  [ "$status" -eq 0 ]

  #; validate permissions
  validate_perms
}
