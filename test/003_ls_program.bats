load common
load_fixtures

@test "Default /bin/ls" {
  echo "
    By default, the value of LS_PROGRAM should be /bin/ls
  "

  # shellcheck source=/dev/null
  YADM_TEST=1 source "$T_YADM"
  status=0
  output=$( require_ls; echo "$LS_PROGRAM" ) || {
    status=$?
    true
  }

  echo "output=$output"

  [ "$status" == 0 ]
  [ "$output" = "/bin/ls" ]
}

@test "Fallback on 'ls'" {
  echo "
    When LS_PROGRAM doesn't exist, use 'ls'
  "

  # shellcheck source=/dev/null
  YADM_TEST=1 source "$T_YADM"
  status=0
  LS_PROGRAM="/ls/missing"
  output=$( require_ls; echo "$LS_PROGRAM" ) || {
    status=$?
    true
  }

  echo "output=$output"

  [ "$status" == 0 ]
  [ "$output" = "ls" ]
}

@test "Fail if ls isn't in PATH" {
  echo "
    When LS_PROGRAM doesn't exist, use 'ls'
  "

  # shellcheck source=/dev/null
  YADM_TEST=1 source "$T_YADM"
  status=0
  LS_PROGRAM="/ls/missing"
  savepath="$PATH"
  # shellcheck disable=SC2123
  PATH=
  output=$( require_ls 2>&1; echo "$LS_PROGRAM" ) || {
    status=$?
    true
  }
  PATH="$savepath"

  echo "output=$output"

  [ "$status" != 0 ]
  [[ "$output" =~ functionality\ requires\ .ls.\ to\ be\ installed ]]
}

