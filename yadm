#!/bin/sh
# yadm - Yet Another Dotfiles Manager
# Copyright (C) 2015-2022 Tim Byrne

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# shellcheck shell=bash
# execute script with bash (shebang line is /bin/sh for portability)
if [ -z "$BASH_VERSION" ]; then
  [ "$YADM_TEST" != 1 ] && exec bash "$0" "$@"
fi

VERSION=3.2.1

YADM_WORK="$HOME"
YADM_DIR=
YADM_DATA=

YADM_LEGACY_DIR="${HOME}/.yadm"
YADM_LEGACY_ARCHIVE="files.gpg"

# these are the default paths relative to YADM_DIR
YADM_CONFIG="config"
YADM_ENCRYPT="encrypt"
YADM_BOOTSTRAP="bootstrap"
YADM_HOOKS="hooks"
YADM_ALT="alt"

# these are the default paths relative to YADM_DATA
YADM_REPO="repo.git"
YADM_ARCHIVE="archive"

HOOK_COMMAND=""
FULL_COMMAND=""

GPG_PROGRAM="gpg"
OPENSSL_PROGRAM="openssl"
GIT_PROGRAM="git"
AWK_PROGRAM=("gawk" "awk")
GIT_CRYPT_PROGRAM="git-crypt"
TRANSCRYPT_PROGRAM="transcrypt"
J2CLI_PROGRAM="j2"
ENVTPL_PROGRAM="envtpl"
ESH_PROGRAM="esh"
LSB_RELEASE_PROGRAM="lsb_release"

OS_RELEASE="/etc/os-release"
PROC_VERSION="/proc/version"
OPERATING_SYSTEM="Unknown"

ENCRYPT_INCLUDE_FILES="unparsed"

LEGACY_WARNING_ISSUED=0
INVALID_ALT=()

GPG_OPTS=()
OPENSSL_OPTS=()

# flag causing path translations with cygpath
USE_CYGPATH=0

# flag when something may have changes (which prompts auto actions to be performed)
CHANGES_POSSIBLE=0

# flag when a bootstrap should be performed after cloning
# 0: skip auto_bootstrap, 1: ask, 2: perform bootstrap, 3: prevent bootstrap
DO_BOOTSTRAP=0

function main() {

  require_git

  # capture full command, for passing to hooks
  # the parameters will be space delimited and
  # spaces, tabs, and backslashes will be escaped
  _tab=$'\t'
  for param in "$@"; do
    param="${param//\\/\\\\}"
    param="${param//$_tab/\\$_tab}"
    param="${param// /\\ }"
    _fc+=( "$param" )
  done
  FULL_COMMAND="${_fc[*]}"

  # create the YADM_DIR & YADM_DATA if they doesn't exist yet
  [ -d "$YADM_DIR" ]  || mkdir -p "$YADM_DIR"
  [ -d "$YADM_DATA" ] || mkdir -p "$YADM_DATA"

  # parse command line arguments
  local retval=0
  internal_commands="^(alt|bootstrap|clean|clone|config|decrypt|encrypt|enter|git-crypt|help|--help|init|introspect|list|perms|transcrypt|upgrade|version|--version)$"
  if [ -z "$*" ] ; then
    # no argumnts will result in help()
    help
  elif [[ "$1" =~ $internal_commands ]] ; then
    # for internal commands, process all of the arguments
    YADM_COMMAND="${1//-/_}"
    YADM_COMMAND="${YADM_COMMAND/__/}"
    YADM_ARGS=()
    shift

    # commands listed below do not process any of the parameters
    if [[ "$YADM_COMMAND" =~ ^(enter|git_crypt)$ ]] ; then
      YADM_ARGS=("$@")
    else
      while [[ $# -gt 0 ]] ; do
        key="$1"
        case $key in
          -a) # used by list()
            LIST_ALL="YES"
          ;;
          -d) # used by all commands
            DEBUG="YES"
          ;;
          -f) # used by init(), clone() and upgrade()
            FORCE="YES"
          ;;
          -l) # used by decrypt()
            DO_LIST="YES"
            [[ "$YADM_COMMAND" =~ ^(clone|config)$ ]] && YADM_ARGS+=("$1")
          ;;
          -w) # used by init() and clone()
            YADM_WORK="$(qualify_path "$2" "work tree")"
            shift
          ;;
          *) # any unhandled arguments
            YADM_ARGS+=("$1")
          ;;
        esac
        shift
      done
    fi
    [ ! -d "$YADM_WORK" ] && error_out "Work tree does not exist: [$YADM_WORK]"
    HOOK_COMMAND="$YADM_COMMAND"
    invoke_hook "pre"
    $YADM_COMMAND "${YADM_ARGS[@]}"
  else
    # any other commands are simply passed through to git
    HOOK_COMMAND="$1"
    invoke_hook "pre"
    git_command "$@"
    retval="$?"
  fi

  # process automatic events
  auto_alt
  auto_perms
  auto_bootstrap

  exit_with_hook $retval

}


# ****** Alternate Processing ******

