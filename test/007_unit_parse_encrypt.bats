load common
load_fixtures

setup() {
  # SC2153 is intentional
  # shellcheck disable=SC2153
  make_parents "$T_YADM_ENCRYPT"
  make_parents "$T_DIR_WORK"
  make_parents "$T_DIR_REPO"
  mkdir "$T_DIR_WORK"
  git init --shared=0600 --bare "$T_DIR_REPO" >/dev/null 2>&1
  GIT_DIR="$T_DIR_REPO" git config core.bare 'false'
  GIT_DIR="$T_DIR_REPO" git config core.worktree "$T_DIR_WORK"
  GIT_DIR="$T_DIR_REPO" git config yadm.managed 'true'
}

teardown() {
  destroy_tmp
}

function run_parse() {
  # shellcheck source=/dev/null
  YADM_TEST=1 source "$T_YADM"
  YADM_ENCRYPT="$T_YADM_ENCRYPT"
  export YADM_ENCRYPT
  GIT_DIR="$T_DIR_REPO"
  export GIT_DIR

  # shellcheck disable=SC2034

  status=0
  { output=$( parse_encrypt) && parse_encrypt; } || {
    status=$?
    true
  }

  if [ "$1" == "twice" ]; then
    GIT_DIR="$T_DIR_REPO" parse_encrypt
  fi

  echo -e "OUTPUT:$output\n"
  echo "ENCRYPT_INCLUDE_FILES:"
  echo "   Size: ${#ENCRYPT_INCLUDE_FILES[@]}"
  echo "  Items: ${ENCRYPT_INCLUDE_FILES[*]}"
  echo "EXPECT_INCLUDE:"
  echo "   Size: ${#EXPECT_INCLUDE[@]}"
  echo "  Items: ${EXPECT_INCLUDE[*]}"
}

@test "parse_encrypt (not called)" {
  echo "
    parse_encrypt() is not called
    Array should be 'unparsed'
  "

  # shellcheck source=/dev/null
  YADM_TEST=1 source "$T_YADM"

  echo "ENCRYPT_INCLUDE_FILES=$ENCRYPT_INCLUDE_FILES"

  [ "$ENCRYPT_INCLUDE_FILES"    == "unparsed" ]

}

@test "parse_encrypt (short-circuit)" {
  echo "
    Parsing should not happen more than once
  "

  run_parse "twice"
  echo "PARSE_ENCRYPT_SHORT: $PARSE_ENCRYPT_SHORT"

  [ "$status" == 0 ]
  [ "$output" == "" ]
  [[ "$PARSE_ENCRYPT_SHORT" =~ not\ reprocessed ]]
}

@test "parse_encrypt (file missing)" {
  echo "
    .yadm/encrypt is empty
    Array should be empty
  "

  EXPECT_INCLUDE=()

  run_parse

  [ "$status" == 0 ]
  [ "$output" == "" ]
  [ "${#ENCRYPT_INCLUDE_FILES[@]}" -eq "${#EXPECT_INCLUDE[@]}" ]
  [ "${ENCRYPT_INCLUDE_FILES[*]}" == "${EXPECT_INCLUDE[*]}" ]
}

@test "parse_encrypt (empty file)" {
  echo "
    .yadm/encrypt is empty
    Array should be empty
  "

  touch "$T_YADM_ENCRYPT"

  EXPECT_INCLUDE=()

  run_parse

  [ "$status" == 0 ]
  [ "$output" == "" ]
  [ "${#ENCRYPT_INCLUDE_FILES[@]}" -eq "${#EXPECT_INCLUDE[@]}" ]
  [ "${ENCRYPT_INCLUDE_FILES[*]}" == "${EXPECT_INCLUDE[*]}" ]
}

@test "parse_encrypt (files)" {
  echo "
    .yadm/encrypt is references present and missing files
    Array should be as expected
  "

  echo "file1" > "$T_DIR_WORK/file1"
  echo "file3" > "$T_DIR_WORK/file3"
  echo "file5" > "$T_DIR_WORK/file5"

  { echo "file1"
    echo "file2"
    echo "file3"
    echo "file4"
    echo "file5"
  } > "$T_YADM_ENCRYPT"

  EXPECT_INCLUDE=("file1" "file3" "file5")

  run_parse

  [ "$status" == 0 ]
  [ "$output" == "" ]
  [ "${#ENCRYPT_INCLUDE_FILES[@]}" -eq "${#EXPECT_INCLUDE[@]}" ]
  [ "${ENCRYPT_INCLUDE_FILES[*]}" == "${EXPECT_INCLUDE[*]}" ]
}

@test "parse_encrypt (files and dirs)" {
  echo "
    .yadm/encrypt is references present and missing files
    .yadm/encrypt is references present and missing dirs
    Array should be as expected
  "

  mkdir -p "$T_DIR_WORK/dir1"
  mkdir -p "$T_DIR_WORK/dir2"
  echo "file1" > "$T_DIR_WORK/file1"
  echo "file2" > "$T_DIR_WORK/file2"
  echo "a"     > "$T_DIR_WORK/dir1/a"
  echo "b"     > "$T_DIR_WORK/dir1/b"

  { echo "file1"
    echo "file2"
    echo "file3"
    echo "dir1"
    echo "dir2"
    echo "dir3"
  } > "$T_YADM_ENCRYPT"

  EXPECT_INCLUDE=("file1" "file2" "dir1" "dir2")

  run_parse

  [ "$status" == 0 ]
  [ "$output" == "" ]
  [ "${#ENCRYPT_INCLUDE_FILES[@]}" -eq "${#EXPECT_INCLUDE[@]}" ]
  [ "${ENCRYPT_INCLUDE_FILES[*]}" == "${EXPECT_INCLUDE[*]}" ]
}

