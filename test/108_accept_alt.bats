load common
load_fixtures
status=;output=; #; populated by bats run()

IN_REPO=(alt* dir1)

setup() {
  destroy_tmp
  build_repo "${IN_REPO[@]}"
}

function test_alt() {
  local alt_type="$1"
  local test_overwrite="$2"
  local auto_alt="$3"

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
  dir_link_name="dir1/${link_name}"
  dir_link_match="dir1/${link_match}"

  if [ "$test_overwrite" = "true" ]; then
    #; create incorrect links (to overwrite)
    ln -nfs "$T_DIR_WORK/dir2/file2" "$T_DIR_WORK/$link_name"
    ln -nfs "$T_DIR_WORK/dir2"       "$T_DIR_WORK/$dir_link_name"
  else
    #; verify link doesn't already exist
    if [ -L "$T_DIR_WORK/$link_name" ] || [ -L "$T_DIR_WORK/$dir_link_name" ]; then
      echo "ERROR: Link already exists before running yadm"
      return 1
    fi
  fi

  #; configure yadm.auto_alt=false
  if [ "$auto_alt" = "false" ]; then
    git config --file="$T_YADM_CONFIG" yadm.auto-alt false
  fi

  #; run yadm (alt or status)
  if [ -z "$auto_alt" ]; then
    run "${T_YADM_Y[@]}" alt
    #; validate status and output
    if [ "$status" != 0 ] || [[ ! "$output" =~ Linking.+$link_name ]] || [[ ! "$output" =~ Linking.+$dir_link_name ]]; then
      echo "OUTPUT:$output"
      echo "ERROR: Could not confirm status and output of alt command"
      return 1;
    fi
  else
    #; running any passed through Git command should trigger auto-alt
    run "${T_YADM_Y[@]}" status
    if [ -n "$auto_alt" ] && [[ "$output" =~ Linking.+$link_name ]] && [[ "$output" =~ Linking.+$dir_link_name ]]; then
      echo "ERROR: Reporting of link should not happen"
      return 1
    fi
  fi

  #; validate link content
  if [ "$alt_type" = "none" ] || [ "$auto_alt" = "false" ]; then
    #; no link should be present
    if [ -L "$T_DIR_WORK/$link_name" ] || [ -L "$T_DIR_WORK/$dir_link_name" ]; then
      echo "ERROR: Links should not exist"
      return 1
    fi
  else
    #; correct link should be present
    local link_content
    local dir_link_content
    link_content=$(cat "$T_DIR_WORK/$link_name")
    dir_link_content=$(cat "$T_DIR_WORK/$dir_link_name/file1")
    if [ "$link_content" != "$link_match" ] || [ "$dir_link_content" != "$dir_link_match/file1" ]; then
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

  test_alt 'base' 'false' ''
}

@test "Command 'alt' (select system)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##SYSTEM
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  test_alt 'system' 'false' ''
}

@test "Command 'alt' (select host)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##SYSTEM.HOST
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  test_alt 'host' 'false' ''
}

@test "Command 'alt' (select user)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##SYSTEM.HOST.USER
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  test_alt 'user' 'false' ''
}

@test "Command 'alt' (select none)" {
  echo "
    When the command 'alt' is provided
    and no file matches
    Verify there is no link
    Exit with 0
  "

  test_alt 'none' 'false' ''
}

@test "Command 'auto-alt' (enabled)" {
  echo "
    When a command possibly changes the repo
    and auto-alt is configured true
    automatically process alternates
    report no linking (not loud)
    verify alternate created
  "

  test_alt 'base' 'false' 'true'
}

@test "Command 'auto-alt' (disabled)" {
  echo "
    When a command possibly changes the repo
    and auto-alt is configured false
    do no linking
    verify no links
  "

  test_alt 'base' 'false' 'false'
}

@test "Command 'alt' (overwrite existing link)" {
  echo "
    When the command 'alt' is provided
    and the link exists, and is wrong
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  test_alt 'base' 'true' ''
}
