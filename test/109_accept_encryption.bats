load common
load_fixtures
status=;output=; #; populated by bats run()

T_PASSWD="ExamplePassword"
T_ARCHIVE_SYMMETRIC="$T_TMP/build_archive.symmetric"
T_ARCHIVE_ASYMMETRIC="$T_TMP/build_archive.asymmetric"
T_KEY_NAME="yadm-test1"
T_KEY_FINGERPRINT="F8BBFC746C58945442349BCEBA54FFD04C599B1A"
T_RECIPIENT_GOOD="[yadm]\n\tgpg-recipient = yadm-test1"
T_RECIPIENT_BAD="[yadm]\n\tgpg-recipient = invalid"
T_RECIPIENT_ASK="[yadm]\n\tgpg-recipient = ASK"

#; use gpg1 if it's available
T_GPG_PROGRAM="gpg"
if command -v gpg1 >/dev/null 2>&1; then
  T_GPG_PROGRAM="gpg1"
fi

function import_keys() {
  "$T_GPG_PROGRAM" --import "test/test_key" >/dev/null 2>&1 || true
  "$T_GPG_PROGRAM" --import-ownertrust < "test/ownertrust.txt" >/dev/null 2>&1
}

function remove_keys() {
  "$T_GPG_PROGRAM" --batch --yes --delete-secret-keys "$T_KEY_FINGERPRINT" >/dev/null 2>&1 || true
  "$T_GPG_PROGRAM" --batch --yes --delete-key "$T_KEY_FINGERPRINT" >/dev/null 2>&1 || true
}

setup() {
  #; start fresh
  destroy_tmp

  #; import test keys
  import_keys

  #; create a worktree & repo
  build_repo

  #; define a YADM_ENCRYPT
  make_parents "$T_YADM_ENCRYPT"
  echo -e ".ssh/*.key\n.gnupg/*.gpg" > "$T_YADM_ENCRYPT"

  #; create a YADM_ARCHIVE
  (
    if cd "$T_DIR_WORK"; then
      # shellcheck disable=2013
      # (globbing is desired)
      for f in $(sort "$T_YADM_ENCRYPT"); do
        tar rf "$T_TMP/build_archive.tar" "$f"
        echo "$f" >> "$T_TMP/archived_files"
      done
    fi
  )

  #; encrypt YADM_ARCHIVE (symmetric)
  expect <<EOF >/dev/null
    set timeout 2;
    spawn "$T_GPG_PROGRAM" --yes -c --output "$T_ARCHIVE_SYMMETRIC" "$T_TMP/build_archive.tar"
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
EOF

  #; encrypt YADM_ARCHIVE (asymmetric)
  "$T_GPG_PROGRAM" --yes --batch -e -r "$T_KEY_NAME" --output "$T_ARCHIVE_ASYMMETRIC" "$T_TMP/build_archive.tar"

  #; configure yadm to use T_GPG_PROGRAM
  git config --file="$T_YADM_CONFIG" yadm.gpg-program "$T_GPG_PROGRAM"
}

teardown() {
  remove_keys
}

