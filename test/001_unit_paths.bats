load common
load_fixtures

function configuration_test() {
  # shellcheck source=/dev/null
  YADM_TEST=1 source "$T_YADM"
  status=0
  output=$( process_global_args "$@" ) || {
    status=$?
    true
  }
  if [ "$status" == 0 ]; then
    process_global_args "$@"
    configure_paths
  fi

  echo -e "STATUS:$status\nOUTPUT:$output"
  echo "CONFIGURED PATHS:"
  echo "      YADM_DIR:$YADM_DIR"
  echo "     YADM_REPO:$YADM_REPO"
  echo "   YADM_CONFIG:$YADM_CONFIG"
  echo "  YADM_ENCRYPT:$YADM_ENCRYPT"
  echo "  YADM_ARCHIVE:$YADM_ARCHIVE"
  echo "YADM_BOOTSTRAP:$YADM_BOOTSTRAP"
  echo "       GIT_DIR:$GIT_DIR"
}

@test "Default paths" {
  echo "
    Default paths should be defined
          YADM_DIR=$DEFAULT_YADM_DIR
         YADM_REPO=$DEFAULT_YADM_DIR/$DEFAULT_REPO
       YADM_CONFIG=$DEFAULT_YADM_DIR/$DEFAULT_CONFIG
      YADM_ENCRYPT=$DEFAULT_YADM_DIR/$DEFAULT_ENCRYPT
      YADM_ARCHIVE=$DEFAULT_YADM_DIR/$DEFAULT_ARCHIVE
    YADM_BOOTSTRAP=$DEFAULT_YADM_DIR/$DEFAULT_BOOTSTRAP
           GIT_DIR=$DEFAULT_YADM_DIR/$DEFAULT_REPO
  "

  configuration_test

  [ "$status" == 0 ]
  [ "$YADM_DIR" = "$HOME/.yadm" ]
  [ "$YADM_REPO" = "$DEFAULT_YADM_DIR/$DEFAULT_REPO" ]
  [ "$YADM_CONFIG" = "$DEFAULT_YADM_DIR/$DEFAULT_CONFIG" ]
  [ "$YADM_ENCRYPT" = "$DEFAULT_YADM_DIR/$DEFAULT_ENCRYPT" ]
  [ "$YADM_ARCHIVE" = "$DEFAULT_YADM_DIR/$DEFAULT_ARCHIVE" ]
  [ "$YADM_BOOTSTRAP" = "$DEFAULT_YADM_DIR/$DEFAULT_BOOTSTRAP" ]
  [ "$GIT_DIR" = "$DEFAULT_YADM_DIR/$DEFAULT_REPO" ]
}

@test "Override YADM_DIR" {
  echo "
    Override YADM_DIR using -Y $T_DIR_YADM
    YADM_DIR should become $T_DIR_YADM
  "

  TEST_ARGS=(-Y $T_DIR_YADM)
  configuration_test "${TEST_ARGS[@]}"

  [ "$status" == 0 ]
  [ "$YADM_DIR" = "$T_DIR_YADM" ]
  [ "$YADM_REPO" = "$T_DIR_YADM/$DEFAULT_REPO" ]
  [ "$YADM_CONFIG" = "$T_DIR_YADM/$DEFAULT_CONFIG" ]
  [ "$YADM_ENCRYPT" = "$T_DIR_YADM/$DEFAULT_ENCRYPT" ]
  [ "$YADM_ARCHIVE" = "$T_DIR_YADM/$DEFAULT_ARCHIVE" ]
  [ "$YADM_BOOTSTRAP" = "$T_DIR_YADM/$DEFAULT_BOOTSTRAP" ]
  [ "$GIT_DIR" = "$T_DIR_YADM/$DEFAULT_REPO" ]
}

@test "Override YADM_DIR (not fully-qualified)" {
  echo "
    Override YADM_DIR using -Y 'relative/path'
    yadm should fail, and report the error
  "

  TEST_ARGS=(-Y relative/path)
  configuration_test "${TEST_ARGS[@]}"

  [ "$status" == 1 ]
  [[ "$output" =~ must\ specify\ a\ fully\ qualified ]]
}

