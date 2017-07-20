load common
load_fixtures
status=;output=; #; populated by bats run()

IN_REPO=(alt*)
export TEST_TREE_WITH_CYGWIN=1
export SIMULATED_CYGWIN="CYGWIN_NT-6.1-WOW64"

setup() {
  destroy_tmp
  build_repo "${IN_REPO[@]}"
}

test_alt() {
  local cygwin_copy="$1"
  local is_cygwin="$2"
  local expect_link="$3"
  local preexisting_link="$4"

  case "$cygwin_copy" in
    true|false)
      git config --file="$T_YADM_CONFIG" "yadm.cygwin-copy" "$cygwin_copy"
      ;;
  esac

  if [ "$is_cygwin" = "true" ]; then
    echo '#!/bin/sh' > "$T_TMP/uname"
    echo "echo $SIMULATED_CYGWIN" >> "$T_TMP/uname"
    chmod a+x "$T_TMP/uname"
  fi

  local expected_content
  expected_content="$T_DIR_WORK/alt-test##$(PATH="$T_TMP:$PATH" uname -s)"

  if [ "$preexisting_link" = 'symlink' ]; then
    ln -s "$expected_content" "$T_DIR_WORK/alt-test"
  elif [ "$preexisting_link" = 'file' ]; then
    touch "$T_DIR_WORK/alt-test"
  fi

  PATH="$T_TMP:$PATH" run "${T_YADM_Y[@]}" alt

  echo "Alt output:$output"
  echo "Alt status:$status"

  if [ -L "$T_DIR_WORK/alt-test" ] && [ "$expect_link" != 'true' ] ; then
    echo "ERROR: Alt should be a simple file, but isn't"
    return 1
  fi
  if [ ! -L "$T_DIR_WORK/alt-test" ] && [ "$expect_link" = 'true' ] ; then
    echo "ERROR: Alt should use symlink, but doesn't"
    return 1
  fi

  if ! diff "$T_DIR_WORK/alt-test" "$expected_content"; then
    echo "ERROR: Alt contains different data than expected"
    return 1
  fi
}

@test "Option 'yadm.cygwin-copy' (unset, non-cygwin)" {
  echo "
    When the option 'yadm.cygwin-copy' is unset
    and the OS is not CYGWIN
    Verify alternate is a symlink
  "
  test_alt 'unset' 'false' 'true'
}

@test "Option 'yadm.cygwin-copy' (true, non-cygwin)" {
  echo "
    When the option 'yadm.cygwin-copy' is true
    and the OS is not CYGWIN
    Verify alternate is a symlink
  "
  test_alt 'true' 'false' 'true'
}

@test "Option 'yadm.cygwin-copy' (false, non-cygwin)" {
  echo "
    When the option 'yadm.cygwin-copy' is false
    and the OS is not CYGWIN
    Verify alternate is a symlink
  "
  test_alt 'false' 'false' 'true'
}

@test "Option 'yadm.cygwin-copy' (unset, cygwin)" {
  echo "
    When the option 'yadm.cygwin-copy' is unset
    and the OS is CYGWIN
    Verify alternate is a symlink
  "
  test_alt 'unset' 'true' 'true'
}

@test "Option 'yadm.cygwin-copy' (true, cygwin)" {
  echo "
    When the option 'yadm.cygwin-copy' is true
    and the OS is CYGWIN
    Verify alternate is a copy
  "
  test_alt 'true' 'true' 'false'
}

@test "Option 'yadm.cygwin-copy' (false, cygwin)" {
  echo "
    When the option 'yadm.cygwin-copy' is false
    and the OS is CYGWIN
    Verify alternate is a symlink
  "
  test_alt 'false' 'true' 'true'
}

@test "Option 'yadm.cygwin-copy' (preexisting symlink) " {
  echo "
    When the option 'yadm.cygwin-copy' is true
    and the OS is CYGWIN
    Verify alternate is a copy
  "
  test_alt 'true' 'true' 'false' 'symlink'
}

@test "Option 'yadm.cygwin-copy' (preexisting file) " {
  echo "
    When the option 'yadm.cygwin-copy' is true
    and the OS is CYGWIN
    Verify alternate is a copy
  "
  test_alt 'true' 'true' 'false' 'file'
}
