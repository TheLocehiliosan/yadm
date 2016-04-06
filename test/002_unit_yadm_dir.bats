load common
load_fixtures

@test "Default YADM_DIR" {
  echo "
    YADM_DIR should default to \$HOME/.yadm
  "

  # shellcheck source=/dev/null

  #; load yadm functions
  YADM_TEST=1 source "$T_YADM"

  #; test value of YADM_DIR
  [ "$HOME/.yadm" = "$YADM_DIR" ]
}

@test "Override default YADM_DIR" {
  echo "
    Override YADM_DIR using -Y $T_DIR_YADM
    YADM_DIR should become $T_DIR_YADM
  "

  # shellcheck source=/dev/null

  #; load yadm functions
  YADM_TEST=1 source "$T_YADM"

  #; call process_global_args() with -Y
  TEST_ARGS=(-Y $T_DIR_YADM)
  process_global_args "${TEST_ARGS[@]}"

  #; test value of YADM_DIR
  [ "$T_DIR_YADM" = "$YADM_DIR" ]
}
