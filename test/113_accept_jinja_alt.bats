load common
load_fixtures
status=;output=; #; populated by bats run()

IN_REPO=(alt* "dir one")
export TEST_TREE_WITH_ALT=1


setup() {
  destroy_tmp
  build_repo "${IN_REPO[@]}"
  echo "excluded-encrypt##yadm.j2"  > "$T_YADM_ENCRYPT"
  echo "included-encrypt##yadm.j2" >> "$T_YADM_ENCRYPT"
  echo "!excluded-encrypt*"        >> "$T_YADM_ENCRYPT"
  echo "included-encrypt"           > "$T_DIR_WORK/included-encrypt##yadm.j2"
  echo "excluded-encrypt"           > "$T_DIR_WORK/excluded-encrypt##yadm.j2"
}


function test_alt() {
  local alt_type="$1"
  local test_overwrite="$2"
  local auto_alt="$3"

  #; detemine test parameters
  case $alt_type in
    base)
      real_name="alt-jinja"
      file_content_match="-${T_SYS}-${T_HOST}-${T_USER}-${T_DISTRO}"
    ;;
    override_all)
      real_name="alt-jinja"
      file_content_match="custom_class-custom_system-custom_host-custom_user-${T_DISTRO}"
    ;;
    encrypt)
      real_name="included-encrypt"
      file_content_match="included-encrypt"
      missing_name="excluded-encrypt"
    ;;
  esac

  if [ "$test_overwrite" = "true" ] ; then
    #; create incorrect links (to overwrite)
    echo "BAD_CONTENT" "$T_DIR_WORK/$real_name"
  else
    #; verify real file doesn't already exist
    if [ -e "$T_DIR_WORK/$real_name" ] ; then
      echo "ERROR: real file already exists before running yadm"
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
    if [ "$status" != 0 ] || [[ ! "$output" =~ Creating.+$real_name ]]; then
      echo "OUTPUT:$output"
      echo "ERROR: Could not confirm status and output of alt command"
      return 1;
    fi
  else
    #; running any passed through Git command should trigger auto-alt
    run "${T_YADM_Y[@]}" status
    if [ -n "$auto_alt" ] && [[ "$output" =~ Creating.+$real_name ]]; then
      echo "ERROR: Reporting of jinja processing should not happen"
      return 1
    fi
  fi

  if [ -n "$missing_name" ] && [ -f "$T_DIR_WORK/$missing_name" ]; then
      echo "ERROR: File should not have been created '$missing_name'"
      return 1
  fi

  #; validate link content
  if [[ "$alt_type" =~ none ]] || [ "$auto_alt" = "false" ]; then
    #; no real file should be present
    if [ -L "$T_DIR_WORK/$real_name" ] ; then
      echo "ERROR: Real file should not exist"
      return 1
    fi
  else
    #; correct real file should be present
    local file_content
    file_content=$(cat "$T_DIR_WORK/$real_name")
    if [ "$file_content" != "$file_content_match" ]; then
      echo "file_content: ${file_content}"
      echo "expected_content: ${file_content_match}"
      echo "ERROR: Link content is not correct"
      return 1
    fi
  fi
}

@test "Command 'alt' (envtpl missing)" {
  echo "
    When the command 'alt' is provided
    and file matches ##yadm.j2
    Report jinja template as unprocessed
    Exit with 0
  "

  # shellcheck source=/dev/null
  YADM_TEST=1 source "$T_YADM"
  process_global_args -Y "$T_DIR_YADM"
  set_operating_system
  configure_paths

  status=0
  output=$( ENVTPL_PROGRAM='envtpl_missing' main alt ) || {
    status=$?
    true
  }

  [ $status -eq 0 ]
  [[ "$output" =~ envtpl.not.available ]]
}

@test "Command 'alt' (select jinja)" {
  echo "
    When the command 'alt' is provided
    and file matches ##yadm.j2
    Report jinja template processing
    Verify that the correct content is written
    Exit with 0
  "

  test_alt 'base' 'false' ''
}

@test "Command 'auto-alt' (enabled)" {
  echo "
    When a command possibly changes the repo
    and auto-alt is configured true
    and file matches ##yadm.j2
    automatically process alternates
    report no linking (not loud)
    Verify that the correct content is written
  "

  test_alt 'base' 'false' 'true'
}

@test "Command 'auto-alt' (disabled)" {
  echo "
    When a command possibly changes the repo
    and auto-alt is configured false
    and file matches ##yadm.j2
    Report no jinja template processing
    Verify no content
  "

  test_alt 'base' 'false' 'false'
}

@test "Command 'alt' (overwrite existing content)" {
  echo "
    When the command 'alt' is provided
    and file matches ##yadm.j2
    and the real file exists, and is wrong
    Report jinja template processing
    Verify that the correct content is written
    Exit with 0
  "

  test_alt 'base' 'true' ''
}

@test "Command 'alt' (overwritten settings)" {
  echo "
    When the command 'alt' is provided
    and file matches ##yadm.j2
    after setting local.*
    Report jinja template processing
    Verify that the correct content is written
    Exit with 0
  "

  GIT_DIR="$T_DIR_REPO" git config local.os custom_system
  GIT_DIR="$T_DIR_REPO" git config local.user custom_user
  GIT_DIR="$T_DIR_REPO" git config local.hostname custom_host
  GIT_DIR="$T_DIR_REPO" git config local.class custom_class
  test_alt 'override_all' 'false' ''
}

@test "Command 'alt' (select jinja within .yadm/encrypt)" {
  echo "
    When the command 'alt' is provided
    and file matches ##yadm.j2 within .yadm/encrypt
    and file excluded within .yadm/encrypt
    Report jinja template processing
    Verify that the correct content is written
    Exit with 0
  "

  test_alt 'encrypt' 'false' ''
}
