load common
load_fixtures
status=;output=; #; populated by bats run()

IN_REPO=(alt* "dir one")
export TEST_TREE_WITH_ALT=1
EXCLUDED_NAME="excluded-base"

function create_encrypt() {
  for efile in "encrypted-base##" "encrypted-system##$T_SYS" "encrypted-host##$T_SYS.$T_HOST" "encrypted-user##$T_SYS.$T_HOST.$T_USER"; do
    echo "$efile" >> "$T_YADM_ENCRYPT"
    echo "$efile" >> "$T_DIR_WORK/$efile"
    mkdir -p "$T_DIR_WORK/dir one/$efile"
    echo "dir one/$efile/file1" >> "$T_YADM_ENCRYPT"
    echo "dir one/$efile/file1" >> "$T_DIR_WORK/dir one/$efile/file1"
  done

  echo "$EXCLUDED_NAME##"  >> "$T_YADM_ENCRYPT"
  echo "!$EXCLUDED_NAME##" >> "$T_YADM_ENCRYPT"
  echo "$EXCLUDED_NAME##"  >> "$T_DIR_WORK/$EXCLUDED_NAME##"
}

setup() {
  destroy_tmp
  build_repo "${IN_REPO[@]}"
  create_encrypt
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
    encrypted_base)
      link_name="encrypted-base"
      link_match="$link_name##"
    ;;
    encrypted_system)
      link_name="encrypted-system"
      link_match="$link_name##$T_SYS"
    ;;
    encrypted_host)
      link_name="encrypted-host"
      link_match="$link_name##$T_SYS.$T_HOST"
    ;;
    encrypted_user)
      link_name="encrypted-user"
      link_match="$link_name##$T_SYS.$T_HOST.$T_USER"
    ;;
    override_system)
      link_name="alt-override-system"
      link_match="$link_name##custom_system"
    ;;
    override_host)
      link_name="alt-override-host"
      link_match="$link_name##$T_SYS.custom_host"
    ;;
    override_user)
      link_name="alt-override-user"
      link_match="$link_name##$T_SYS.$T_HOST.custom_user"
    ;;
    class_aaa)
      link_name="alt-system"
      link_match="$link_name##aaa"
    ;;
    class_zzz)
      link_name="alt-system"
      link_match="$link_name##zzz"
    ;;
    class_AAA)
      link_name="alt-system"
      link_match="$link_name##AAA"
    ;;
    class_ZZZ)
      link_name="alt-system"
      link_match="$link_name##ZZZ"
    ;;
  esac
  dir_link_name="dir one/${link_name}"
  dir_link_match="dir one/${link_match}"

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
    echo "TEST:Link Name:$link_name"
    echo "TEST:DIR Link Name:$dir_link_name"
    if [ "$status" != 0 ] || [[ ! "$output" =~ Linking.+$link_name ]] || [[ ! "$output" =~ Linking.+$dir_link_name ]]; then
      echo "OUTPUT:$output"
      echo "STATUS:$status"
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

  if [ -L "$T_DIR_WORK/$EXCLUDED_NAME" ] ; then
    echo "ERROR: Found link: $T_DIR_WORK/$EXCLUDED_NAME"
    echo "ERROR: Excluded files should not be linked"
    return 1
  fi

  #; validate link content
  if [[ "$alt_type" =~ none ]] || [ "$auto_alt" = "false" ]; then
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
      echo "link_content: $link_content"
      echo "dir_link_content: $dir_link_content"
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

@test "Command 'alt' (select class - aaa)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##CLASS - aaa
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  GIT_DIR="$T_DIR_REPO" git config local.class aaa

  test_alt 'class_aaa' 'false' ''
}

@test "Command 'alt' (select class - zzz)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##CLASS - zzz
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  GIT_DIR="$T_DIR_REPO" git config local.class zzz

  test_alt 'class_zzz' 'false' ''
}

@test "Command 'alt' (select class - AAA)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##CLASS - AAA
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  GIT_DIR="$T_DIR_REPO" git config local.class AAA

  test_alt 'class_AAA' 'false' ''
}

@test "Command 'alt' (select class - ZZZ)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##CLASS - ZZZ
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  GIT_DIR="$T_DIR_REPO" git config local.class ZZZ

  test_alt 'class_ZZZ' 'false' ''
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

@test "Command 'alt' (select encrypted base)" {
  echo "
    When the command 'alt' is provided
    and encrypted file matches only ##
    Report the linking
    Verify correct encrypted file is linked
    Exit with 0
  "

  test_alt 'encrypted_base' 'false' ''
}

@test "Command 'alt' (select encrypted system)" {
  echo "
    When the command 'alt' is provided
    and encrypted file matches only ##SYSTEM
    Report the linking
    Verify correct encrypted file is linked
    Exit with 0
  "

  test_alt 'encrypted_system' 'false' ''
}

@test "Command 'alt' (select encrypted host)" {
  echo "
    When the command 'alt' is provided
    and encrypted file matches only ##SYSTEM.HOST
    Report the linking
    Verify correct encrypted file is linked
    Exit with 0
  "

  test_alt 'encrypted_host' 'false' ''
}

@test "Command 'alt' (select encrypted user)" {
  echo "
    When the command 'alt' is provided
    and encrypted file matches only ##SYSTEM.HOST.USER
    Report the linking
    Verify correct encrypted file is linked
    Exit with 0
  "

  test_alt 'encrypted_user' 'false' ''
}

@test "Command 'alt' (select encrypted none)" {
  echo "
    When the command 'alt' is provided
    and no encrypted file matches
    Verify there is no link
    Exit with 0
  "

  test_alt 'encrypted_none' 'false' ''
}

@test "Command 'alt' (override-system)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##SYSTEM
    after setting local.os
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  GIT_DIR="$T_DIR_REPO" git config local.os custom_system
  test_alt 'override_system' 'false' ''
}

@test "Command 'alt' (override-host)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##SYSTEM.HOST
    after setting local.hostname
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  GIT_DIR="$T_DIR_REPO" git config local.hostname custom_host
  test_alt 'override_host' 'false' ''
}

@test "Command 'alt' (override-user)" {
  echo "
    When the command 'alt' is provided
    and file matches only ##SYSTEM.HOST.USER
    after setting local.user
    Report the linking
    Verify correct file is linked
    Exit with 0
  "

  GIT_DIR="$T_DIR_REPO" git config local.user custom_user
  test_alt 'override_user' 'false' ''
}