function score_file() {
  src="$1"
  tgt="${src%%##*}"
  conditions="${src#*##}"

  if [ "${tgt#"$YADM_ALT/"}" != "${tgt}" ]; then
    tgt="${YADM_BASE}/${tgt#"$YADM_ALT/"}"
  fi

  score=0
  IFS=',' read -ra fields <<< "$conditions"
  for field in "${fields[@]}"; do
    label=${field%%.*}
    value=${field#*.}
    [ "$field" = "$label" ] && value="" # when .value is omitted
    # extension isn't a condition and doesn't affect the score
    if [[ "$label" =~ ^(e|extension)$ ]]; then
      continue
    fi
    score=$((score + 1000))
    # default condition
    if [[ "$label" =~ ^(default)$ ]]; then
      score=$((score + 0))
    # variable conditions
    elif [[ "$label" =~ ^(a|arch)$ ]]; then
      if [ "$value" = "$local_arch" ]; then
        score=$((score + 1))
      else
        score=0
        return
      fi
    elif [[ "$label" =~ ^(o|os)$ ]]; then
      if [ "$value" = "$local_system" ]; then
        score=$((score + 2))
      else
        score=0
        return
      fi
    elif [[ "$label" =~ ^(d|distro)$ ]]; then
      if [ "$value" = "$local_distro" ]; then
        score=$((score + 4))
      else
        score=0
        return
      fi
    elif [[ "$label" =~ ^(f|distro_family)$ ]]; then
      if [ "$value" = "$local_distro_family" ]; then
        score=$((score + 8))
      else
        score=0
        return
      fi
    elif [[ "$label" =~ ^(c|class)$ ]]; then
      if in_list "$value" "${local_classes[@]}"; then
        score=$((score + 16))
      else
        score=0
        return
      fi
    elif [[ "$label" =~ ^(h|hostname)$ ]]; then
      if [ "$value" = "$local_host" ]; then
        score=$((score + 32))
      else
        score=0
        return
      fi
    elif [[ "$label" =~ ^(u|user)$ ]]; then
      if [ "$value" = "$local_user" ]; then
        score=$((score + 64))
      else
        score=0
        return
      fi
    # templates
    elif [[ "$label" =~ ^(t|template|yadm)$ ]]; then
      score=0
      cmd=$(choose_template_cmd "$value")
      if [ -n "$cmd" ]; then
        record_template "$tgt" "$cmd" "$src"
      else
        debug "No supported template processor for template $src"
        [ -n "$loud" ] && echo "No supported template processor for template $src"
      fi
      return 0
    # unsupported values
    else
      if [[ "${src##*/}" =~ .\#\#. ]]; then
        INVALID_ALT+=("$src")
      fi
      score=0
      return
    fi
  done

  record_score "$score" "$tgt" "$src"
}

function record_score() {
  score="$1"
  tgt="$2"
  src="$3"

  # record nothing if the score is zero
  [ "$score" -eq 0 ] && return

  # search for the index of this target, to see if we already are tracking it
  index=-1
  for search_index in "${!alt_targets[@]}"; do
    if [ "${alt_targets[$search_index]}" = "$tgt" ]; then
        index="$search_index"
        break
    fi
  done
  # if we don't find an existing index, create one by appending to the array
  if [ "$index" -eq -1 ]; then
    # $YADM_CONFIG must be processed first, in case other templates lookup yadm configurations
    if [ "$tgt" = "$YADM_CONFIG" ]; then
        alt_targets=("$tgt" "${alt_targets[@]}")
        alt_sources=("$src" "${alt_sources[@]}")
        alt_scores=(0 "${alt_scores[@]}")
        index=0
        # increase the index of any existing alt_template_cmds
        new_cmds=()
        for cmd_index in "${!alt_template_cmds[@]}"; do
            new_cmds[$((cmd_index+1))]="${alt_template_cmds[$cmd_index]}"
        done
        alt_template_cmds=()
        for cmd_index in "${!new_cmds[@]}"; do
            alt_template_cmds[$cmd_index]="${new_cmds[$cmd_index]}"
        done
    else
        alt_targets+=("$tgt")
        # set index to the last index (newly created one)
        for index in "${!alt_targets[@]}"; do :; done
        # and set its initial score to zero
        alt_scores[$index]=0
     fi
  fi

  # record nothing if a template command is registered for this file
  [ "${alt_template_cmds[$index]+isset}" ] && return

  # record higher scoring sources
  if [ "$score" -gt "${alt_scores[$index]}" ]; then
    alt_scores[$index]="$score"
    alt_sources[$index]="$src"
  fi

}

function record_template() {
  tgt="$1"
  cmd="$2"
  src="$3"

  # search for the index of this target, to see if we already are tracking it
  index=-1
  for search_index in "${!alt_targets[@]}"; do
    if [ "${alt_targets[$search_index]}" = "$tgt" ]; then
        index="$search_index"
        break
    fi
  done
  # if we don't find an existing index, create one by appending to the array
  if [ "$index" -eq -1 ]; then
    alt_targets+=("$tgt")
    # set index to the last index (newly created one)
    for index in "${!alt_targets[@]}"; do :; done
  fi

  # record the template command, last one wins
  alt_template_cmds[$index]="$cmd"
  alt_sources[$index]="$src"

}

function choose_template_cmd() {
  kind="$1"

  if [ "$kind" = "default" ] || [ "$kind" = "" ] && awk_available; then
    echo "template_default"
  elif [ "$kind" = "esh" ] && esh_available; then
    echo "template_esh"
  elif [ "$kind" = "j2cli" ] || [ "$kind" = "j2" ] && j2cli_available; then
    echo "template_j2cli"
  elif [ "$kind" = "envtpl" ] || [ "$kind" = "j2" ] && envtpl_available; then
    echo "template_envtpl"
  else
    return # this "kind" of template is not supported
  fi

}

# ****** Template Processors ******

function template_default() {
  input="$1"
  output="$2"
  temp_file="${output}.$$.$RANDOM"

  # the explicit "space + tab" character class used below is used because not
  # all versions of awk seem to support the POSIX character classes [[:blank:]]
  read -r -d '' awk_pgm << "EOF"
# built-in default template processor
BEGIN {
  blank              = "[ 	]"
  c["class"]         = class
  c["classes"]       = classes
  c["arch"]          = arch
  c["os"]            = os
  c["hostname"]      = host
  c["user"]          = user
  c["distro"]        = distro
  c["distro_family"] = distro_family
  c["source"]        = source
  ifs                = "^{%" blank "*if"
  els                = "^{%" blank "*else" blank "*%}$"
  end                = "^{%" blank "*endif" blank "*%}$"
  skp                = "^{%" blank "*(if|else|endif)"
  vld                = conditions()
  inc_start          = "^{%" blank "*include" blank "+\"?"
  inc_end            = "\"?" blank "*%}$"
  inc                = inc_start ".+" inc_end
  prt                = 1
  err                = 0
}
END { exit err }
{ replace_vars() } # variable replacements
$0 ~ vld, $0 ~ end {
  if ($0 ~ vld || $0 ~ end) prt=1;
  if ($0 ~ els) prt=0;
  if ($0 ~ skp) next;
}
($0 ~ ifs && $0 !~ vld), $0 ~ end {
  if ($0 ~ ifs && $0 !~ vld) prt=0;
  if ($0 ~ els || $0 ~ end) prt=1;
  if ($0 ~ skp) next;
}
{ if (!prt) next }
$0 ~ inc {
  file = $0
  sub(inc_start, "", file)
  sub(inc_end, "", file)
  sub(/^[^\/].*$/, source_dir "/&", file)

  while ((res = getline <file) > 0) {
    replace_vars()
    print
  }
  if (res < 0) {
    printf "%s:%d: error: could not read '%s'\n", FILENAME, NR, file | "cat 1>&2"
    err = 1
  }
  close(file)
  next
}
{ print }
function replace_vars() {
  for (label in c) {
    gsub(("{{" blank "*yadm\\." label blank "*}}"), c[label])
  }
  for (label in ENVIRON) {
    gsub(("{{" blank "*env\\." label blank "*}}"), ENVIRON[label])
  }
}
function condition_helper(label, value) {
  gsub(/[\\.^$(){}\[\]|*+?]/, "\\\\&", value)
  return sprintf("yadm\\.%s" blank "*==" blank "*\"%s\"", label, value)
}
function conditions() {
  pattern = ifs blank "+("
  for (label in c) {
    if (label != "class") {
      value = c[label]
      pattern = sprintf("%s%s|", pattern, condition_helper(label, value));
    }
  }
  split(classes, cls_array, "\n")
  for (idx in cls_array) {
    value = cls_array[idx]
    pattern = sprintf("%s%s|", pattern, condition_helper("class", value));
  }
  sub(/\|$/, ")" blank "*%}$", pattern)
  return pattern
}
EOF

  "${AWK_PROGRAM[0]}" \
    -v class="$local_class" \
    -v arch="$local_arch" \
    -v os="$local_system" \
    -v host="$local_host" \
    -v user="$local_user" \
    -v distro="$local_distro" \
    -v distro_family="$local_distro_family" \
    -v source="$input" \
    -v source_dir="$(dirname "$input")" \
    -v classes="$(join_string $'\n' "${local_classes[@]}")" \
    "$awk_pgm" \
    "$input" > "$temp_file" || rm -f "$temp_file"

  move_file "$input" "$output" "$temp_file"
}

function template_j2cli() {
  input="$1"
  output="$2"
  temp_file="${output}.$$.$RANDOM"

  YADM_CLASS="$local_class"   \
  YADM_ARCH="$local_arch"     \
  YADM_OS="$local_system"     \
  YADM_HOSTNAME="$local_host" \
  YADM_USER="$local_user"     \
  YADM_DISTRO="$local_distro" \
  YADM_DISTRO_FAMILY="$local_distro_family" \
  YADM_SOURCE="$input"        \
  YADM_CLASSES="$(join_string $'\n' "${local_classes[@]}")" \
  "$J2CLI_PROGRAM" "$input" -o "$temp_file"

  move_file "$input" "$output" "$temp_file"
}

function template_envtpl() {
  input="$1"
  output="$2"
  temp_file="${output}.$$.$RANDOM"

  YADM_CLASS="$local_class"   \
  YADM_ARCH="$local_arch"     \
  YADM_OS="$local_system"     \
  YADM_HOSTNAME="$local_host" \
  YADM_USER="$local_user"     \
  YADM_DISTRO="$local_distro" \
  YADM_DISTRO_FAMILY="$local_distro_family" \
  YADM_SOURCE="$input"        \
  YADM_CLASSES="$(join_string $'\n' "${local_classes[@]}")" \
  "$ENVTPL_PROGRAM" --keep-template "$input" -o "$temp_file"

  move_file "$input" "$output" "$temp_file"
}

function template_esh() {
  input="$1"
  output="$2"
  temp_file="${output}.$$.$RANDOM"

  YADM_CLASSES="$(join_string $'\n' "${local_classes[@]}")" \
  "$ESH_PROGRAM" -o "$temp_file" "$input" \
  YADM_CLASS="$local_class"   \
  YADM_ARCH="$local_arch"     \
  YADM_OS="$local_system"     \
  YADM_HOSTNAME="$local_host" \
  YADM_USER="$local_user"     \
  YADM_DISTRO="$local_distro" \
  YADM_DISTRO_FAMILY="$local_distro_family" \
  YADM_SOURCE="$input"

  move_file "$input" "$output" "$temp_file"
}

function move_file() {
  local input=$1
  local output=$2
  local temp_file=$3

  [ ! -f "$temp_file" ] && return

  # if the output files already exists as read-only, change it to be writable.
  # there are some environments in which a read-only file will prevent the move
  # from being successful.
  [[ -e "$output" && ! -w "$output" ]] && chmod u+w "$output"

  mv -f "$temp_file" "$output"
  copy_perms "$input" "$output"
}

# ****** yadm Commands ******

function alt() {

  require_repo
  parse_encrypt

  # gather values for processing alternates
  local local_class
  local -a local_classes
  local local_arch
  local local_system
  local local_host
  local local_user
  local local_distro
  local local_distro_family
  set_local_alt_values

  # only be noisy if the "alt" command was run directly
  local loud=
  [ "$YADM_COMMAND" = "alt" ] && loud="YES"

  # decide if a copy should be done instead of a symbolic link
  local do_copy=0
  [ "$(config --bool yadm.alt-copy)" == "true" ] && do_copy=1

  cd_work "Alternates" || return

  # determine all tracked files
  local tracked_files=()
  local IFS=$'\n'
  for tracked_file in $("$GIT_PROGRAM" ls-files | LC_ALL=C sort); do
    tracked_files+=("$tracked_file")
  done

  # generate data for removing stale links
  local possible_alts=()
  local IFS=$'\n'
  for possible_alt in "${tracked_files[@]}" "${ENCRYPT_INCLUDE_FILES[@]}"; do
    if [[ $possible_alt =~ .\#\#. ]]; then
      base_alt="${possible_alt%%##*}"
      yadm_alt="${YADM_BASE}/${base_alt}"
      if [ "${yadm_alt#"$YADM_ALT/"}" != "${yadm_alt}" ]; then
        base_alt="${yadm_alt#"$YADM_ALT/"}"
      fi
      possible_alts+=("$YADM_BASE/${base_alt}")
    fi
  done
  local alt_linked=()

  alt_linking
  remove_stale_links
  report_invalid_alts

}

function report_invalid_alts() {
  [ "$LEGACY_WARNING_ISSUED" = "1" ] && return
  [ "${#INVALID_ALT[@]}" = "0" ] && return
  local path_list
  for invalid in "${INVALID_ALT[@]}"; do
    path_list="$path_list    * $invalid"$'\n'
  done
  local msg
  IFS='' read -r -d '' msg <<EOF

**WARNING**
  Invalid alternates have been detected.

  Beginning with version 2.0.0, yadm uses a new naming convention for alternate
  files. Read more about this change here:

    https://yadm.io/docs/upgrade_from_1

  Or to learn more about alternates in general, read:

    https://yadm.io/docs/alternates

  To rename the invalid alternates run:

    yadm mv <old name> <new name>

  Invalid alternates detected:
${path_list}
***********
EOF
    printf '%s\n' "$msg" >&2
}

function remove_stale_links() {
  # review alternate candidates for stale links
  # if a possible alt IS linked, but it's source is not part of alt_linked,
  # remove it.
  if readlink_available; then
    for stale_candidate in "${possible_alts[@]}"; do
      if [ -L "$stale_candidate" ]; then
        src=$(readlink "$stale_candidate" 2>/dev/null)
        if [ -n "$src" ]; then
          for review_link in "${alt_linked[@]}"; do
            [ "$src" = "$review_link" ] && continue 2
          done
          rm -f "$stale_candidate"
        fi
      fi
    done
  fi
}

function set_local_alt_values() {

  local -a all_classes
  all_classes=$(config --get-all local.class)
  while IFS='' read -r class; do
      local_classes+=("$class")
      local_class="$class"
  done <<< "$all_classes"

  local_arch="$(config local.arch)"
  if [ -z "$local_arch" ] ; then
    local_arch=$(uname -m)
  fi

  local_system="$(config local.os)"
  if [ -z "$local_system" ] ; then
    local_system="$OPERATING_SYSTEM"
  fi

  local_host="$(config local.hostname)"
  if [ -z "$local_host" ] ; then
    local_host=$(uname -n)
    local_host=${local_host%%.*} # trim any domain from hostname
  fi

  local_user="$(config local.user)"
  if [ -z "$local_user" ] ; then
    local_user=$(id -u -n)
  fi

  local_distro="$(query_distro)"
  local_distro_family="$(query_distro_family)"

}

function alt_linking() {

  local alt_scores=()
  local alt_targets=()
  local alt_sources=()
  local alt_template_cmds=()

  for alt_path in $(for tracked in "${tracked_files[@]}"; do printf "%s\n" "$tracked" "${tracked%/*}"; done | LC_ALL=C sort -u) "${ENCRYPT_INCLUDE_FILES[@]}"; do
    alt_path="$YADM_BASE/$alt_path"
    if [[ "$alt_path" =~ .\#\#. ]]; then
      if [ -e "$alt_path" ] ; then
        score_file "$alt_path"
      fi
    fi
  done

  for index in "${!alt_targets[@]}"; do
    tgt="${alt_targets[$index]}"
    src="${alt_sources[$index]}"
    template_cmd="${alt_template_cmds[$index]}"
    if [ -n "$template_cmd" ]; then
      # a template is defined, process the template
      debug "Creating $tgt from template $src"
      [ -n "$loud" ] && echo "Creating $tgt from template $src"
      # ensure the destination path exists
      assert_parent "$tgt"
      # remove any existing symlink before processing template
      [ -L "$tgt" ] && rm -f "$tgt"
      "$template_cmd" "$src" "$tgt"
    elif [ -n "$src" ]; then
      # a link source is defined, create symlink
      debug "Linking $src to $tgt"
      [ -n "$loud" ] && echo "Linking $src to $tgt"
      # ensure the destination path exists
      assert_parent "$tgt"
      if [ "$do_copy" -eq 1 ]; then
        # remove any existing symlink before copying
        [ -L "$tgt" ] && rm -f "$tgt"
        cp -f "$src" "$tgt"
      else
        ln_relative "$src" "$tgt"
      fi
    fi
  done

}

function ln_relative() {
  local full_source full_target target_dir
  local full_source="$1"
  local full_target="$2"
  local target_dir="${full_target%/*}"
  if [ "$target_dir" == "" ]; then
    target_dir="/"
  fi
  local rel_source
  rel_source=$(relative_path "$target_dir" "$full_source")
  ln -nfs "$rel_source" "$full_target"
  alt_linked+=("$rel_source")
}

function bootstrap() {

  bootstrap_available || error_out "Cannot execute bootstrap\n'$YADM_BOOTSTRAP' is not an executable program."

  # GIT_DIR should not be set for user's bootstrap code
  unset GIT_DIR

  echo "Executing $YADM_BOOTSTRAP"
  exec "$YADM_BOOTSTRAP"

}

function clean() {

  error_out "\"git clean\" has been disabled for safety. You could end up removing all unmanaged files."

}

function clone() {

  DO_BOOTSTRAP=1
  local -a args
  local -i do_checkout=1
  while [[ $# -gt 0 ]] ; do
    case "$1" in
      --bootstrap) # force bootstrap, without prompt
        DO_BOOTSTRAP=2
      ;;
      --no-bootstrap) # prevent bootstrap, without prompt
        DO_BOOTSTRAP=3
      ;;
      --checkout)
        do_checkout=1
      ;;
      -n|--no-checkout)
        do_checkout=0
      ;;
      --bare|--mirror|--recurse-submodules*|--recursive|--separate-git-dir=*)
        # ignore arguments without separate parameter
      ;;
      --separate-git-dir)
        # ignore arguments with separate parameter
        shift
      ;;
      *)
        args+=("$1")
      ;;
    esac
    shift
  done

  [ -n "$DEBUG" ] && display_private_perms "initial"

  # safety check, don't attempt to clone when the repo is already present
  [ -d "$YADM_REPO" ] && [ -z "$FORCE" ] &&
    error_out "Git repo already exists. [$YADM_REPO]\nUse '-f' if you want to force it to be overwritten."

  # remove existing if forcing the clone to happen anyway
  [ -d "$YADM_REPO" ] && {
    debug "Removing existing repo prior to clone"
    "$GIT_PROGRAM" -C "$YADM_WORK" submodule deinit -f --all
    rm -rf "$YADM_REPO"
  }

  local wc
  wc="$(mk_tmp_dir)"
  [ -d "$wc" ] || error_out "Unable to create temporary directory"

  # first clone without checkout
  debug "Doing an initial clone of the repository"
  (cd "$wc" &&
       "$GIT_PROGRAM" -c core.sharedrepository=0600 clone --no-checkout \
                      --separate-git-dir="$YADM_REPO" "${args[@]}" repo.git) || {
      debug "Removing repo after failed clone"
      rm -rf "$YADM_REPO" "$wc"
      error_out "Unable to clone the repository"
  }
  configure_repo
  rm -rf "$wc"

  # then reset the index as the --no-checkout flag makes the index empty
  "$GIT_PROGRAM" reset --quiet -- .

  if [ "$YADM_WORK" = "$HOME" ]; then
    debug "Determining if repo tracks private directories"
    for private_dir in $(private_dirs all); do
      found_log=$("$GIT_PROGRAM" log -n 1 -- "$private_dir" 2>/dev/null)
      if [ -n "$found_log" ]; then
        debug "Private directory $private_dir is tracked by repo"
        assert_private_dirs "$private_dir"
      fi
    done
  fi

  # finally check out (unless instructed not to) all files that don't exist in $YADM_WORK
  if [[ $do_checkout -ne 0 ]]; then
      [ -n "$DEBUG" ] && display_private_perms "pre-checkout"

      cd_work "Clone" || return

      "$GIT_PROGRAM" ls-files --deleted | while IFS= read -r file; do
          "$GIT_PROGRAM" checkout -- ":/$file"
      done

      if [ -n "$("$GIT_PROGRAM" ls-files --modified)" ]; then
        local msg
        IFS='' read -r -d '' msg <<EOF
**NOTE**
  Local files with content that differs from the ones just
  cloned were found in $YADM_WORK. They have been left
  unmodified.

  Please review and resolve any differences appropriately.
  If you know what you're doing, and want to overwrite the
  tracked files, consider 'yadm checkout "$YADM_WORK"'.
EOF
        printf '%s\n' "$msg"
      fi

      [ -n "$DEBUG" ] && display_private_perms "post-checkout"

      CHANGES_POSSIBLE=1
  fi

}

function config() {

  use_repo_config=0
  local_options="^local\.(class|arch|os|hostname|user)$"
  for option in "$@"; do
    [[ "$option" =~ $local_options ]] && use_repo_config=1
  done

  if [ -z "$*" ] ; then
    # with no parameters, provide some helpful documentation
    echo "yadm supports the following configurations:"
    echo
    local IFS=$'\n'
    for supported_config in $(introspect_configs); do
      echo "  ${supported_config}"
    done
    echo
    local msg
    read -r -d '' msg << EOF
Please read the CONFIGURATION section in the man
page for more details about configurations, and
how to adjust them.
EOF
    printf '%s\n' "$msg"
  elif [ "$use_repo_config" -eq 1 ]; then

    require_repo

    # operate on the yadm repo's configuration file
    # this is always local to the machine
    "$GIT_PROGRAM" config "$@"

    CHANGES_POSSIBLE=1

  else
    # make sure parent folder of config file exists
    assert_parent "$YADM_CONFIG"
    # operate on the yadm configuration file
    "$GIT_PROGRAM" config --file="$(mixed_path "$YADM_CONFIG")" "$@"

  fi

}

function _set_gpg_options() {
  gpg_key="$(config yadm.gpg-recipient)"
  if [ "$gpg_key" = "ASK" ]; then
    GPG_OPTS=("--no-default-recipient" "-e")
  elif [ "$gpg_key" != "" ]; then
    GPG_OPTS=("-e")
    for key in $gpg_key; do
      GPG_OPTS+=("-r $key")
    done
  else
    GPG_OPTS=("-c")
  fi
}

function _get_openssl_ciphername() {
  OPENSSL_CIPHERNAME="$(config yadm.openssl-ciphername)"
  if [ -z "$OPENSSL_CIPHERNAME" ]; then
    OPENSSL_CIPHERNAME="aes-256-cbc"
  fi
  echo "$OPENSSL_CIPHERNAME"
}

function _set_openssl_options() {
  cipher_name="$(_get_openssl_ciphername)"
  OPENSSL_OPTS=("-${cipher_name}" -salt)
  if [ "$(config --bool yadm.openssl-old)" == "true" ]; then
    OPENSSL_OPTS+=(-md md5)
  else
    OPENSSL_OPTS+=(-pbkdf2 -iter 100000 -md sha512)
  fi
}

function _get_cipher() {
  output_archive="$1"
  yadm_cipher="$(config yadm.cipher)"
  if [ -z "$yadm_cipher" ]; then
      yadm_cipher="gpg"
  fi
}

function _decrypt_from() {

  local output_archive
  local yadm_cipher
  _get_cipher "$1"

  case "$yadm_cipher" in
    gpg)
      require_gpg
      $GPG_PROGRAM -d "$output_archive"
      ;;

    openssl)
      require_openssl
      _set_openssl_options
      $OPENSSL_PROGRAM enc -d "${OPENSSL_OPTS[@]}" -in "$output_archive"
      ;;

    *)
      error_out "Unknown cipher '$yadm_cipher'"
      ;;

  esac

}

