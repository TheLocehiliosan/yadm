
#; common fixtures
function load_fixtures() {
  export DEFAULT_YADM_DIR="$HOME/.yadm"
  export DEFAULT_REPO="repo.git"
  export DEFAULT_CONFIG="config"
  export DEFAULT_ENCRYPT="encrypt"
  export DEFAULT_ARCHIVE="files.gpg"

  export T_YADM="$PWD/yadm"
  export T_TMP="$BATS_TMPDIR/ytmp"
  export T_DIR_YADM="$T_TMP/.yadm"
  export T_DIR_WORK="$T_TMP/yadm-work"
  export T_DIR_REPO="$T_DIR_YADM/repo.git"
  export T_YADM_CONFIG="$T_DIR_YADM/config"
  export T_YADM_ENCRYPT="$T_DIR_YADM/encrypt"
  export T_YADM_ARCHIVE="$T_DIR_YADM/files.gpg"

  export T_YADM_Y
  T_YADM_Y=( "$T_YADM" -Y "$T_DIR_YADM" )

  export T_SYS
  T_SYS=$(uname -s)
  export T_HOST
  T_HOST=$(hostname -s)
  export T_USER
  T_USER=$(id -u -n)
}

function configure_git() {
  (git config user.name  || git config --global user.name  'test') >/dev/null
  (git config user.email || git config --global user.email 'test@test.test') > /dev/null
}

function make_parents() {
  local parent_dir
  parent_dir=$(dirname "$@")
  mkdir -p "$parent_dir"
}

function test_perms() {
  local test_path="$1"
  local regex="$2"
  local ls
  ls=$(ls -ld "$test_path")
  local perms="${ls:0:10}"
  if [[ ! $perms =~ $regex ]]; then
    echo "ERROR: Found permissions $perms for $test_path"
    return 1
  fi
  return 0
}

function test_repo_attribute() {
  local repo_dir="$1"
  local attribute="$2"
  local expected="$3"
  local actual
  actual=$(GIT_DIR="$repo_dir" git config --local "$attribute")
  if [ "$actual" != "$expected" ]; then
    echo "ERROR: repo attribute $attribute set to $actual"
    return 1
  fi
  return 0
}

#; create worktree at path
function create_worktree() {
  local DIR_WORKTREE="$1"
  if [ -z "$DIR_WORKTREE" ]; then
    echo "ERROR: create_worktree() called without a path"
    return 1
  fi

  if [[ ! "$DIR_WORKTREE" =~ ^$T_TMP ]]; then
    echo "ERROR: create_worktree() called with a path outside of $T_TMP"
    return 1
  fi

  #; remove any existing data
  rm -rf "$DIR_WORKTREE"

  #; create some standard files
  for f in                             \
    "alt-none##S"                      \
    "alt-none##S.H"                    \
    "alt-none##S.H.U"                  \
    "alt-base##"                       \
    "alt-base##S"                      \
    "alt-base##S.H"                    \
    "alt-base##S.H.U"                  \
    "alt-system##"                     \
    "alt-system##S"                    \
    "alt-system##S.H"                  \
    "alt-system##S.H.U"                \
    "alt-system##$T_SYS"               \
    "alt-host##"                       \
    "alt-host##S"                      \
    "alt-host##S.H"                    \
    "alt-host##S.H.U"                  \
    "alt-host##$T_SYS.$T_HOST"         \
    "alt-user##"                       \
    "alt-user##S"                      \
    "alt-user##S.H"                    \
    "alt-user##S.H.U"                  \
    "alt-user##$T_SYS.$T_HOST.$T_USER" \
    .bash_profile                      \
    .gnupg/gpg.conf                    \
    .gnupg/pubring.gpg                 \
    .gnupg/secring.gpg                 \
    .hammerspoon/init.lua              \
    .ssh/config                        \
    .ssh/secret.key                    \
    .ssh/secret.pub                    \
    .tmux.conf                         \
    .vimrc                             \
  ;
  do
    make_parents "$DIR_WORKTREE/$f"
    echo "$f" > "$DIR_WORKTREE/$f"
  done

  #; change all perms (so permission updates can be observed)
  find "$DIR_WORKTREE" -exec chmod 0777 '{}' ';'

}

#; create a repo in T_DIR_REPO
function build_repo() {
  local files_to_add=( "$@" )

  #; create a worktree
  create_worktree "$T_DIR_WORK"

  #; remove the repo if it exists
  if [ -e "$T_DIR_REPO" ]; then
    rm -rf "$T_DIR_REPO"
  fi

  #; create the repo
  git init --shared=0600 --bare "$T_DIR_REPO" >/dev/null 2>&1

  #; standard repo config
  GIT_DIR="$T_DIR_REPO" git config core.bare 'false'
  GIT_DIR="$T_DIR_REPO" git config core.worktree "$T_DIR_WORK"
  GIT_DIR="$T_DIR_REPO" git config status.showUntrackedFiles no
  GIT_DIR="$T_DIR_REPO" git config yadm.managed 'true'

  if [ ${#files_to_add[@]} -ne 0 ]; then
    for f in "${files_to_add[@]}"; do
      GIT_DIR="$T_DIR_REPO" git add "$T_DIR_WORK/$f" >/dev/null
    done
    GIT_DIR="$T_DIR_REPO" git commit -m 'Create repo template' >/dev/null
  fi

}

#; remove all tmp files
function destroy_tmp() {
  load_fixtures
  rm -rf "$T_TMP"
}

configure_git