@test "parse_encrypt (comments/empty lines)" {
  echo "
    .yadm/encrypt is references present and missing files
    .yadm/encrypt is references present and missing dirs
    .yadm/encrypt contains comments / blank lines
    Array should be as expected
  "

  mkdir -p "$T_DIR_WORK/dir1"
  mkdir -p "$T_DIR_WORK/dir2"
  echo "file1" > "$T_DIR_WORK/file1"
  echo "file2" > "$T_DIR_WORK/file2"
  echo "file3" > "$T_DIR_WORK/file3"
  echo "a"     > "$T_DIR_WORK/dir1/a"
  echo "b"     > "$T_DIR_WORK/dir1/b"

  { echo "file1"
    echo "file2"
    echo "#file3"
    echo "    #file3"
    echo ""
    echo "dir1"
    echo "dir2"
    echo "dir3"
  } > "$T_YADM_ENCRYPT"

  EXPECT_INCLUDE=("file1" "file2" "dir1" "dir2")

  run_parse

  [ "$status" == 0 ]
  [ "$output" == "" ]
  [ "${#ENCRYPT_INCLUDE_FILES[@]}" -eq "${#EXPECT_INCLUDE[@]}" ]
  [ "${ENCRYPT_INCLUDE_FILES[*]}" == "${EXPECT_INCLUDE[*]}" ]
}

@test "parse_encrypt (w/spaces)" {
  echo "
    .yadm/encrypt is references present and missing files
    .yadm/encrypt is references present and missing dirs
    .yadm/encrypt references contain spaces
    Array should be as expected
  "

  mkdir -p "$T_DIR_WORK/di r1"
  mkdir -p "$T_DIR_WORK/dir2"
  echo "file1"  > "$T_DIR_WORK/file1"
  echo "fi le2" > "$T_DIR_WORK/fi le2"
  echo "file3"  > "$T_DIR_WORK/file3"
  echo "a"      > "$T_DIR_WORK/di r1/a"
  echo "b"      > "$T_DIR_WORK/di r1/b"

  { echo "file1"
    echo "fi le2"
    echo "#file3"
    echo "    #file3"
    echo ""
    echo "di r1"
    echo "dir2"
    echo "dir3"
  } > "$T_YADM_ENCRYPT"

  EXPECT_INCLUDE=("file1" "fi le2" "di r1" "dir2")

  run_parse

  [ "$status" == 0 ]
  [ "$output" == "" ]
  [ "${#ENCRYPT_INCLUDE_FILES[@]}" -eq "${#EXPECT_INCLUDE[@]}" ]
  [ "${ENCRYPT_INCLUDE_FILES[*]}" == "${EXPECT_INCLUDE[*]}" ]
}

@test "parse_encrypt (wildcards)" {
  echo "
    .yadm/encrypt contains wildcards
    Array should be as expected
  "

  mkdir -p "$T_DIR_WORK/di r1"
  mkdir -p "$T_DIR_WORK/dir2"
  echo "file1"  > "$T_DIR_WORK/file1"
  echo "fi le2" > "$T_DIR_WORK/fi le2"
  echo "file2"  > "$T_DIR_WORK/file2"
  echo "file3"  > "$T_DIR_WORK/file3"
  echo "a"      > "$T_DIR_WORK/di r1/a"
  echo "b"      > "$T_DIR_WORK/di r1/b"

  { echo "fi*"
    echo "#file3"
    echo "    #file3"
    echo ""
    echo "#dir2"
    echo "di r1"
    echo "dir2"
    echo "dir3"
  } > "$T_YADM_ENCRYPT"

  EXPECT_INCLUDE=("fi le2" "file1" "file2" "file3" "di r1" "dir2")

  run_parse

  [ "$status" == 0 ]
  [ "$output" == "" ]
  [ "${#ENCRYPT_INCLUDE_FILES[@]}" -eq "${#EXPECT_INCLUDE[@]}" ]
  [ "${ENCRYPT_INCLUDE_FILES[*]}" == "${EXPECT_INCLUDE[*]}" ]
}

@test "parse_encrypt (excludes)" {
  echo "
    .yadm/encrypt contains exclusions
    Array should be as expected
  "

  mkdir -p "$T_DIR_WORK/di r1"
  mkdir -p "$T_DIR_WORK/dir2"
  mkdir -p "$T_DIR_WORK/dir3"
  echo "file1"  > "$T_DIR_WORK/file1"
  echo "file1.ex"  > "$T_DIR_WORK/file1.ex"
  echo "fi le2" > "$T_DIR_WORK/fi le2"
  echo "file3"  > "$T_DIR_WORK/file3"
  echo "test"  > "$T_DIR_WORK/test"
  echo "a.txt"  > "$T_DIR_WORK/di r1/a.txt"
  echo "b.txt"  > "$T_DIR_WORK/di r1/b.txt"
  echo "c.inc"  > "$T_DIR_WORK/di r1/c.inc"

  { echo "fi*"
    echo "#file3"
    echo "    #file3"
    echo ""
    echo " #test"
    echo "#dir2"
    echo "di r1/*"
    echo "dir2"
    echo "dir3"
    echo "dir4"
    echo "!*.ex"
    echo "!di r1/*.txt"
  } > "$T_YADM_ENCRYPT"

  EXPECT_INCLUDE=("fi le2" "file1" "file3" "di r1/c.inc" "dir2" "dir3")

  run_parse

  [ "$status" == 0 ]
  [ "$output" == "" ]
  [ "${#ENCRYPT_INCLUDE_FILES[@]}" -eq "${#EXPECT_INCLUDE[@]}" ]
  [ "${ENCRYPT_INCLUDE_FILES[*]}" == "${EXPECT_INCLUDE[*]}" ]
}