function _encrypt_to() {

  local output_archive
  local yadm_cipher
  _get_cipher "$1"

  case "$yadm_cipher" in
    gpg)
      require_gpg
      _set_gpg_options
      $GPG_PROGRAM --yes "${GPG_OPTS[@]}" --output "$output_archive"
      ;;

    openssl)
      require_openssl
      _set_openssl_options
      $OPENSSL_PROGRAM enc -e "${OPENSSL_OPTS[@]}" -out "$output_archive"
      ;;

    *)
      error_out "Unknown cipher '$yadm_cipher'"
      ;;

  esac

}

function decrypt() {

  require_archive

  [ -f "$YADM_ENCRYPT" ] && exclude_encrypted

  if [ "$DO_LIST" = "YES" ] ; then
    tar_option="t"
  else
    tar_option="x"
  fi

  # decrypt the archive
  if (_decrypt_from "$YADM_ARCHIVE" || echo 1) | tar v${tar_option}f - -C "$YADM_WORK"; then
    [ ! "$DO_LIST" = "YES" ] && echo "All files decrypted."
  else
    error_out "Unable to extract encrypted files."
  fi

  CHANGES_POSSIBLE=1

}

function encrypt() {

  require_encrypt
  exclude_encrypted
  parse_encrypt

  cd_work "Encryption" || return

  # report which files will be encrypted
  echo "Encrypting the following files:"
  printf '%s\n' "${ENCRYPT_INCLUDE_FILES[@]}"
  echo

  # encrypt all files which match the globs
  if tar -f - -c "${ENCRYPT_INCLUDE_FILES[@]}" | _encrypt_to "$YADM_ARCHIVE"; then
    echo "Wrote new file: $YADM_ARCHIVE"
  else
    error_out "Unable to write $YADM_ARCHIVE"
  fi

  # offer to add YADM_ARCHIVE if untracked
  archive_status=$("$GIT_PROGRAM" status --porcelain -uall "$(mixed_path "$YADM_ARCHIVE")" 2>/dev/null)
  archive_regex="^\?\?"
  if [[ $archive_status =~ $archive_regex ]] ; then
    echo "It appears that $YADM_ARCHIVE is not tracked by yadm's repository."
    echo "Would you like to add it now? (y/n)"
    read -r answer < /dev/tty
    if [[ $answer =~ ^[yY]$ ]] ; then
      "$GIT_PROGRAM" add "$(mixed_path "$YADM_ARCHIVE")"
    fi
  fi

  CHANGES_POSSIBLE=1

}

