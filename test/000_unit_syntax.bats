load common
load_fixtures

@test "Syntax check" {
  echo "
    $T_YADM must parse correctly
  "

  #; check the syntax of yadm
  bash -n "$T_YADM"
}
