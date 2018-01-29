load common
load_fixtures
status=;output=; #; populated by bats run()

IN_REPO=(.bash_profile .vimrc)

setup() {
  destroy_tmp
  build_repo "${IN_REPO[@]}"
  rm -rf "$T_DIR_WORK"
  mkdir -p "$T_DIR_WORK"
}

@test "Private dirs (private dirs missing)" {
  echo "
    When a git command is run
    And private directories are missing
      Create private directories prior to command
  "

  #; confirm directories are missing at start
  [ ! -e "$T_DIR_WORK/.gnupg" ]
  [ ! -e "$T_DIR_WORK/.ssh" ]

  #; run status
  export DEBUG=yes
  run "${T_YADM_Y[@]}" status

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ On\ branch\ master ]]

  #; confirm private directories are created
  [ -d "$T_DIR_WORK/.gnupg" ]
  test_perms "$T_DIR_WORK/.gnupg" "drwx------"
  [ -d "$T_DIR_WORK/.ssh" ]
  test_perms "$T_DIR_WORK/.ssh" "drwx------"

  #; confirm directories are created before command is run
  [[ "$output" =~ Creating.+/.gnupg/.+Creating.+/.ssh/.+Running\ git\ command\ git\ status ]]
}

@test "Private dirs (private dirs missing / yadm.auto-private-dirs=false)" {
  echo "
    When a git command is run
    And private directories are missing
    But auto-private-dirs is false
      Do not create private dirs
  "

  #; confirm directories are missing at start
  [ ! -e "$T_DIR_WORK/.gnupg" ]
  [ ! -e "$T_DIR_WORK/.ssh" ]

  #; set configuration
  run "${T_YADM_Y[@]}" config --bool "yadm.auto-private-dirs" "false"

  #; run status
  run "${T_YADM_Y[@]}" status

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ On\ branch\ master ]]

  #; confirm private directories are not created
  [ ! -e "$T_DIR_WORK/.gnupg" ]
  [ ! -e "$T_DIR_WORK/.ssh" ]
}

@test "Private dirs (private dirs exist / yadm.auto-perms=false)" {
  echo "
    When a git command is run
    And private directories exist
    And yadm is configured not to auto update perms
      Do not alter directories
  "

  #shellcheck disable=SC2174
  mkdir -m 0777 -p "$T_DIR_WORK/.gnupg" "$T_DIR_WORK/.ssh"

  #; confirm directories are preset and open
  [ -d "$T_DIR_WORK/.gnupg" ]
  test_perms "$T_DIR_WORK/.gnupg" "drwxrwxrwx"
  [ -d "$T_DIR_WORK/.ssh" ]
  test_perms "$T_DIR_WORK/.ssh" "drwxrwxrwx"

  #; set configuration
  run "${T_YADM_Y[@]}" config --bool "yadm.auto-perms" "false"

  #; run status
  run "${T_YADM_Y[@]}" status

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ On\ branch\ master ]]

  #; confirm directories are still preset and open
  [ -d "$T_DIR_WORK/.gnupg" ]
  test_perms "$T_DIR_WORK/.gnupg" "drwxrwxrwx"
  [ -d "$T_DIR_WORK/.ssh" ]
  test_perms "$T_DIR_WORK/.ssh" "drwxrwxrwx"
}