function git_crypt() {
  require_git_crypt
  enter "${GIT_CRYPT_PROGRAM} $*"
}

function transcrypt() {
  require_transcrypt
  enter "${TRANSCRYPT_PROGRAM} $*"
}

function enter() {
  command="$*"
  require_shell
  require_repo

  local -a shell_opts
  local shell_path=""
  if [[ "$SHELL" =~ bash$ ]]; then
    shell_opts=("--norc")
    shell_path="\w"
  elif [[ "$SHELL" =~ [cz]sh$ ]]; then
    shell_opts=("-f")
    if [[ "$SHELL" =~ zsh$ && "$TERM" = "dumb" ]]; then
      # Disable ZLE for tramp
      shell_opts+=("--no-zle")
    fi
    shell_path="%~"
  fi

  shell_cmd=()
  if [ -n "$command" ]; then
    shell_cmd=('-c' "$*")
  fi

  GIT_WORK_TREE="$YADM_WORK"
  export GIT_WORK_TREE

  [ "${#shell_cmd[@]}" -eq 0 ] && echo "Entering yadm repo"

  yadm_prompt="yadm shell ($YADM_REPO) $shell_path > "
  PROMPT="$yadm_prompt" PS1="$yadm_prompt" "$SHELL" "${shell_opts[@]}" "${shell_cmd[@]}"
  return_code="$?"

  if [ "${#shell_cmd[@]}" -eq 0 ]; then
    echo "Leaving yadm repo"
  else
    exit_with_hook "$return_code"
  fi
}

function git_command() {

  require_repo

  # translate 'gitconfig' to 'config' -- 'config' is reserved for yadm
  if [ "$1" = "gitconfig" ] ; then
    set -- "config" "${@:2}"
  fi

  # ensure private .ssh and .gnupg directories exist first
  # TODO: consider restricting this to only commands which modify the work-tree

  if [ "$YADM_WORK" = "$HOME" ]; then
    auto_private_dirs=$(config --bool yadm.auto-private-dirs)
    if [ "$auto_private_dirs" != "false" ] ; then
      for pdir in $(private_dirs all); do
        assert_private_dirs "$pdir"
      done
    fi
  fi

  CHANGES_POSSIBLE=1

  # pass commands through to git
  debug "Running git command $GIT_PROGRAM $*"
  "$GIT_PROGRAM" "$@"
  return "$?"
}

