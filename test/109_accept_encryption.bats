load common
load_fixtures

T_PASSWD="ExamplePassword"

setup() {
  #; start fresh
  destroy_tmp

  #; create a worktree & repo
  build_repo

  #; define a YADM_ENCRYPT
  mkdir -p $(dirname "$T_YADM_ENCRYPT")
  echo -e ".ssh/*.key\n.gnupg/*.gpg" > $T_YADM_ENCRYPT

  #; create a YADM_ARCHIVE
  (
    cd $T_DIR_WORK
    for f in $(sort "$T_YADM_ENCRYPT"); do
      tar rf "$T_TMP/build_archive.tar" "$f"
      echo "$f" >> "$T_TMP/archived_files"
    done
  )

  #; encrypt YADM_ARCHIVE
  expect <<EOF >/dev/null
    set timeout 2;
    spawn gpg --yes -c --output "$T_YADM_ARCHIVE" "$T_TMP/build_archive.tar"
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
EOF
}

function validate_archive() {
  #; inventory what's in the archive
  expect <<EOF >/dev/null
    set timeout 2;
    spawn bash -c "(gpg -q -d '$T_YADM_ARCHIVE' || echo 1) | tar t | sort > $T_TMP/archive_list"
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
EOF

  #; inventory what is expected in the archive
  (
    cd $T_DIR_WORK
    for f in $(cat "$T_YADM_ENCRYPT"); do
      echo "$f"
    done | sort > "$T_TMP/expected_list"
  )

  #; compare the archive vs expected
  if ! cmp -s "$T_TMP/archive_list" "$T_TMP/expected_list"; then
    echo "ERROR: Archive does not contain the correct files"
    echo "Contains:"
    cat "$T_TMP/archive_list"
    return 1
  fi
  return 0
}

function validate_extraction() {
  #; test each file which was archived
  for f in $(cat "$T_TMP/archived_files"); do
    local contents=$(cat "$T_DIR_WORK/$f")
    if [ "$contents" != "$f" ]; then
      echo "ERROR: Contents of $T_DIR_WORK/$f is incorrect"
      return 1
    fi
  done
  return 0
}

@test "Command 'encrypt' (missing YADM_ENCRYPT)" {
  echo "
    When 'encrypt' command is provided,
    and YADM_ENCRYPT does not exist
    Report problem
    Exit with 1
  "

  #; remove YADM_ENCRYPT
  rm -f "$T_YADM_ENCRYPT"

  #; run encrypt
  run $T_YADM_Y encrypt

  #; validate status and output
  [ "$status" -eq 1 ]
  [[ "$output" =~ does\ not\ exist ]]
}

@test "Command 'encrypt' (mismatched password)" {
  echo "
    When 'encrypt' command is provided,
    and YADM_ENCRYPT is present
    and the provided passwords do not match
    Report problem
    Exit with 1
  "

  #; remove existing T_YADM_ARCHIVE
  rm -f "$T_YADM_ARCHIVE"

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn $T_YADM_Y encrypt;
    expect "passphrase:" {send "ONE\n"}
    expect "passphrase:" {send "TWO\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
    exit \$value
EOF

  #; validate status and output
  [ "$status" -eq 1 ]
  [[ "$output" =~ invalid\ passphrase ]]
  [[ "$output" =~ Unable\ to\ write ]]
}

@test "Command 'encrypt'" {
  echo "
    When 'encrypt' command is provided,
    and YADM_ENCRYPT is present
    Create YADM_ARCHIVE
    Report the archive created
    Archive should be valid
    Exit with 0
  "

  #; remove existing T_YADM_ARCHIVE
  rm -f "$T_YADM_ARCHIVE"

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn $T_YADM_Y encrypt;
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
    exit \$value
EOF

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Wrote\ new\ file:.+$T_YADM_ARCHIVE ]]

  #; validate the archive
  validate_archive
}

@test "Command 'encrypt' (comments in YADM_ARCHIVE)" {
  echo "
    When 'encrypt' command is provided,
    and YADM_ENCRYPT is present
    Create YADM_ARCHIVE
    Report the archive created
    Archive should be valid
    Exit with 0
  "

  #; remove existing T_YADM_ARCHIVE
  rm -f "$T_YADM_ARCHIVE"

  #; add comment to YADM_ARCHIVE
  local original_encrypt=$(cat "$T_YADM_ENCRYPT")
  echo -e "#.vimrc" >> $T_YADM_ENCRYPT

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn $T_YADM_Y encrypt;
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
    exit \$value
EOF

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Wrote\ new\ file:.+$T_YADM_ARCHIVE ]]

  #; restore comment-free version before valiation
  echo "$original_encrypt" > "$T_YADM_ENCRYPT"

  #; validate the archive
  validate_archive
}