function validate_archive() {
  #; inventory what's in the archive
  if [ "$1" = "symmetric" ]; then
    expect <<EOF >/dev/null
      set timeout 2;
      spawn bash -c "($T_GPG_PROGRAM -q -d '$T_YADM_ARCHIVE' || echo 1) | tar t | sort > $T_TMP/archive_list"
      expect "passphrase:" {send "$T_PASSWD\n"}
      expect "$"
      foreach {pid spawnid os_error_flag value} [wait] break
EOF
  else
    "$T_GPG_PROGRAM" -q -d "$T_YADM_ARCHIVE" | tar t | sort > "$T_TMP/archive_list"
  fi

  excluded="$2"

  #; inventory what is expected in the archive
  (
    if cd "$T_DIR_WORK"; then
      # shellcheck disable=2013
      # (globbing is desired)
      while IFS='' read -r glob || [ -n "$glob" ]; do
        if [[ ! $glob =~ ^# && ! $glob =~ ^[[:space:]]*$ ]] ; then
          if [[ ! $glob =~ ^!(.+) ]] ; then
            local IFS=$'\n'
            for matching_file in $glob; do
              if [ -e "$matching_file" ]; then
                if [ "$matching_file" != "$excluded" ]; then
                  if [ -d "$matching_file" ]; then
                      echo "$matching_file/"
                    for subfile in "$matching_file"/*; do
                      echo "$subfile"
                    done
                  else
                    echo "$matching_file"
                  fi
                fi
              fi
            done
          fi
        fi
      done < "$T_YADM_ENCRYPT" | sort > "$T_TMP/expected_list"
    fi
  )

  #; compare the archive vs expected
  if ! cmp -s "$T_TMP/archive_list" "$T_TMP/expected_list"; then
    echo "ERROR: Archive does not contain the correct files"
    echo "Contains:"
    cat "$T_TMP/archive_list"
    echo "Expected:"
    cat "$T_TMP/expected_list"
    return 1
  fi
  return 0
}

function validate_extraction() {
  #; test each file which was archived
  while IFS= read -r f; do
    local contents
    contents=$(cat "$T_DIR_WORK/$f")
    if [ "$contents" != "$f" ]; then
      echo "ERROR: Contents of $T_DIR_WORK/$f is incorrect"
      return 1
    fi
  done < "$T_TMP/archived_files"
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
  run "${T_YADM_Y[@]}" encrypt

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

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} encrypt;
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

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} encrypt;
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
  validate_archive symmetric
}

@test "Command 'encrypt' (comments in YADM_ENCRYPT)" {
  echo "
    When 'encrypt' command is provided,
    and YADM_ENCRYPT is present
    Create YADM_ARCHIVE
    Report the archive created
    Archive should be valid
    Exit with 0
  "

  #; add comment to YADM_ARCHIVE
  local original_encrypt
  original_encrypt=$(cat "$T_YADM_ENCRYPT")
  echo -e "#.vimrc" >> "$T_YADM_ENCRYPT"

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} encrypt;
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
  validate_archive symmetric
}

@test "Command 'encrypt' (empty lines and space lines in YADM_ENCRYPT)" {
  echo "
    When 'encrypt' command is provided,
    and YADM_ENCRYPT is present
    Create YADM_ARCHIVE
    Report the archive created
    Archive should be valid
    Exit with 0
  "

  #; add empty lines to YADM_ARCHIVE
  local original_encrypt
  original_encrypt=$(cat "$T_YADM_ENCRYPT")
  echo -e " \n\n \n" >> "$T_YADM_ENCRYPT"

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} encrypt;
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
    exit \$value
EOF

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Wrote\ new\ file:.+$T_YADM_ARCHIVE ]]

  #; restore empty-line-free version before valiation
  echo "$original_encrypt" > "$T_YADM_ENCRYPT"

  #; validate the archive
  validate_archive symmetric
}

@test "Command 'encrypt' (paths with spaces/globs in YADM_ENCRYPT)" {
  echo "
    When 'encrypt' command is provided,
    and YADM_ENCRYPT is present
    Create YADM_ARCHIVE
    Report the archive created
    Archive should be valid
    Exit with 0
  "

  #; add paths with spaces to YADM_ARCHIVE
  local original_encrypt
  original_encrypt=$(cat "$T_YADM_ENCRYPT")
  echo -e "space test/file*" >> "$T_YADM_ENCRYPT"

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} encrypt;
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
  validate_archive symmetric
}

@test "Command 'encrypt' (exclusions in YADM_ENCRYPT)" {
  echo "
    When 'encrypt' command is provided,
    and YADM_ENCRYPT is present
    Create YADM_ARCHIVE
    Report the archive created
    Archive should be valid
    Exit with 0
  "

  #; add paths with spaces to YADM_ARCHIVE
  local original_encrypt
  original_encrypt=$(cat "$T_YADM_ENCRYPT")
  echo -e ".ssh/*" >> "$T_YADM_ENCRYPT"
  echo -e "!.ssh/sec*.pub" >> "$T_YADM_ENCRYPT"

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} encrypt;
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
    exit \$value
EOF

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Wrote\ new\ file:.+$T_YADM_ARCHIVE ]]
  [[ ! "$output" =~ \.ssh/secret.pub ]]

  #; validate the archive
  validate_archive symmetric ".ssh/secret.pub"
}

@test "Command 'encrypt' (directories in YADM_ENCRYPT)" {
  echo "
    When 'encrypt' command is provided,
    and YADM_ENCRYPT is present
    Create YADM_ARCHIVE
    Report the archive created
    Archive should be valid
    Exit with 0
  "

  #; add directory paths to YADM_ARCHIVE
  local original_encrypt
  original_encrypt=$(cat "$T_YADM_ENCRYPT")
  echo -e "space test" >> "$T_YADM_ENCRYPT"

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} encrypt;
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
  validate_archive symmetric
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

  #; Explicitly create an invalid archive
  echo "EXISTING ARCHIVE" > "$T_YADM_ARCHIVE"

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} encrypt;
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
  validate_archive symmetric
}

@test "Command 'decrypt' (missing YADM_ARCHIVE)" {
  echo "
    When 'decrypt' command is provided,
    and YADM_ARCHIVE does not exist
    Report problem
    Exit with 1
  "

  #; run decrypt
  run "${T_YADM_Y[@]}" decrypt

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

  #; use the symmetric archive
  cp -f "$T_ARCHIVE_SYMMETRIC" "$T_YADM_ARCHIVE"

  #; run decrypt
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} decrypt;
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

  #; use the symmetric archive
  cp -f "$T_ARCHIVE_SYMMETRIC" "$T_YADM_ARCHIVE"

  #; run decrypt
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} decrypt -l;
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

  #; use the symmetric archive
  cp -f "$T_ARCHIVE_SYMMETRIC" "$T_YADM_ARCHIVE"

  #; empty the worktree
  rm -rf "$T_DIR_WORK"
  mkdir -p "$T_DIR_WORK"

  #; run decrypt
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} decrypt;
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

  #; use the symmetric archive
  cp -f "$T_ARCHIVE_SYMMETRIC" "$T_YADM_ARCHIVE"

  #; alter the values of the archived files
  while IFS= read -r f; do
    echo "changed" >> "$T_DIR_WORK/$f"
  done < "$T_TMP/archived_files"

  #; run decrypt
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} decrypt;
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

  #; use the symmetric archive
  cp -f "$T_ARCHIVE_SYMMETRIC" "$T_YADM_ARCHIVE"

  #; run decrypt
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} decrypt -l;
    expect "passphrase:" {send "$T_PASSWD\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
    exit \$value
EOF

  #; validate status
  [ "$status" -eq 0 ]

  #; validate every file is listed in output
  while IFS= read -r f; do
    if [[ ! "$output" =~ $f ]]; then
      echo "ERROR: Did not find '$f' in output"
      return 1
    fi
  done < "$T_TMP/archived_files"

}

@test "Command 'encrypt' (asymmetric, missing key)" {
  echo "
    When 'encrypt' command is provided,
    and YADM_ENCRYPT is present
    and yadm.gpg-recipient refers to an invalid private key
    Report problem
    Exit with 1
  "

  #; manually set yadm.gpg-recipient in configuration
  make_parents "$T_YADM_CONFIG"
  echo -e "$T_RECIPIENT_BAD" > "$T_YADM_CONFIG"

  #; run encrypt
  run "${T_YADM_Y[@]}" encrypt

  #; validate status and output
  [ "$status" -eq 1 ]
  [[ "$output" =~ public\ key\ not\ found ]] || [[ "$output" =~ No\ public\ key ]]
  [[ "$output" =~ Unable\ to\ write ]]
}


@test "Command 'encrypt' (asymmetric)" {
  echo "
    When 'encrypt' command is provided,
    and YADM_ENCRYPT is present
    and yadm.gpg-recipient refers to a valid private key
    Create YADM_ARCHIVE
    Report the archive created
    Archive should be valid
    Exit with 0
  "

  #; manually set yadm.gpg-recipient in configuration
  make_parents "$T_YADM_CONFIG"
  echo -e "$T_RECIPIENT_GOOD" > "$T_YADM_CONFIG"

  #; run encrypt
  run "${T_YADM_Y[@]}" encrypt

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Wrote\ new\ file:.+$T_YADM_ARCHIVE ]]

  #; validate the archive
  validate_archive asymmetric
}

@test "Command 'encrypt' (asymmetric, overwrite)" {
  echo "
    When 'encrypt' command is provided,
    and YADM_ENCRYPT is present
    and yadm.gpg-recipient refers to a valid private key
    and YADM_ARCHIVE already exists
    Overwrite YADM_ARCHIVE
    Report the archive created
    Archive should be valid
    Exit with 0
  "

  #; manually set yadm.gpg-recipient in configuration
  make_parents "$T_YADM_CONFIG"
  echo -e "$T_RECIPIENT_GOOD" > "$T_YADM_CONFIG"

  #; Explicitly create an invalid archive
  echo "EXISTING ARCHIVE" > "$T_YADM_ARCHIVE"

  #; run encrypt
  run "${T_YADM_Y[@]}" encrypt

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Wrote\ new\ file:.+$T_YADM_ARCHIVE ]]

  #; validate the archive
  validate_archive asymmetric
}

@test "Command 'encrypt' (asymmetric, ask)" {
  echo "
    When 'encrypt' command is provided,
    and YADM_ENCRYPT is present
    and yadm.gpg-recipient is set to ASK
    Ask for recipient
    Create YADM_ARCHIVE
    Report the archive created
    Archive should be valid
    Exit with 0
  "

  #; manually set yadm.gpg-recipient in configuration
  make_parents "$T_YADM_CONFIG"
  echo -e "$T_RECIPIENT_ASK" > "$T_YADM_CONFIG"

  #; run encrypt
  run expect <<EOF
    set timeout 2;
    spawn ${T_YADM_Y[*]} encrypt;
    expect "Enter the user ID" {send "$T_KEY_NAME\n\n"}
    expect "$"
    foreach {pid spawnid os_error_flag value} [wait] break
    exit \$value
EOF

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ Wrote\ new\ file:.+$T_YADM_ARCHIVE ]]

  #; validate the archive
  validate_archive asymmetric
}

@test "Command 'decrypt' (asymmetric, missing YADM_ARCHIVE)" {
  echo "
    When 'decrypt' command is provided,
    and yadm.gpg-recipient refers to a valid private key
    and YADM_ARCHIVE does not exist
    Report problem
    Exit with 1
  "

  #; manually set yadm.gpg-recipient in configuration
  make_parents "$T_YADM_CONFIG"
  echo -e "$T_RECIPIENT_GOOD" > "$T_YADM_CONFIG"

  #; run decrypt
  run "${T_YADM_Y[@]}" decrypt

  #; validate status and output
  [ "$status" -eq 1 ]
  [[ "$output" =~ does\ not\ exist ]]
}

@test "Command 'decrypt' (asymmetric, missing key)" {
  echo "
    When 'decrypt' command is provided,
    and yadm.gpg-recipient refers to a valid private key
    and YADM_ARCHIVE is present
    and the private key is not present
    Report problem
    Exit with 1
  "

  #; manually set yadm.gpg-recipient in configuration
  make_parents "$T_YADM_CONFIG"
  echo -e "$T_RECIPIENT_GOOD" > "$T_YADM_CONFIG"

  #; use the asymmetric archive
  cp -f "$T_ARCHIVE_ASYMMETRIC" "$T_YADM_ARCHIVE"

  #; remove the private key
  remove_keys

  #; run decrypt
  run "${T_YADM_Y[@]}" decrypt

  #; validate status and output
  [ "$status" -eq 1 ]
  [[ "$output" =~ decryption\ failed ]]
  [[ "$output" =~ Unable\ to\ extract ]]
}

@test "Command 'decrypt' -l (asymmetric, missing key)" {
  echo "
    When 'decrypt' command is provided,
    and '-l' is provided,
    and yadm.gpg-recipient refers to a valid private key
    and YADM_ARCHIVE is present
    and the private key is not present
    Report problem
    Exit with 1
  "

  #; manually set yadm.gpg-recipient in configuration
  make_parents "$T_YADM_CONFIG"
  echo -e "$T_RECIPIENT_GOOD" > "$T_YADM_CONFIG"

  #; use the asymmetric archive
  cp -f "$T_ARCHIVE_ASYMMETRIC" "$T_YADM_ARCHIVE"

  #; remove the private key
  remove_keys

  #; run decrypt
  run "${T_YADM_Y[@]}" decrypt

  #; validate status and output
  [ "$status" -eq 1 ]
  [[ "$output" =~ decryption\ failed ]]
  [[ "$output" =~ Unable\ to\ extract ]]
}

@test "Command 'decrypt' (asymmetric)" {
  echo "
    When 'decrypt' command is provided,
    and yadm.gpg-recipient refers to a valid private key
    and YADM_ARCHIVE is present
    Report the data created
    Data should be valid
    Exit with 0
  "

  #; manually set yadm.gpg-recipient in configuration
  make_parents "$T_YADM_CONFIG"
  echo -e "$T_RECIPIENT_GOOD" > "$T_YADM_CONFIG"

  #; use the asymmetric archive
  cp -f "$T_ARCHIVE_ASYMMETRIC" "$T_YADM_ARCHIVE"

  #; empty the worktree
  rm -rf "$T_DIR_WORK"
  mkdir -p "$T_DIR_WORK"

  #; run decrypt
  run "${T_YADM_Y[@]}" decrypt

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ All\ files\ decrypted ]]

  #; validate the extracted files
  validate_extraction
}

@test "Command 'decrypt' (asymmetric, overwrite)" {
  echo "
    When 'decrypt' command is provided,
    and yadm.gpg-recipient refers to a valid private key
    and YADM_ARCHIVE is present
    and archived content already exists
    Report the data overwritten
    Data should be valid
    Exit with 0
  "

  #; manually set yadm.gpg-recipient in configuration
  make_parents "$T_YADM_CONFIG"
  echo -e "$T_RECIPIENT_GOOD" > "$T_YADM_CONFIG"

  #; use the asymmetric archive
  cp -f "$T_ARCHIVE_ASYMMETRIC" "$T_YADM_ARCHIVE"

  #; alter the values of the archived files
  while IFS= read -r f; do
    echo "changed" >> "$T_DIR_WORK/$f"
  done < "$T_TMP/archived_files"

  #; run decrypt
  run "${T_YADM_Y[@]}" decrypt

  #; validate status and output
  [ "$status" -eq 0 ]
  [[ "$output" =~ All\ files\ decrypted ]]

  #; validate the extracted files
  validate_extraction
}

@test "Command 'decrypt' -l (asymmetric)" {
  echo "
    When 'decrypt' command is provided,
    and '-l' is provided,
    and yadm.gpg-recipient refers to a valid private key
    and YADM_ARCHIVE is present
    Report the contents of YADM_ARCHIVE
    Exit with 0
  "

  #; manually set yadm.gpg-recipient in configuration
  make_parents "$T_YADM_CONFIG"
  echo -e "$T_RECIPIENT_GOOD" > "$T_YADM_CONFIG"

  #; use the asymmetric archive
  cp -f "$T_ARCHIVE_ASYMMETRIC" "$T_YADM_ARCHIVE"

  #; run decrypt
  run "${T_YADM_Y[@]}" decrypt -l

  #; validate status
  [ "$status" -eq 0 ]

  #; validate every file is listed in output
  while IFS= read -r f; do
    if [[ ! "$output" =~ $f ]]; then
      echo "ERROR: Did not find '$f' in output"
      return 1
    fi
  done < "$T_TMP/archived_files"

}
