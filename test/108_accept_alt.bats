load common
load_fixtures

IN_REPO=(alt*)

setup() {
  destroy_tmp
  build_repo "${IN_REPO[@]}"
}

function test_alt() {
  local alt_type="$1"
  local auto_alt="$2"

  #; detemine test parameters
  case $alt_type in
    base)
      link_name="alt-base"
      link_match="$link_name##"
    ;;
    system)
      link_name="alt-system"
      link_match="$link_name##$T_SYS"
    ;;
    host)
      link_name="alt-host"
      link_match="$link_name##$T_SYS.$T_HOST"
    ;;
    user)
      link_name="alt-user"
      link_match="$link_name##$T_SYS.$T_HOST.$T_USER"
    ;;
  esac

  #; verify link doesn't already exist
  if [ -L "$T_DIR_WORK/$link_name" ]; then
    echo "ERROR: Link already exists before running yadm"
    return 1
  fi

  #; configure yadm.auto_alt=false
  if [ "$auto_alt" = "false" ]; then
    git config --file="$T_YADM_CONFIG" yadm.auto-alt false
  fi

  #; run yadm (alt or status)
  if [ -z "$auto_alt" ]; then
    run $T_YADM_Y alt
    #; validate status and output
    if [ "$status" != 0 ] || [[ ! "$output" =~ Linking.+$link_name ]]; then
      echo "ERROR: Could not confirm status and output of alt command"
      return 1;
    fi
  else
    #; running any passed through Git command should trigger auto-alt
    run $T_YADM_Y status
    if [ ! -z "$auto_alt" ] && [[ "$output" =~ Linking.+$link_name ]]; then
      echo "ERROR: Reporting of link should not happen"
      return 1
    fi
  fi

  #; validate link content
  if [ "$alt_type" = "none" ] || [ "$auto_alt" = "false" ]; then
    #; no link should be present
    if [ -L "$T_DIR_WORK/$link_name" ]; then
      echo "ERROR: Link should not exist"
      return 1
    fi
  else
    #; correct link should be present
    local link_content=$(cat "$T_DIR_WORK/$link_name")
    if [ "$link_content" != "$link_match" ]; then
      echo "ERROR: Link content is not correct"
      return 1
    fi
  fi
}

@test "Command 'alt' (select base)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  test_alt 'base' ""
}

@test "Command 'alt' (select system)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##SYSTEM
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  test_alt 'system' ""
}

@test "Command 'alt' (select host)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##SYSTEM.HOST
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  test_alt 'host' ""
}

@test "Command 'alt' (select user)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##SYSTEM.HOST.USER
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  test_alt 'user' ""
}

@test "Command 'alt' (select none)" {
  echo "
    When the command 'alt' is provided
    and no file matches
    Verify there is no link
    Exit with 0
  "

  test_alt 'none' ""
}

@test "Command 'auto-alt' (enabled)" {
  echo "
    When a command possibly changes the repo
    and auto-alt is configured true
    automatically process alternates
    report no linking (not loud)
    verify alternate created
  "

  test_alt 'base' "true"
}

@test "Command 'auto-alt' (disabled)" {
  echo "
    When a command possibly changes the repo
    and auto-alt is configured false
    do no linking
    verify no links
  "

  test_alt 'base' "false"
}
