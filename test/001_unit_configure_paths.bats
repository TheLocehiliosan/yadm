load common
load_fixtures

@test "configure_paths() (standard YADM_DIR)" {
  echo "
    Correct paths should be defined
         YADM_REPO=$DEFAULT_YADM_DIR/$DEFAULT_REPO
       YADM_CONFIG=$DEFAULT_YADM_DIR/$DEFAULT_CONFIG
      YADM_ENCRYPT=$DEFAULT_YADM_DIR/$DEFAULT_ENCRYPT
      YADM_ARCHIVE=$DEFAULT_YADM_DIR/$DEFAULT_ARCHIVE
           GIT_DIR=$DEFAULT_YADM_DIR/$DEFAULT_REPO
  "

  # shellcheck source=/dev/null

  #; load yadm functions
  YADM_TEST=1 source "$T_YADM"

  #; configure the paths
  configure_paths

  echo "CONFIGURED PATHS:"
  echo "   YADM_REPO:$YADM_REPO"
  echo " YADM_CONFIG:$YADM_CONFIG"
  echo "YADM_ENCRYPT:$YADM_ENCRYPT"
  echo "YADM_ARCHIVE:$YADM_ARCHIVE"
  echo "     GIT_DIR:$GIT_DIR"

  #; test value of configured paths
  [ "$DEFAULT_YADM_DIR/$DEFAULT_REPO" = "$YADM_REPO" ]
  [ "$DEFAULT_YADM_DIR/$DEFAULT_CONFIG" = "$YADM_CONFIG" ]
  [ "$DEFAULT_YADM_DIR/$DEFAULT_ENCRYPT" = "$YADM_ENCRYPT" ]
  [ "$DEFAULT_YADM_DIR/$DEFAULT_ARCHIVE" = "$YADM_ARCHIVE" ]
  [ "$DEFAULT_YADM_DIR/$DEFAULT_REPO" = "$GIT_DIR" ]
}

@test "configure_paths() (custom YADM_DIR)" {
  echo "
    Correct paths should be defined
         YADM_REPO=$T_DIR_YADM/$DEFAULT_REPO
       YADM_CONFIG=$T_DIR_YADM/$DEFAULT_CONFIG
      YADM_ENCRYPT=$T_DIR_YADM/$DEFAULT_ENCRYPT
      YADM_ARCHIVE=$T_DIR_YADM/$DEFAULT_ARCHIVE
           GIT_DIR=$T_DIR_YADM/$DEFAULT_REPO
  "

  # shellcheck source=/dev/null

  #; load yadm functions
  YADM_TEST=1 source "$T_YADM"

  #; configure the paths
  TEST_ARGS=(-Y $T_DIR_YADM)
  process_global_args "${TEST_ARGS[@]}"
  configure_paths

  echo "CONFIGURED PATHS:"
  echo "   YADM_REPO:$YADM_REPO"
  echo " YADM_CONFIG:$YADM_CONFIG"
  echo "YADM_ENCRYPT:$YADM_ENCRYPT"
  echo "YADM_ARCHIVE:$YADM_ARCHIVE"
  echo "     GIT_DIR:$GIT_DIR"

  #; test value of configured paths
  [ "$T_DIR_YADM/$DEFAULT_REPO" = "$YADM_REPO" ]
  [ "$T_DIR_YADM/$DEFAULT_CONFIG" = "$YADM_CONFIG" ]
  [ "$T_DIR_YADM/$DEFAULT_ENCRYPT" = "$YADM_ENCRYPT" ]
  [ "$T_DIR_YADM/$DEFAULT_ARCHIVE" = "$YADM_ARCHIVE" ]
  [ "$T_DIR_YADM/$DEFAULT_REPO" = "$GIT_DIR" ]
}