@test "Command 'encrypt' (overwrite)" {
  echo "
    When 'encrypt' command is provided,
    and YADM_ENCRYPT is present
    and YADM_ARCHIVE already exists
    Overwrite YADM_ARCHIVE
    Report the archive created
    Archive should be valid
    Exit with 0
  "

  #; Explictly create an invalid archive
  echo "EXISTING ARCHIVE" > "$T_YADM_ARCHIVE"

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn $T_YADM_Y encrypt;
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
    exit \$value
EOF

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Wrote\ new\ file:.+$T_YADM_ARCHIVE ]]

  #; validate the archive
  validate_archive
}

@test "Command 'decrypt' (missing YADM_ARCHIVE)" {
  echo "
    When 'decrypt' command is provided,
    and YADM_ARCHIVE does not exist
    Report problem
    Exit with 1
  "

  #; remove YADM_ARCHIVE
  rm -f "$T_YADM_ARCHIVE"

  #; run encrypt
  run $T_YADM_Y decrypt

  #; validate status and output
  [ "$status" -eq 1 ]
  [[ "$output" =~ does\ not\ exist ]]
}

@test "Command 'decrypt' (wrong password)" {
  echo "
    When 'decrypt' command is provided,
    and YADM_ARCHIVE is present
    and the provided password is wrong
    Report problem
    Exit with 1
  "

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn $T_YADM_Y decrypt;
    expect "passphrase:" {send "WRONG\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
    exit \$value
EOF

  #; validate status and output
  [ "$status" -eq 1 ]
  [[ "$output" =~ decryption\ failed ]]
  [[ "$output" =~ Unable\ to\ extract ]]
}

@test "Command 'decrypt' -l (wrong password)" {
  echo "
    When 'decrypt' command is provided,
    and '-l' is provided,
    and YADM_ARCHIVE is present
    and the provided password is wrong
    Report problem
    Exit with 1
  "

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn $T_YADM_Y decrypt -l;
    expect "passphrase:" {send "WRONG\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
    exit \$value
EOF

  #; validate status and output
  [ "$status" -eq 1 ]
  [[ "$output" =~ decryption\ failed ]]
  [[ "$output" =~ Unable\ to\ extract ]]
}

@test "Command 'decrypt'" {
  echo "
    When 'decrypt' command is provided,
    and YADM_ARCHIVE is present
    Report the data created
    Data should be valid
    Exit with 0
  "

  #; empty the worktree
  rm -rf "$T_DIR_WORK"
  mkdir -p "$T_DIR_WORK"

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn $T_YADM_Y decrypt;
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
    exit \$value
EOF

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ All\ files\ decrypted ]]

  #; validate the extracted files
  validate_extraction
}

@test "Command 'decrypt' (overwrite)" {
  echo "
    When 'decrypt' command is provided,
    and YADM_ARCHIVE is present
    and archived content already exists
    Report the data overwritten
    Data should be valid
    Exit with 0
  "

  #; alter the values of the archived files
  for f in $(cat "$T_TMP/archived_files"); do
    echo "changed" >> "$T_DIR_WORK/$f"
  done

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn $T_YADM_Y decrypt;
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
    exit \$value
EOF

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ All\ files\ decrypted ]]

  #; validate the extracted files
  validate_extraction
}

@test "Command 'decrypt' -l" {
  echo "
    When 'decrypt' command is provided,
    and '-l' is provided,
    and YADM_ARCHIVE is present
    Report the contents of YADM_ARCHIVE
    Exit with 0
  "

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn $T_YADM_Y decrypt -l;
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
    exit \$value
EOF

  #; validate status
  [ "$status" -eq 0 ]

  #; validate every file is listed in output
  for f in $(cat "$T_TMP/archived_files"); do
    if [[ ! "$output" =~ $f ]]; then
      echo "ERROR: Did not find '$f' in output"
      return 1
    fi
  done

}
