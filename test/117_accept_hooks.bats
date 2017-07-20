load common
load_fixtures
status=;output=; #; populated by bats run()

version_regex="yadm [[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+"

setup() {
  destroy_tmp
  build_repo
  mkdir -p "$T_DIR_HOOKS"
}

function create_hook() {
  hook_name="$1"
  hook_exit="$2"
  hook_file="$T_DIR_HOOKS/$hook_name"
  {
    echo "#!/bin/sh"
    echo "echo ran $hook_name"
    echo "env"
    echo "exit $hook_exit"
  } > "$hook_file"
  chmod a+x "$hook_file"
}

@test "Hooks (no hook)" {
  echo "
    When no hook is present
      do no not run the hook
      run command
      Exit with 0
  "

  #; run yadm with no command
  run "${T_YADM_Y[@]}" version

  [ $status -eq 0 ]
  [[ "$output" =~ $version_regex ]]
}

@test "Hooks (successful pre hook)" {
  echo "
    When hook is present
      run hook
      run command
      Exit with 0
  "

  create_hook "pre_version" "0"

  #; run yadm with no command
  run "${T_YADM_Y[@]}" version

  [ $status -eq 0 ]
  [[ "$output" =~ ran\ pre_version ]]
  [[ "$output" =~ $version_regex ]]
}

@test "Hooks (unsuccessful pre hook)" {
  echo "
    When hook is present
      run hook
      report hook failure
      do no not run command
      Exit with 13
  "

  create_hook "pre_version" "13"

  #; run yadm with no command
  run "${T_YADM_Y[@]}" version

  [ $status -eq 13 ]
  [[ "$output" =~ ran\ pre_version ]]
  [[ "$output" =~ pre_version\ was\ not\ successful ]]
  [[ ! "$output" =~ $version_regex ]]
}

@test "Hooks (successful post hook)" {
  echo "
    When hook is present
      run command
      run hook
      Exit with 0
  "

  create_hook "post_version" "0"

  #; run yadm with no command
  run "${T_YADM_Y[@]}" version

  [ $status -eq 0 ]
  [[ "$output" =~ $version_regex ]]
  [[ "$output" =~ ran\ post_version ]]
}

@test "Hooks (unsuccessful post hook)" {
  echo "
    When hook is present
      run command
      run hook
      Exit with 0
  "

  create_hook "post_version" "13"

  #; run yadm with no command
  run "${T_YADM_Y[@]}" version

  [ $status -eq 0 ]
  [[ "$output" =~ $version_regex ]]
  [[ "$output" =~ ran\ post_version ]]
}

@test "Hooks (successful pre hook + post hook)" {
  echo "
    When hook is present
      run hook
      run command
      run hook
      Exit with 0
  "

  create_hook "pre_version" "0"
  create_hook "post_version" "0"

  #; run yadm with no command
  run "${T_YADM_Y[@]}" version

  [ $status -eq 0 ]
  [[ "$output" =~ ran\ pre_version ]]
  [[ "$output" =~ $version_regex ]]
  [[ "$output" =~ ran\ post_version ]]
}

@test "Hooks (unsuccessful pre hook + post hook)" {
  echo "
    When hook is present
      run hook
      report hook failure
      do no not run command
      do no not run post hook
      Exit with 13
  "

  create_hook "pre_version" "13"
  create_hook "post_version" "0"

  #; run yadm with no command
  run "${T_YADM_Y[@]}" version

  [ $status -eq 13 ]
  [[ "$output" =~ ran\ pre_version ]]
  [[ "$output" =~ pre_version\ was\ not\ successful ]]
  [[ ! "$output" =~ $version_regex ]]
  [[ ! "$output" =~ ran\ post_version ]]
}

@test "Hooks (environment variables)" {
  echo "
    When hook is present
      run command
      run hook
      hook should have access to environment variables
      Exit with 0
  "

  create_hook "post_version" "0"

  #; run yadm with no command
  run "${T_YADM_Y[@]}" version extra_args

  [ $status -eq 0 ]
  [[ "$output" =~ $version_regex ]]
  [[ "$output" =~ ran\ post_version ]]
  [[ "$output" =~ YADM_HOOK_COMMAND=version ]]
  [[ "$output" =~ YADM_HOOK_EXIT=0 ]]
  [[ "$output" =~ YADM_HOOK_FULL_COMMAND=version\ extra_args ]]
  [[ "$output" =~ YADM_HOOK_REPO=${T_DIR_REPO} ]]
  [[ "$output" =~ YADM_HOOK_WORK=${T_DIR_WORK} ]]
}
