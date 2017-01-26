load common
load_fixtures
status=;output=; #; populated by bats run()

IN_REPO=(wild*)
export TEST_TREE_WITH_WILD=1

setup() {
  destroy_tmp
  build_repo "${IN_REPO[@]}"
}

function test_alt() {
  local link_name="$1"
  local link_match="$2"

  #; run yadm alt
  run "${T_YADM_Y[@]}" alt
  #; validate status and output
  if [ "$status" != 0 ] || [[ ! "$output" =~ Linking.+$link_name ]]; then
    echo "OUTPUT:$output"
    echo "ERROR: Could not confirm status and output of alt command"
    return 1;
  fi

  #; correct link should be present
  local link_content
  link_content=$(cat "$T_DIR_WORK/$link_name")
  if [ "$link_content" != "$link_match" ]; then
    echo "OUTPUT:$output"
    echo "ERROR: Link content is not correct"
    return 1
  fi
}

@test "Command 'alt' (wild none)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  test_alt 'wild-none' 'wild-none##'
}

@test "Command 'alt' (wild system)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##SYSTEM
    with possible wildcards
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  for WILD_S in 'local' 'wild'; do
    local s_base="wild-system-$WILD_S"
    case $WILD_S in local) WILD_S="$T_SYS";; wild) WILD_S="%";; esac
    local match="${s_base}##${WILD_S}"
    echo test_alt "$s_base" "$match"
    test_alt "$s_base" "$match"
  done
}

@test "Command 'alt' (wild class)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##CLASS
    with possible wildcards
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  GIT_DIR="$T_DIR_REPO" git config local.class set_class

  for WILD_C in 'local' 'wild'; do
    local c_base="wild-class-$WILD_C"
    case $WILD_C in local) WILD_C="set_class";; wild) WILD_C="%";; esac
    local match="${c_base}##${WILD_C}"
    echo test_alt "$c_base" "$match"
    test_alt "$c_base" "$match"
  done
}

@test "Command 'alt' (wild host)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##SYSTEM.HOST
    with possible wildcards
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  for WILD_S in 'local' 'wild'; do
    local s_base="wild-host-$WILD_S"
    case $WILD_S in local) WILD_S="$T_SYS";; wild) WILD_S="%";; esac
    for WILD_H in 'local' 'wild'; do
      local h_base="${s_base}-$WILD_H"
      case $WILD_H in local) WILD_H="$T_HOST";; wild) WILD_H="%";; esac
      local match="${h_base}##${WILD_S}.${WILD_H}"
      echo test_alt "$h_base" "$match"
      test_alt "$h_base" "$match"
    done
  done
}

@test "Command 'alt' (wild class-system)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##CLASS.SYSTEM
    with possible wildcards
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  GIT_DIR="$T_DIR_REPO" git config local.class set_class

  for WILD_C in 'local' 'wild'; do
    local c_base="wild-class-system-$WILD_C"
    case $WILD_C in local) WILD_C="set_class";; wild) WILD_C="%";; esac
    for WILD_S in 'local' 'wild'; do
      local s_base="${c_base}-$WILD_S"
      case $WILD_S in local) WILD_S="$T_SYS";; wild) WILD_S="%";; esac
      local match="${s_base}##${WILD_C}.${WILD_S}"
      echo test_alt "$s_base" "$match"
      test_alt "$s_base" "$match"
    done
  done
}

@test "Command 'alt' (wild user)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##SYSTEM.HOST.USER
    with possible wildcards
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  for WILD_S in 'local' 'wild'; do
    local s_base="wild-user-$WILD_S"
    case $WILD_S in local) WILD_S="$T_SYS";; wild) WILD_S="%";; esac
    for WILD_H in 'local' 'wild'; do
      local h_base="${s_base}-$WILD_H"
      case $WILD_H in local) WILD_H="$T_HOST";; wild) WILD_H="%";; esac
      for WILD_U in 'local' 'wild'; do
        local u_base="${h_base}-$WILD_U"
        case $WILD_U in local) WILD_U="$T_USER";; wild) WILD_U="%";; esac
        local match="${u_base}##${WILD_S}.${WILD_H}.${WILD_U}"
        echo test_alt "$u_base" "$match"
        test_alt "$u_base" "$match"
      done
    done
  done
}

@test "Command 'alt' (wild class-system-host)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##CLASS.SYSTEM.HOST
    with possible wildcards
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  GIT_DIR="$T_DIR_REPO" git config local.class set_class

  for WILD_C in 'local' 'wild'; do
    local c_base="wild-class-system-host-$WILD_C"
    case $WILD_C in local) WILD_C="set_class";; wild) WILD_C="%";; esac
    for WILD_S in 'local' 'wild'; do
      local s_base="${c_base}-$WILD_S"
      case $WILD_S in local) WILD_S="$T_SYS";; wild) WILD_S="%";; esac
      for WILD_H in 'local' 'wild'; do
        local h_base="${s_base}-$WILD_H"
        case $WILD_H in local) WILD_H="$T_HOST";; wild) WILD_H="%";; esac
        local match="${h_base}##${WILD_C}.${WILD_S}.${WILD_H}"
        echo test_alt "$h_base" "$match"
        test_alt "$h_base" "$match"
      done
    done
  done
}

@test "Command 'alt' (wild class-system-host-user)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##CLASS.SYSTEM.HOST.USER
    with possible wildcards
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  GIT_DIR="$T_DIR_REPO" git config local.class set_class

  for WILD_C in 'local' 'wild'; do
    local c_base="wild-class-system-host-user-$WILD_C"
    case $WILD_C in local) WILD_C="set_class";; wild) WILD_C="%";; esac
    for WILD_S in 'local' 'wild'; do
      local s_base="${c_base}-$WILD_S"
      case $WILD_S in local) WILD_S="$T_SYS";; wild) WILD_S="%";; esac
      for WILD_H in 'local' 'wild'; do
        local h_base="${s_base}-$WILD_H"
        case $WILD_H in local) WILD_H="$T_HOST";; wild) WILD_H="%";; esac
        for WILD_U in 'local' 'wild'; do
          local u_base="${h_base}-$WILD_U"
          case $WILD_U in local) WILD_U="$T_USER";; wild) WILD_U="%";; esac
          local match="${u_base}##${WILD_C}.${WILD_S}.${WILD_H}.${WILD_U}"
          echo test_alt "$u_base" "$match"
          test_alt "$u_base" "$match"
        done
      done
    done
  done
}