function help() {

  local msg
  IFS='' read -r -d '' msg << EOF
Usage: yadm <command> [options...]

Manage dotfiles maintained in a Git repository. Manage alternate files
for specific systems or hosts. Encrypt/decrypt private files.

Git Commands:
Any Git command or alias can be used as a <command>. It will operate
on yadm's repository and files in the work tree (usually \$HOME).

Commands:
  yadm init [-f]             - Initialize an empty repository
  yadm clone <url> [-f]      - Clone an existing repository
  yadm config <name> <value> - Configure a setting
  yadm list [-a]             - List tracked files
  yadm alt                   - Create links for alternates
  yadm bootstrap             - Execute \$HOME/.config/yadm/bootstrap
  yadm encrypt               - Encrypt files
  yadm decrypt [-l]          - Decrypt files
  yadm perms                 - Fix perms for private files
  yadm enter [COMMAND]       - Run sub-shell with GIT variables set
  yadm git-crypt [OPTIONS]   - Run git-crypt commands for the yadm repo
  yadm transcrypt [OPTIONS]  - Run transcrypt commands for the yadm repo

Files:
  \$HOME/.config/yadm/config        - yadm's configuration file
  \$HOME/.config/yadm/encrypt       - List of globs to encrypt/decrypt
  \$HOME/.config/yadm/bootstrap     - Script run via: yadm bootstrap
  \$HOME/.local/share/yadm/repo.git - yadm's Git repository
  \$HOME/.local/share/yadm/archive  - Encrypted data stored here

Use "man yadm" for complete documentation.
EOF
  printf '%s\n' "$msg"
  exit_with_hook 1

}

# shellcheck disable=SC2120
function init() {

  # safety check, don't attempt to init when the repo is already present
  [ -d "$YADM_REPO" ] && [ -z "$FORCE" ] &&
    error_out "Git repo already exists. [$YADM_REPO]\nUse '-f' if you want to force it to be overwritten."

  # remove existing if forcing the init to happen anyway
  [ -d "$YADM_REPO" ] && {
    debug "Removing existing repo prior to init"
    "$GIT_PROGRAM" -C "$YADM_WORK" submodule deinit -f --all
    rm -rf "$YADM_REPO"
  }

  # init a new bare repo
  debug "Init new repo"
  "$GIT_PROGRAM" init --shared=0600 --bare "$(mixed_path "$YADM_REPO")" "$@"
  configure_repo

  CHANGES_POSSIBLE=1

}

function introspect() {
  case "$1" in
    commands|configs|repo|switches)
      "introspect_$1"
    ;;
  esac
}

function introspect_commands() {
  local msg
  read -r -d '' msg <<-EOF
alt
bootstrap
clean
clone
config
decrypt
encrypt
enter
git-crypt
gitconfig
help
init
introspect
list
perms
transcrypt
upgrade
version
EOF
  printf '%s' "$msg"
}

function introspect_configs() {
  local msg
  read -r -d '' msg <<-EOF
local.arch
local.class
local.hostname
local.os
local.user
yadm.alt-copy
yadm.auto-alt
yadm.auto-exclude
yadm.auto-perms
yadm.auto-private-dirs
yadm.cipher
yadm.git-program
yadm.gpg-perms
yadm.gpg-program
yadm.gpg-recipient
yadm.openssl-ciphername
yadm.openssl-old
yadm.openssl-program
yadm.ssh-perms
EOF
  printf '%s' "$msg"
}

function introspect_repo() {
  echo "$YADM_REPO"
}

function introspect_switches() {
  local msg
  read -r -d '' msg <<-EOF
--yadm-archive
--yadm-bootstrap
--yadm-config
--yadm-data
--yadm-dir
--yadm-encrypt
--yadm-repo
-Y
EOF
  printf '%s' "$msg"
}

function list() {

  require_repo

  # process relative to YADM_WORK when --all is specified
  if [ -n "$LIST_ALL" ] ; then
    cd_work "List" || return
  fi

  # list tracked files
  "$GIT_PROGRAM" ls-files

}

function perms() {

  parse_encrypt

  # TODO: prevent repeats in the files changed

  cd_work "Perms" || return

  GLOBS=()

  # include the archive created by "encrypt"
  [ -f "$YADM_ARCHIVE" ] && GLOBS+=("$YADM_ARCHIVE")

  # only include private globs if using HOME as worktree
  if [ "$YADM_WORK" = "$HOME" ]; then
    # include all .ssh files (unless disabled)
    if [[ $(config --bool yadm.ssh-perms) != "false" ]] ; then
      GLOBS+=(".ssh" ".ssh/*" ".ssh/.[!.]*")
    fi

    # include all gpg files (unless disabled)
    gnupghome="$(private_dirs gnupg)"
    if [[ $(config --bool yadm.gpg-perms) != "false" ]] ; then
      GLOBS+=("${gnupghome}" "${gnupghome}/*" "${gnupghome}/.[!.]*")
    fi
  fi

  # include any files we encrypt
  GLOBS+=("${ENCRYPT_INCLUDE_FILES[@]}")

  # remove group/other permissions from collected globs
  #shellcheck disable=SC2068
  #(SC2068 is disabled because in this case, we desire globbing)
  chmod -f go-rwx ${GLOBS[@]} &> /dev/null
  # TODO: detect and report changing permissions in a portable way

}

function upgrade() {

  local actions_performed=0
  local -a submodules
  local repo_updates=0

  [[ -n "${YADM_OVERRIDE_REPO}${YADM_OVERRIDE_ARCHIVE}" || "$YADM_DATA" = "$YADM_DIR" ]] && \
    error_out "Unable to upgrade. Paths have been overridden with command line options"

  # choose a legacy repo, the version 2 location will be favored
  local LEGACY_REPO=
  [ -d "$YADM_LEGACY_DIR/repo.git" ] && LEGACY_REPO="$YADM_LEGACY_DIR/repo.git"
  [ -d "$YADM_DIR/repo.git" ] && LEGACY_REPO="$YADM_DIR/repo.git"

  # handle legacy repo
  if [ -d "$LEGACY_REPO" ]; then
    # choose
    # legacy repo detected, it must be moved to YADM_REPO
    if [ -e "$YADM_REPO" ]; then
      error_out "Unable to upgrade. '$YADM_REPO' already exists. Refusing to overwrite it."
    else
      actions_performed=1
      echo "Moving $LEGACY_REPO to $YADM_REPO"

      export GIT_DIR="$LEGACY_REPO"

      # Must absorb git dirs, otherwise deinit below will fail for modules that have
      # been cloned first and then added as a submodule.
      "$GIT_PROGRAM" submodule absorbgitdirs

      local submodule_status
      submodule_status=$("$GIT_PROGRAM" -C "$YADM_WORK" submodule status)
      while read -r sha submodule rest; do
          [ "$submodule" == "" ] && continue
          if [[ "$sha" = -* ]]; then
              continue
          fi
          "$GIT_PROGRAM" -C "$YADM_WORK" submodule deinit ${FORCE:+-f} -- "$submodule" || {
              for other in "${submodules[@]}"; do
                  "$GIT_PROGRAM" -C "$YADM_WORK" submodule update --init --recursive -- "$other"
              done
              error_out "Unable to upgrade. Could not deinit submodule $submodule"
          }
          submodules+=("$submodule")
      done <<< "$submodule_status"

      assert_parent "$YADM_REPO"
      mv "$LEGACY_REPO" "$YADM_REPO"
    fi
  fi
  GIT_DIR="$YADM_REPO"
  export GIT_DIR

  # choose a legacy archive, the version 2 location will be favored
  local LEGACY_ARCHIVE=
  [ -e "$YADM_LEGACY_DIR/$YADM_LEGACY_ARCHIVE" ] && LEGACY_ARCHIVE="$YADM_LEGACY_DIR/$YADM_LEGACY_ARCHIVE"
  [ -e "$YADM_DIR/$YADM_LEGACY_ARCHIVE" ] && LEGACY_ARCHIVE="$YADM_DIR/$YADM_LEGACY_ARCHIVE"

  # handle legacy archive
  if [ -e "$LEGACY_ARCHIVE" ]; then
    actions_performed=1
    echo "Moving $LEGACY_ARCHIVE to $YADM_ARCHIVE"
    assert_parent "$YADM_ARCHIVE"
    # test to see if path is "tracked" in repo, if so 'git mv' must be used
    if "$GIT_PROGRAM" ls-files --error-unmatch "$LEGACY_ARCHIVE" &> /dev/null; then
      "$GIT_PROGRAM" mv "$LEGACY_ARCHIVE" "$YADM_ARCHIVE" && repo_updates=1
    else
      mv -i "$LEGACY_ARCHIVE" "$YADM_ARCHIVE"
    fi
  fi

  # handle any remaining version 1 paths
  for legacy_path in                      \
    "$YADM_LEGACY_DIR/config"             \
    "$YADM_LEGACY_DIR/encrypt"            \
    "$YADM_LEGACY_DIR/bootstrap"          \
    "$YADM_LEGACY_DIR"/hooks/{pre,post}_* \
  ;
  do
    if [ -e "$legacy_path" ]; then
      new_filename="${legacy_path#"$YADM_LEGACY_DIR/"}"
      new_filename="$YADM_DIR/$new_filename"
      actions_performed=1
      echo "Moving $legacy_path to $new_filename"
      assert_parent "$new_filename"
      # test to see if path is "tracked" in repo, if so 'git mv' must be used
      if "$GIT_PROGRAM" ls-files --error-unmatch "$legacy_path" &> /dev/null; then
        "$GIT_PROGRAM" mv "$legacy_path" "$new_filename" && repo_updates=1
      else
        mv -i "$legacy_path" "$new_filename"
      fi
    fi
  done

  # handle submodules, which need to be reinitialized
  for submodule in "${submodules[@]}"; do
      "$GIT_PROGRAM" -C "$YADM_WORK" submodule update --init --recursive -- "$submodule"
  done

  [ "$actions_performed" -eq 0 ] && \
    echo "No legacy paths found. Upgrade is not necessary"

  [ "$repo_updates" -eq 1 ] && \
    echo "Some files tracked by yadm have been renamed. These changes should probably be commited now."

  exit 0

}