@test "Override YADM_REPO" {
  echo "
    Override YADM_REPO using --yadm-repo /custom/repo
    YADM_REPO should become /custom/repo
    GIT_DIR should become /custom/repo
  "

  TEST_ARGS=(--yadm-repo /custom/repo)
  configuration_test "${TEST_ARGS[@]}"

  [ "$YADM_REPO" = "/custom/repo" ]
  [ "$GIT_DIR"  = "/custom/repo" ]
}

@test "Override YADM_REPO (not fully qualified)" {
  echo "
    Override YADM_REPO using --yadm-repo relative/repo
    yadm should fail, and report the error
  "

  TEST_ARGS=(--yadm-repo relative/repo)
  configuration_test "${TEST_ARGS[@]}"

  [ "$status" == 1 ]
  [[ "$output" =~ must\ specify\ a\ fully\ qualified ]]
}

@test "Override YADM_CONFIG" {
  echo "
    Override YADM_CONFIG using --yadm-config /custom/config
    YADM_CONFIG should become /custom/config
  "

  TEST_ARGS=(--yadm-config /custom/config)
  configuration_test "${TEST_ARGS[@]}"

  [ "$YADM_CONFIG" = "/custom/config" ]
}

@test "Override YADM_CONFIG (not fully qualified)" {
  echo "
    Override YADM_CONFIG using --yadm-config relative/config
    yadm should fail, and report the error
  "

  TEST_ARGS=(--yadm-config relative/config)
  configuration_test "${TEST_ARGS[@]}"

  [ "$status" == 1 ]
  [[ "$output" =~ must\ specify\ a\ fully\ qualified ]]
}

@test "Override YADM_ENCRYPT" {
  echo "
    Override YADM_ENCRYPT using --yadm-encrypt /custom/encrypt
    YADM_ENCRYPT should become /custom/encrypt
  "

  TEST_ARGS=(--yadm-encrypt /custom/encrypt)
  configuration_test "${TEST_ARGS[@]}"

  [ "$YADM_ENCRYPT" = "/custom/encrypt" ]
}

@test "Override YADM_ENCRYPT (not fully qualified)" {
  echo "
    Override YADM_ENCRYPT using --yadm-encrypt relative/encrypt
    yadm should fail, and report the error
  "

  TEST_ARGS=(--yadm-encrypt relative/encrypt)
  configuration_test "${TEST_ARGS[@]}"

  [ "$status" == 1 ]
  [[ "$output" =~ must\ specify\ a\ fully\ qualified ]]
}

@test "Override YADM_ARCHIVE" {
  echo "
    Override YADM_ARCHIVE using --yadm-archive /custom/archive
    YADM_ARCHIVE should become /custom/archive
  "

  TEST_ARGS=(--yadm-archive /custom/archive)
  configuration_test "${TEST_ARGS[@]}"

  [ "$YADM_ARCHIVE" = "/custom/archive" ]
}

@test "Override YADM_ARCHIVE (not fully qualified)" {
  echo "
    Override YADM_ARCHIVE using --yadm-archive relative/archive
    yadm should fail, and report the error
  "

  TEST_ARGS=(--yadm-archive relative/archive)
  configuration_test "${TEST_ARGS[@]}"

  [ "$status" == 1 ]
  [[ "$output" =~ must\ specify\ a\ fully\ qualified ]]
}

@test "Override YADM_BOOTSTRAP" {
  echo "
    Override YADM_BOOTSTRAP using --yadm-bootstrap /custom/bootstrap
    YADM_BOOTSTRAP should become /custom/bootstrap
  "

  TEST_ARGS=(--yadm-bootstrap /custom/bootstrap)
  configuration_test "${TEST_ARGS[@]}"

  [ "$YADM_BOOTSTRAP" = "/custom/bootstrap" ]
}

@test "Override YADM_BOOTSTRAP (not fully qualified)" {
  echo "
    Override YADM_BOOTSTRAP using --yadm-bootstrap relative/bootstrap
    yadm should fail, and report the error
  "

  TEST_ARGS=(--yadm-bootstrap relative/bootstrap)
  configuration_test "${TEST_ARGS[@]}"

  [ "$status" == 1 ]
  [[ "$output" =~ must\ specify\ a\ fully\ qualified ]]
}
