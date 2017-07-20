
#; common fixtures
function load_fixtures() {
  export DEFAULT_YADM_DIR="$HOME/.yadm"
  export DEFAULT_REPO="repo.git"
  export DEFAULT_CONFIG="config"
  export DEFAULT_ENCRYPT="encrypt"
  export DEFAULT_ARCHIVE="files.gpg"
  export DEFAULT_BOOTSTRAP="bootstrap"

  export T_YADM="$PWD/yadm"
  export T_TMP="$BATS_TMPDIR/ytmp"
  export T_DIR_YADM="$T_TMP/.yadm"
  export T_DIR_WORK="$T_TMP/yadm-work"
  export T_DIR_REPO="$T_DIR_YADM/repo.git"
  export T_DIR_HOOKS="$T_DIR_YADM/hooks"
  export T_YADM_CONFIG="$T_DIR_YADM/config"
  export T_YADM_ENCRYPT="$T_DIR_YADM/encrypt"
  export T_YADM_ARCHIVE="$T_DIR_YADM/files.gpg"
  export T_YADM_BOOTSTRAP="$T_DIR_YADM/bootstrap"

  export T_YADM_Y
  T_YADM_Y=( "$T_YADM" -Y "$T_DIR_YADM" )

  export T_SYS
  T_SYS=$(uname -s)
  export T_HOST
  T_HOST=$(hostname -s)
  export T_USER
  T_USER=$(id -u -n)
  export T_DISTRO
  T_DISTRO=$(lsb_release -si 2>/dev/null || true)
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
  if [ ! -z "$TEST_TREE_WITH_ALT" ] ; then
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
      "alt-system##AAA"                  \
      "alt-system##ZZZ"                  \
      "alt-system##aaa"                  \
      "alt-system##zzz"                  \
      "alt-host##"                       \
      "alt-host##S"                      \
      "alt-host##S.H"                    \
      "alt-host##S.H.U"                  \
      "alt-host##$T_SYS.$T_HOST"         \
      "alt-host##${T_SYS}_${T_HOST}"     \
      "alt-user##"                       \
      "alt-user##S"                      \
      "alt-user##S.H"                    \
      "alt-user##S.H.U"                  \
      "alt-user##$T_SYS.$T_HOST.$T_USER" \
      "alt-user##${T_SYS}_${T_HOST}_${T_USER}" \
      "alt-override-system##"                          \
      "alt-override-system##$T_SYS"                    \
      "alt-override-system##custom_system"             \
      "alt-override-host##"                            \
      "alt-override-host##$T_SYS.$T_HOST"              \
      "alt-override-host##$T_SYS.custom_host"          \
      "alt-override-user##"                            \
      "alt-override-user##S.H.U"                       \
      "alt-override-user##$T_SYS.$T_HOST.custom_user"  \
      "dir one/alt-none##S/file1"                      \
      "dir one/alt-none##S/file2"                      \
      "dir one/alt-none##S.H/file1"                    \
      "dir one/alt-none##S.H/file2"                    \
      "dir one/alt-none##S.H.U/file1"                  \
      "dir one/alt-none##S.H.U/file2"                  \
      "dir one/alt-base##/file1"                       \
      "dir one/alt-base##/file2"                       \
      "dir one/alt-base##S/file1"                      \
      "dir one/alt-base##S/file2"                      \
      "dir one/alt-base##S.H/file1"                    \
      "dir one/alt-base##S.H/file2"                    \
      "dir one/alt-base##S.H.U/file1"                  \
      "dir one/alt-base##S.H.U/file2"                  \
      "dir one/alt-system##/file1"                     \
      "dir one/alt-system##/file2"                     \
      "dir one/alt-system##S/file1"                    \
      "dir one/alt-system##S/file2"                    \
      "dir one/alt-system##S.H/file1"                  \
      "dir one/alt-system##S.H/file2"                  \
      "dir one/alt-system##S.H.U/file1"                \
      "dir one/alt-system##S.H.U/file2"                \
      "dir one/alt-system##$T_SYS/file1"               \
      "dir one/alt-system##$T_SYS/file2"               \
      "dir one/alt-system##AAA/file1"                  \
      "dir one/alt-system##AAA/file2"                  \
      "dir one/alt-system##ZZZ/file1"                  \
      "dir one/alt-system##ZZZ/file2"                  \
      "dir one/alt-system##aaa/file1"                  \
      "dir one/alt-system##aaa/file2"                  \
      "dir one/alt-system##zzz/file1"                  \
      "dir one/alt-system##zzz/file2"                  \
      "dir one/alt-host##/file1"                       \
      "dir one/alt-host##/file2"                       \
      "dir one/alt-host##S/file1"                      \
      "dir one/alt-host##S/file2"                      \
      "dir one/alt-host##S.H/file1"                    \
      "dir one/alt-host##S.H/file2"                    \
      "dir one/alt-host##S.H.U/file1"                  \
      "dir one/alt-host##S.H.U/file2"                  \
      "dir one/alt-host##$T_SYS.$T_HOST/file1"         \
      "dir one/alt-host##$T_SYS.$T_HOST/file2"         \
      "dir one/alt-host##${T_SYS}_${T_HOST}/file1"     \
      "dir one/alt-host##${T_SYS}_${T_HOST}/file2"     \
      "dir one/alt-user##/file1"                       \
      "dir one/alt-user##/file2"                       \
      "dir one/alt-user##S/file1"                      \
      "dir one/alt-user##S/file2"                      \
      "dir one/alt-user##S.H/file1"                    \
      "dir one/alt-user##S.H/file2"                    \
      "dir one/alt-user##S.H.U/file1"                  \
      "dir one/alt-user##S.H.U/file2"                  \
      "dir one/alt-user##$T_SYS.$T_HOST.$T_USER/file1" \
      "dir one/alt-user##$T_SYS.$T_HOST.$T_USER/file2" \
      "dir one/alt-user##${T_SYS}_${T_HOST}_${T_USER}/file1" \
      "dir one/alt-user##${T_SYS}_${T_HOST}_${T_USER}/file2" \
      "dir one/alt-override-system##/file1"                          \
      "dir one/alt-override-system##/file2"                          \
      "dir one/alt-override-system##$T_SYS/file1"                    \
      "dir one/alt-override-system##$T_SYS/file2"                    \
      "dir one/alt-override-system##custom_system/file1"             \
      "dir one/alt-override-system##custom_system/file2"             \
      "dir one/alt-override-host##/file1"                            \
      "dir one/alt-override-host##/file2"                            \
      "dir one/alt-override-host##$T_SYS.$T_HOST/file1"              \
      "dir one/alt-override-host##$T_SYS.$T_HOST/file2"              \
      "dir one/alt-override-host##$T_SYS.custom_host/file1"          \
      "dir one/alt-override-host##$T_SYS.custom_host/file2"          \
      "dir one/alt-override-user##/file1"                            \
      "dir one/alt-override-user##/file2"                            \
      "dir one/alt-override-user##S.H.U/file1"                       \
      "dir one/alt-override-user##S.H.U/file2"                       \
      "dir one/alt-override-user##$T_SYS.$T_HOST.custom_user/file1"  \
      "dir one/alt-override-user##$T_SYS.$T_HOST.custom_user/file2"  \
      "dir2/file2"                                                   \
    ;
    do
      make_parents "$DIR_WORKTREE/$f"
      echo "$f" > "$DIR_WORKTREE/$f"
    done
    echo "{{ YADM_CLASS }}-{{ YADM_OS }}-{{ YADM_HOSTNAME }}-{{ YADM_USER }}-{{ YADM_DISTRO }}" > "$DIR_WORKTREE/alt-jinja##yadm.j2"
  fi

  #; for some cygwin tests
  if [ ! -z "$TEST_TREE_WITH_CYGWIN" ] ; then
    for f in                        \
      "alt-test##"                  \
      "alt-test##$T_SYS"            \
      "alt-test##$SIMULATED_CYGWIN" \
    ;
    do
      make_parents "$DIR_WORKTREE/$f"
      echo "$f" > "$DIR_WORKTREE/$f"
    done
  fi

  if [ ! -z "$TEST_TREE_WITH_WILD" ] ; then
    #; wildcard test data - yes this is a big mess :(
    #; none
    for f in "wild-none##"; do
      make_parents "$DIR_WORKTREE/$f"
      echo "$f" > "$DIR_WORKTREE/$f"
    done
    #; system
    for WILD_S in 'local' 'wild' 'other'; do
      local s_base="wild-system-$WILD_S"
      case $WILD_S in local) WILD_S="$T_SYS";; wild) WILD_S="%";; esac
      local f="${s_base}##${WILD_S}"
      make_parents "$DIR_WORKTREE/$f"
      echo "$f" > "$DIR_WORKTREE/$f"
    done
    #; system.host
    for WILD_S in 'local' 'wild' 'other'; do
      local s_base="wild-host-$WILD_S"
      case $WILD_S in local) WILD_S="$T_SYS";; wild) WILD_S="%";; esac
      for WILD_H in 'local' 'wild' 'other'; do
        local h_base="${s_base}-$WILD_H"
        case $WILD_H in local) WILD_H="$T_HOST";; wild) WILD_H="%";; esac
        local f="${h_base}##${WILD_S}.${WILD_H}"
        make_parents "$DIR_WORKTREE/$f"
        echo "$f" > "$DIR_WORKTREE/$f"
      done
    done
    #; system.host.user
    for WILD_S in 'local' 'wild' 'other'; do
      local s_base="wild-user-$WILD_S"
      case $WILD_S in local) WILD_S="$T_SYS";; wild) WILD_S="%";; esac
      for WILD_H in 'local' 'wild' 'other'; do
        local h_base="${s_base}-$WILD_H"
        case $WILD_H in local) WILD_H="$T_HOST";; wild) WILD_H="%";; esac
        for WILD_U in 'local' 'wild' 'other'; do
          local u_base="${h_base}-$WILD_U"
          case $WILD_U in local) WILD_U="$T_USER";; wild) WILD_U="%";; esac
          local f="${u_base}##${WILD_S}.${WILD_H}.${WILD_U}"
          make_parents "$DIR_WORKTREE/$f"
          echo "$f" > "$DIR_WORKTREE/$f"
        done
      done
    done
    #; class
    for WILD_C in 'local' 'wild' 'other'; do
      local c_base="wild-class-$WILD_C"
      case $WILD_C in local) WILD_C="set_class";; wild) WILD_C="%";; esac
      local f="${c_base}##${WILD_C}"
      make_parents "$DIR_WORKTREE/$f"
      echo "$f" > "$DIR_WORKTREE/$f"
    done
    #; class.system
    for WILD_C in 'local' 'wild' 'other'; do
      local c_base="wild-class-system-$WILD_C"
      case $WILD_C in local) WILD_C="set_class";; wild) WILD_C="%";; esac
      for WILD_S in 'local' 'wild' 'other'; do
        local s_base="${c_base}-$WILD_S"
        case $WILD_S in local) WILD_S="$T_SYS";; wild) WILD_S="%";; esac
        local f="${s_base}##${WILD_C}.${WILD_S}"
        make_parents "$DIR_WORKTREE/$f"
        echo "$f" > "$DIR_WORKTREE/$f"
      done
    done
    #; class.system.host
    for WILD_C in 'local' 'wild' 'other'; do
      local c_base="wild-class-system-host-$WILD_C"
      case $WILD_C in local) WILD_C="set_class";; wild) WILD_C="%";; esac
      for WILD_S in 'local' 'wild' 'other'; do
        local s_base="${c_base}-$WILD_S"
        case $WILD_S in local) WILD_S="$T_SYS";; wild) WILD_S="%";; esac
        for WILD_H in 'local' 'wild' 'other'; do
          local h_base="${s_base}-$WILD_H"
          case $WILD_H in local) WILD_H="$T_HOST";; wild) WILD_H="%";; esac
          local f="${h_base}##${WILD_C}.${WILD_S}.${WILD_H}"
          make_parents "$DIR_WORKTREE/$f"
          echo "$f" > "$DIR_WORKTREE/$f"
        done
      done
    done
    #; class.system.host.user
    for WILD_C in 'local' 'wild' 'other'; do
      local c_base="wild-class-system-host-user-$WILD_C"
      case $WILD_C in local) WILD_C="set_class";; wild) WILD_C="%";; esac
      for WILD_S in 'local' 'wild' 'other'; do
        local s_base="${c_base}-$WILD_S"
        case $WILD_S in local) WILD_S="$T_SYS";; wild) WILD_S="%";; esac
        for WILD_H in 'local' 'wild' 'other'; do
          local h_base="${s_base}-$WILD_H"
          case $WILD_H in local) WILD_H="$T_HOST";; wild) WILD_H="%";; esac
          for WILD_U in 'local' 'wild' 'other'; do
            local u_base="${h_base}-$WILD_U"
            case $WILD_U in local) WILD_U="$T_USER";; wild) WILD_U="%";; esac
            local f="${u_base}##${WILD_C}.${WILD_S}.${WILD_H}.${WILD_U}"
            make_parents "$DIR_WORKTREE/$f"
            echo "$f" > "$DIR_WORKTREE/$f"
          done
        done
      done
    done
  fi
  for f in                             \
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
    "space test/file one"              \
    "space test/file two"              \
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