function version() {

  echo "bash version $BASH_VERSION"
  printf " "; "$GIT_PROGRAM" --version
  echo "yadm version $VERSION"
  exit_with_hook 0

}

# ****** Utility Functions ******

function exclude_encrypted() {

  auto_exclude=$(config --bool yadm.auto-exclude)
  [ "$auto_exclude" == "false" ] && return 0

  exclude_path="${YADM_REPO}/info/exclude"
  newline=$'\n'
  exclude_flag="# yadm-auto-excludes"
  exclude_header="${exclude_flag}${newline}"
  exclude_header="${exclude_header}# This section is managed by yadm."
  exclude_header="${exclude_header}${newline}"
  exclude_header="${exclude_header}# Any edits below will be lost."
  exclude_header="${exclude_header}${newline}"

  # do nothing if there is no YADM_ENCRYPT
  [ -e "$YADM_ENCRYPT" ] || return 0

  # read encrypt
  encrypt_data=""
  while IFS='' read -r line || [ -n "$line" ]; do
    encrypt_data="${encrypt_data}${line}${newline}"
  done < "$YADM_ENCRYPT"

  # read info/exclude
  unmanaged=""
  managed=""
  if [ -e "$exclude_path" ]; then
    flag_seen=0
    while IFS='' read -r line || [ -n "$line" ]; do
      [ "$line" = "$exclude_flag" ] && flag_seen=1
      if [ "$flag_seen" -eq 0 ]; then
        unmanaged="${unmanaged}${line}${newline}"
      else
        managed="${managed}${line}${newline}"
      fi
    done < "$exclude_path"
  fi

  if [ "${exclude_header}${encrypt_data}" != "$managed" ]; then
    debug "Updating ${exclude_path}"
    assert_parent "$exclude_path"
    printf "%s" "${unmanaged}${exclude_header}${encrypt_data}" > "$exclude_path"
  fi

  return 0

}

function query_distro() {
  distro=""
  if command -v "$LSB_RELEASE_PROGRAM" &> /dev/null; then
    distro=$($LSB_RELEASE_PROGRAM -si 2>/dev/null)
  elif [ -f "$OS_RELEASE" ]; then
    while IFS='' read -r line || [ -n "$line" ]; do
      if [[ "$line" = ID=* ]]; then
        distro="${line#ID=}"
        distro="${distro//\"}"
        break
      fi
    done < "$OS_RELEASE"
  fi
  echo "$distro"
}

function query_distro_family() {
  family=""
  if [ -f "$OS_RELEASE" ]; then
    while IFS='' read -r line || [ -n "$line" ]; do
      if [[ "$line" = ID_LIKE=* ]]; then
        family="${line#ID_LIKE=}"
        family="${family//\"}"
        break
      fi
    done < "$OS_RELEASE"
  fi
  echo "$family"
}

function process_global_args() {

  # global arguments are removed before the main processing is done
  MAIN_ARGS=()
  while [[ $# -gt 0 ]] ; do
    key="$1"
    case $key in
      -Y|--yadm-dir) # override the standard YADM_DIR
        YADM_DIR="$(qualify_path "$2" "yadm")"
        shift
      ;;
      --yadm-data) # override the standard YADM_DATA
        YADM_DATA="$(qualify_path "$2" "data")"
        shift
      ;;
      --yadm-repo) # override the standard YADM_REPO
        YADM_OVERRIDE_REPO="$(qualify_path "$2" "repo")"
        shift
      ;;
      --yadm-config) # override the standard YADM_CONFIG
        YADM_OVERRIDE_CONFIG="$(qualify_path "$2" "config")"
        shift
      ;;
      --yadm-encrypt) # override the standard YADM_ENCRYPT
        YADM_OVERRIDE_ENCRYPT="$(qualify_path "$2" "encrypt")"
        shift
      ;;
      --yadm-archive) # override the standard YADM_ARCHIVE
        YADM_OVERRIDE_ARCHIVE="$(qualify_path "$2" "archive")"
        shift
      ;;
      --yadm-bootstrap) # override the standard YADM_BOOTSTRAP
        YADM_OVERRIDE_BOOTSTRAP="$(qualify_path "$2" "bootstrap")"
        shift
      ;;
      *) # main arguments are kept intact
        MAIN_ARGS+=("$1")
      ;;
    esac
    shift
  done

}

