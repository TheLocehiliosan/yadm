load common
load_fixtures
status=;output=; #; populated by bats run()

T_SECTION="test"
T_ATTRIB="attribute"
T_KEY="$T_SECTION.$T_ATTRIB"
T_VALUE="testvalue"
T_EXPECTED="[$T_SECTION]\n\t$T_ATTRIB = $T_VALUE"

setup() {
  destroy_tmp
}

@test "Command 'config' (no parameters)" {
  echo "
    When 'config' command is provided alone,
    Produce instructions about supported configuration options
    Exit with 1
  "

  #; run config
  run "${T_YADM_Y[@]}" config

  #; validate status and output
  [ $status -eq 0 ]
  [[ "$output" =~ Please\ read\ the\ CONFIGURATION\ section ]]
}

@test "Command 'config' (read missing)" {
  echo "
    When 'config' command is provided,
      and an attribute is provided
      and the attribute isn't configured
    Report an empty value
    Exit with 0
  "

  #; run config
  run "${T_YADM_Y[@]}" config $T_KEY

  #; validate status and output
  [ $status -eq 0 ]
  [ "$output" = "" ]
}

@test "Command 'config' (write)" {
  echo "
    When 'config' command is provided,
      and an attribute is provided
      and a value is provided
    Report no output
    Update configuration file
    Exit with 0
  "

  #; run config
  run "${T_YADM_Y[@]}" config "$T_KEY" "$T_VALUE"

  #; validate status and output
  [ $status -eq 0 ]
  [ "$output" = "" ]

  #; validate configuration
  local config
  config=$(cat "$T_YADM_CONFIG")
  local expected
  expected=$(echo -e "$T_EXPECTED")
  if [ "$config" != "$expected" ]; then
    echo "ERROR: Config does not match expected"
    echo "$config"
    return 1
  fi
}

@test "Command 'config' (read)" {
  echo "
    When 'config' command is provided,
      and an attribute is provided
      and the attribute is configured
    Report the requested value
    Exit with 0
  "

  #; manually load a value into the configuration
  make_parents "$T_YADM_CONFIG"
  echo -e "$T_EXPECTED" > "$T_YADM_CONFIG"

  #; run config
  run "${T_YADM_Y[@]}" config "$T_KEY"

  #; validate status and output
  [ $status -eq 0 ]
  if [ "$output" != "$T_VALUE" ]; then
    echo "ERROR: Incorrect value returned. Expected '$T_VALUE', got '$output'"
    return 1
  fi
}

@test "Command 'config' (update)" {
  echo "
    When 'config' command is provided,
      and an attribute is provided
      and the attribute is already configured
    Report no output
    Update configuration file
    Exit with 0
  "

  #; manually load a value into the configuration
  make_parents "$T_YADM_CONFIG"
  echo -e "${T_EXPECTED}_with_extra_data" > "$T_YADM_CONFIG"

  #; run config
  run "${T_YADM_Y[@]}" config "$T_KEY" "$T_VALUE"

  #; validate status and output
  [ $status -eq 0 ]
  [ "$output" = "" ]

  #; validate configuration
  local config
  config=$(cat "$T_YADM_CONFIG")
  local expected
  expected=$(echo -e "$T_EXPECTED")
  if [ "$config" != "$expected" ]; then
    echo "ERROR: Config does not match expected"
    echo "$config"
    return 1
  fi
}

@test "Command 'config' (local read)" {
  echo "
    When 'config' command is provided,
      and an attribute is provided
      and the attribute is configured
      and the attribute is local.*
    Fetch the value from the repo config
    Report the requested value
    Exit with 0
  "

  #; write local attributes
  build_repo
  for loption in class os hostname user; do
    GIT_DIR="$T_DIR_REPO" git config "local.$loption" "custom_$loption"
  done

  #; run config
  for loption in class os hostname user; do
    run "${T_YADM_Y[@]}" config "local.$loption"
    #; validate status and output
    [ $status -eq 0 ]
    if [ "$output" != "custom_$loption" ]; then
      echo "ERROR: Incorrect value returned. Expected 'custom_$loption', got '$output'"
      return 1
    fi
  done

}

@test "Command 'config' (local write)" {
  echo "
    When 'config' command is provided,
      and an attribute is provided
      and a value is provided
      and the attribute is local.*
    Report no output
    Write the value to the repo config
    Exit with 0
  "

  build_repo
  local expected
  local linecount
  expected="[local]\n"
  linecount=1
  for loption in class os hostname user; do
    #; update expected
    expected="$expected\t$loption = custom_$loption\n"
    ((linecount+=1))
    #; write local attributes
    run "${T_YADM_Y[@]}" config "local.$loption" "custom_$loption"

    #; validate status and output
    [ $status -eq 0 ]
    [ "$output" = "" ]
  done

  #; validate data
  local config
  config=$(tail "-$linecount" "$T_DIR_REPO/config")
  expected=$(echo -ne "$expected")
  if [ "$config" != "$expected" ]; then
    echo "ERROR: Config does not match expected"
    echo -e "$config"
    echo -e "EXPECTED:\n$expected"
    return 1
  fi

}