function qualify_path() {
    local path="$1"
    if [ -z "$path" ]; then
        error_out "You can't specify an empty $2 path"
    fi

    if [ "$path" = "." ]; then
        path="$PWD"
    elif [[ "$path" != /* ]]; then
        path="$PWD/${path#./}"
    fi
    echo "$path"
}

function set_yadm_dirs() {

  # only resolve YADM_DATA if it hasn't been provided already
  if [ -z "$YADM_DATA" ]; then
    local base_yadm_data="$XDG_DATA_HOME"
    if [[ ! "$base_yadm_data" =~ ^/ ]] ; then
      base_yadm_data="${HOME}/.local/share"
    fi
    YADM_DATA="${base_yadm_data}/yadm"
  fi

  # only resolve YADM_DIR if it hasn't been provided already
  if [ -z "$YADM_DIR" ]; then
    local base_yadm_dir="$XDG_CONFIG_HOME"
    if [[ ! "$base_yadm_dir" =~ ^/ ]] ; then
      base_yadm_dir="${HOME}/.config"
    fi
    YADM_DIR="${base_yadm_dir}/yadm"
  fi

  issue_legacy_path_warning

}

function issue_legacy_path_warning() {

  # no warnings during upgrade
  [[ "${MAIN_ARGS[*]}" =~ upgrade ]] && return

  # no warnings if YADM_DIR is resolved as the leacy path
  [ "$YADM_DIR" = "$YADM_LEGACY_DIR" ] && return

  # no warnings if overrides have been provided
  [[ -n "${YADM_OVERRIDE_REPO}${YADM_OVERRIDE_ARCHIVE}" || "$YADM_DATA" = "$YADM_DIR" ]] && return

  # test for legacy paths
  local legacy_found=()
  # this is ordered by importance
  for legacy_path in                            \
    "$YADM_DIR/$YADM_REPO"                      \
    "$YADM_DIR/$YADM_LEGACY_ARCHIVE"            \
    "$YADM_LEGACY_DIR/$YADM_REPO"               \
    "$YADM_LEGACY_DIR/$YADM_BOOTSTRAP"          \
    "$YADM_LEGACY_DIR/$YADM_CONFIG"             \
    "$YADM_LEGACY_DIR/$YADM_ENCRYPT"            \
    "$YADM_LEGACY_DIR/$YADM_HOOKS"/{pre,post}_* \
    "$YADM_LEGACY_DIR/$YADM_LEGACY_ARCHIVE"     \
  ;
  do
    [ -e "$legacy_path" ] && legacy_found+=("$legacy_path")
  done

  [ ${#legacy_found[@]} -eq 0 ] && return

  local path_list
  for legacy_path in "${legacy_found[@]}"; do
    path_list="$path_list    * $legacy_path"$'\n'
  done

  local msg
  IFS='' read -r -d '' msg <<EOF

**WARNING**
  Legacy paths have been detected.

  With version 3.0.0, yadm uses the XDG Base Directory Specification
  to find its configurations and data. Read more about these changes here:

    https://yadm.io/docs/upgrade_from_2
    https://yadm.io/docs/upgrade_from_1

  In your environment, the data directory has been resolved to:

    $YADM_DATA

  To remove this warning do one of the following:
    * Run "yadm upgrade" to move the yadm data to the new paths. (RECOMMENDED)
    * Manually move yadm data to new default paths and reinit any submodules.
    * Specify your preferred paths with --yadm-data and --yadm-archive each execution.

  Legacy paths detected:
${path_list}
***********
EOF
  printf '%s\n' "$msg" >&2
LEGACY_WARNING_ISSUED=1

}

function configure_paths() {

  # change paths to be relative to YADM_DIR
  YADM_CONFIG="$YADM_DIR/$YADM_CONFIG"
  YADM_ENCRYPT="$YADM_DIR/$YADM_ENCRYPT"
  YADM_BOOTSTRAP="$YADM_DIR/$YADM_BOOTSTRAP"
  YADM_HOOKS="$YADM_DIR/$YADM_HOOKS"
  YADM_ALT="$YADM_DIR/$YADM_ALT"

  # change paths to be relative to YADM_DATA
  YADM_REPO="$YADM_DATA/$YADM_REPO"
  YADM_ARCHIVE="$YADM_DATA/$YADM_ARCHIVE"

  # independent overrides for paths
  if [ -n "$YADM_OVERRIDE_REPO" ]; then
    YADM_REPO="$YADM_OVERRIDE_REPO"
  fi
  if [ -n "$YADM_OVERRIDE_CONFIG" ]; then
    YADM_CONFIG="$YADM_OVERRIDE_CONFIG"
  fi
  if [ -n "$YADM_OVERRIDE_ENCRYPT" ]; then
    YADM_ENCRYPT="$YADM_OVERRIDE_ENCRYPT"
  fi
  if [ -n "$YADM_OVERRIDE_ARCHIVE" ]; then
    YADM_ARCHIVE="$YADM_OVERRIDE_ARCHIVE"
  fi
  if [ -n "$YADM_OVERRIDE_BOOTSTRAP" ]; then
    YADM_BOOTSTRAP="$YADM_OVERRIDE_BOOTSTRAP"
  fi

  # use the yadm repo for all git operations
  GIT_DIR=$(mixed_path "$YADM_REPO")
  export GIT_DIR

  # obtain YADM_WORK from repo if it exists
  if [ -d "$GIT_DIR" ]; then
    local work
    work=$(unix_path "$("$GIT_PROGRAM" config core.worktree)")
    [ -n "$work" ] && YADM_WORK="$work"
  fi

  # YADM_BASE is used for manipulating the base worktree path for much of the
  # alternate file processing
  if [ "$YADM_WORK" == "/" ]; then
    YADM_BASE=""
  else
    YADM_BASE="$YADM_WORK"
  fi

}

function configure_repo() {

  debug "Configuring new repo"

  # change bare to false (there is a working directory)
  "$GIT_PROGRAM" config core.bare 'false'

  # set the worktree for the yadm repo
  "$GIT_PROGRAM" config core.worktree "$(mixed_path "$YADM_WORK")"

  # by default, do not show untracked files and directories
  "$GIT_PROGRAM" config status.showUntrackedFiles no

  # possibly used later to ensure we're working on the yadm repo
  "$GIT_PROGRAM" config yadm.managed 'true'

}

function set_operating_system() {

  if [[ "$(<$PROC_VERSION)" =~ [Mm]icrosoft ]]; then
    OPERATING_SYSTEM="WSL"
  else
    OPERATING_SYSTEM=$(uname -s)
  fi 2>/dev/null

  case "$OPERATING_SYSTEM" in
    CYGWIN*|MINGW*|MSYS*)
      git_version="$("$GIT_PROGRAM" --version 2>/dev/null)"
      if [[ "$git_version" =~ windows ]] ; then
          USE_CYGPATH=1
      fi
      OPERATING_SYSTEM=$(uname -o)
      ;;
    *)
      ;;
  esac

}

function set_awk() {
  local pgm
  for pgm in "${AWK_PROGRAM[@]}"; do
    command -v "$pgm" &> /dev/null && AWK_PROGRAM=("$pgm") && return
  done
}

function debug() {

  [ -n "$DEBUG" ] && echo_e "DEBUG: $*"

}

function error_out() {

  echo_e "ERROR: $*" >&2
  exit_with_hook 1

}

function exit_with_hook() {

  invoke_hook "post" "$1"
  exit "$1"

}

function invoke_hook() {

  mode="$1"
  exit_status="$2"
  hook_command="${YADM_HOOKS}/${mode}_$HOOK_COMMAND"

  if [ -x "$hook_command" ] || \
     { [[ $OPERATING_SYSTEM == MINGW* ]] && [ -f "$hook_command" ] ;} ; then
    debug "Invoking hook: $hook_command"

    # expose some internal data to all hooks
    YADM_HOOK_COMMAND=$HOOK_COMMAND
    YADM_HOOK_DIR=$YADM_DIR
    YADM_HOOK_DATA=$YADM_DATA
    YADM_HOOK_EXIT=$exit_status
    YADM_HOOK_FULL_COMMAND=$FULL_COMMAND
    YADM_HOOK_REPO=$YADM_REPO
    YADM_HOOK_WORK=$YADM_WORK

    # pack array to export it; filenames including a newline character (\n)
    # are NOT supported
    YADM_ENCRYPT_INCLUDE_FILES=$(join_string $'\n' "${ENCRYPT_INCLUDE_FILES[@]}")

    export YADM_HOOK_COMMAND
    export YADM_HOOK_DIR
    export YADM_HOOK_DATA
    export YADM_HOOK_EXIT
    export YADM_HOOK_FULL_COMMAND
    export YADM_HOOK_REPO
    export YADM_HOOK_WORK
    export YADM_ENCRYPT_INCLUDE_FILES

    # export helper functions
    export -f builtin_dirname
    export -f relative_path
    export -f unix_path
    export -f mixed_path

    "$hook_command"
    hook_status=$?

    # failing "pre" hooks will prevent commands from being run
    if [ "$mode" = "pre" ] && [ "$hook_status" -ne 0 ]; then
      echo "Hook $hook_command was not successful"
      echo "$HOOK_COMMAND will not be run"
      exit "$hook_status"
    fi

  fi

}

function private_dirs() {
  fetch="$1"
  pdirs=(.ssh)
  if [ -z "${GNUPGHOME:-}" ]; then
    pdirs+=(.gnupg)
  else
    pdirs+=("$(relative_path "$YADM_WORK" "$GNUPGHOME")")
  fi
  if [ "$fetch" = "all" ]; then
    echo "${pdirs[@]}"
  else
    echo "${pdirs[1]}"
  fi
}

function assert_private_dirs() {
  for private_dir in "$@"; do
    if [ ! -d "$YADM_WORK/$private_dir" ]; then
      debug "Creating $YADM_WORK/$private_dir"
      #shellcheck disable=SC2174
      mkdir -m 0700 -p "$YADM_WORK/$private_dir" &> /dev/null
    fi
  done
}

function assert_parent() {
  basedir=${1%/*}
  if [ -n "$basedir" ]; then
    [ -e "$basedir" ] || mkdir -p "$basedir"
  fi
}

function display_private_perms() {
  when="$1"
  for private_dir in $(private_dirs all); do
    if [ -d "$YADM_WORK/$private_dir" ]; then
      private_perms=$(ls -ld "$YADM_WORK/$private_dir")
      debug "$when" private dir perms "$private_perms"
    fi
  done
}

function cd_work() {
  cd "$YADM_WORK" || {
    debug "$1 not processed, unable to cd to $YADM_WORK"
    return 1
  }
  return 0
}

function parse_encrypt() {
  if [ "$ENCRYPT_INCLUDE_FILES" != "unparsed" ]; then
    #shellcheck disable=SC2034
    PARSE_ENCRYPT_SHORT="parse_encrypt() not reprocessed"
    return
  fi

  ENCRYPT_INCLUDE_FILES=()
  ENCRYPT_EXCLUDE_FILES=()
  FINAL_INCLUDE=()

  [ -f "$YADM_ENCRYPT" ] || return

  cd_work "Parsing encrypt" || return

  # setting globstar to allow ** in encrypt patterns
  # (only supported on Bash >= 4)
  local unset_globstar
  if ! shopt globstar &> /dev/null; then
    unset_globstar=1
  fi
  shopt -s globstar &> /dev/null

  exclude_pattern="^!(.+)"
  # parse both included/excluded
  while IFS='' read -r line || [ -n "$line" ]; do
    if [[ ! $line =~ ^# && ! $line =~ ^[[:blank:]]*$ ]] ; then
      local IFS=$'\n'
      for pattern in $line; do
        if [[ "$pattern" =~ $exclude_pattern ]]; then
          for ex_file in ${BASH_REMATCH[1]}; do
            if [ -e "$ex_file" ]; then
              ENCRYPT_EXCLUDE_FILES+=("$ex_file")
            fi
          done
        else
          for in_file in $pattern; do
            if [ -e "$in_file" ]; then
              ENCRYPT_INCLUDE_FILES+=("$in_file")
            fi
          done
        fi
      done
    fi
  done < "$YADM_ENCRYPT"

  # remove excludes from the includes
  #(SC2068 is disabled because in this case, we desire globbing)
  #shellcheck disable=SC2068
  for included in "${ENCRYPT_INCLUDE_FILES[@]}"; do
    skip=
    #shellcheck disable=SC2068
    for ex_file in ${ENCRYPT_EXCLUDE_FILES[@]}; do
      [ "$included" == "$ex_file" ] && { skip=1; break; }
    done
    [ -n "$skip" ] || FINAL_INCLUDE+=("$included")
  done

  # sort the encrypted files
  #shellcheck disable=SC2207
  IFS=$'\n' ENCRYPT_INCLUDE_FILES=($(LC_ALL=C sort <<<"${FINAL_INCLUDE[*]}"))
  unset IFS

  if [ "$unset_globstar" = "1" ]; then
    shopt -u globstar &> /dev/null
  fi

}

function builtin_dirname() {
  # dirname is not builtin, and universally available, this is a built-in
  # replacement using parameter expansion
  path="$1"
  dname="${path%/*}"
  if ! [[ "$path" =~ / ]]; then
    echo "."
  elif [ "$dname" = "" ]; then
    echo "/"
  else
    echo "$dname"
  fi
}

function relative_path() {
  # Output a path to $2/full, relative to $1/base
  #
  # This fucntion created with ideas from
  # https://stackoverflow.com/questions/2564634
  base="$1"
  full="$2"

  common_part="$base"
  result=""

  count=0
  while [ "${full#"$common_part"}" == "${full}" ]; do
      [ "$count" = "500" ] && return # this is a failsafe
      # no match, means that candidate common part is not correct
      # go up one level (reduce common part)
      common_part="$(builtin_dirname "$common_part")"
      # and record that we went back, with correct / handling
      if [[ -z $result ]]; then
          result=".."
      else
          result="../$result"
      fi
      count=$((count+1))
  done

  if [[ $common_part == "/" ]]; then
      # special case for root (no common path)
      result="$result/"
  fi

  # since we now have identified the common part,
  # compute the non-common part
  forward_part="${full#"$common_part"}"

  # and now stick all parts together
  if [[ -n $result ]] && [[ -n $forward_part ]]; then
      result="$result$forward_part"
  elif [[ -n $forward_part ]]; then
      # extra slash removal
      result="${forward_part:1}"
  fi

  echo "$result"
}

# ****** Auto Functions ******

function auto_alt() {

  # process alternates if there are possible changes
  if [ "$CHANGES_POSSIBLE" = "1" ] ; then
    auto_alt=$(config --bool yadm.auto-alt)
    if [ "$auto_alt" != "false" ] ; then
      [ -d "$YADM_REPO" ] && alt
    fi
  fi

}

function auto_perms() {

  # process permissions if there are possible changes
  if [ "$CHANGES_POSSIBLE" = "1" ] ; then
    auto_perms=$(config --bool yadm.auto-perms)
    if [ "$auto_perms" != "false" ] ; then
      [ -d "$YADM_REPO" ] && perms
    fi
  fi

}

function auto_bootstrap() {

  bootstrap_available || return

  [ "$DO_BOOTSTRAP" -eq 0 ] && return
  [ "$DO_BOOTSTRAP" -eq 3 ] && return
  [ "$DO_BOOTSTRAP" -eq 2 ] && bootstrap
  if [ "$DO_BOOTSTRAP" -eq 1 ] ; then
    echo "Found $YADM_BOOTSTRAP"
    echo "It appears that a bootstrap program exists."
    echo "Would you like to execute it now? (y/n)"
    read -r answer < /dev/tty
    if [[ $answer =~ ^[yY]$ ]] ; then
      bootstrap
    fi
  fi

}

# ****** Helper Functions ******

function join_string {
    local IFS="$1"
    printf "%s" "${*:2}"
}

function in_list {
  local element="$1"
  shift

  for e in "$@"; do
    [[ "$e" = "$element" ]] && return 0
  done
  return 1
}

function get_mode {
  local filename="$1"
  local mode

  # most *nixes
  mode=$(stat -c '%a' "$filename" 2>/dev/null)
  if [ -z "$mode" ] ; then
    # BSD-style
    mode=$(stat -f '%p' "$filename" 2>/dev/null)
    mode=${mode: -4}
  fi

  # only accept results if they are octal
  if [[ ! $mode =~ ^[0-7]+$ ]] ; then
    mode=""
  fi

  echo "$mode"
}

function copy_perms {
  local source="$1"
  local dest="$2"
  mode=$(get_mode "$source")
  [ -n "$mode" ] && chmod "$mode" "$dest"
  return 0
}

function mk_tmp_dir {
  local tempdir="$YADM_DATA/tmp.$$.$RANDOM"
  assert_parent "$tempdir/"
  echo "$tempdir"
}

# ****** Prerequisites Functions ******

function require_archive() {
  [ -f "$YADM_ARCHIVE" ] || error_out "$YADM_ARCHIVE does not exist. did you forget to create it?"
}
function require_encrypt() {
  [ -f "$YADM_ENCRYPT" ] || error_out "$YADM_ENCRYPT does not exist. did you forget to create it?"
}
function require_git() {
  local alt_git
  alt_git="$(config yadm.git-program)"

  local more_info=""

  if [ "$alt_git" != "" ] ; then
    GIT_PROGRAM="$alt_git"
    more_info="\nThis command has been set via the yadm.git-program configuration."
  fi
  command -v "$GIT_PROGRAM" &> /dev/null ||
    error_out "This functionality requires Git to be installed, but the command '$GIT_PROGRAM' cannot be located.$more_info"
}
function require_gpg() {
  local alt_gpg
  alt_gpg="$(config yadm.gpg-program)"

  local more_info=""

  if [ "$alt_gpg" != "" ] ; then
    GPG_PROGRAM="$alt_gpg"
    more_info="\nThis command has been set via the yadm.gpg-program configuration."
  fi
  command -v "$GPG_PROGRAM" &> /dev/null ||
    error_out "This functionality requires GPG to be installed, but the command '$GPG_PROGRAM' cannot be located.$more_info"
}
function require_openssl() {
  local alt_openssl
  alt_openssl="$(config yadm.openssl-program)"

  local more_info=""

  if [ "$alt_openssl" != "" ] ; then
    OPENSSL_PROGRAM="$alt_openssl"
    more_info="\nThis command has been set via the yadm.openssl-program configuration."
  fi
  command -v "$OPENSSL_PROGRAM" &> /dev/null ||
    error_out "This functionality requires OpenSSL to be installed, but the command '$OPENSSL_PROGRAM' cannot be located.$more_info"
}
function require_repo() {
  [ -d "$YADM_REPO" ] || error_out "Git repo does not exist. did you forget to run 'init' or 'clone'?"
}
function require_shell() {
  [ -x "$SHELL" ] || error_out "\$SHELL does not refer to an executable."
}
function require_git_crypt() {
  command -v "$GIT_CRYPT_PROGRAM" &> /dev/null ||
    error_out "This functionality requires git-crypt to be installed, but the command '$GIT_CRYPT_PROGRAM' cannot be located."
}
function require_transcrypt() {
  command -v "$TRANSCRYPT_PROGRAM" &> /dev/null ||
    error_out "This functionality requires transcrypt to be installed, but the command '$TRANSCRYPT_PROGRAM' cannot be located."
}
function bootstrap_available() {
  [ -f "$YADM_BOOTSTRAP" ] && [ -x "$YADM_BOOTSTRAP" ] && return
  return 1
}
function awk_available() {
  command -v "${AWK_PROGRAM[0]}" &> /dev/null && return
  return 1
}
function j2cli_available() {
  command -v "$J2CLI_PROGRAM" &> /dev/null && return
  return 1
}
function envtpl_available() {
  command -v "$ENVTPL_PROGRAM" &> /dev/null && return
  return 1
}
function esh_available() {
  command -v "$ESH_PROGRAM" &> /dev/null && return
  return 1
}
function readlink_available() {
  command -v "readlink" &> /dev/null && return
  return 1
}

# ****** Directory translations ******

function unix_path() {
  # for paths used by bash/yadm
  if [ "$USE_CYGPATH" = "1" ] ; then
    cygpath -u "$1"
  else
    echo "$1"
  fi
}
function mixed_path() {
  # for paths used by Git
  if [ "$USE_CYGPATH" = "1" ] ; then
    cygpath -m "$1"
  else
    echo "$1"
  fi
}

# ****** echo replacements ******

function echo() {
  IFS=' '
  printf '%s\n' "$*"
}
function echo_n() {
  IFS=' '
  printf '%s' "$*"
}
function echo_e() {
  IFS=' '
  printf '%b\n' "$*"
}

# ****** Main processing (when not unit testing) ******

if [ "$YADM_TEST" != 1 ] ; then
  process_global_args "$@"
  set_operating_system
  set_awk
  set_yadm_dirs
  configure_paths
  main "${MAIN_ARGS[@]}"
fi
