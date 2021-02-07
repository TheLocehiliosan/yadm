# test if git completion is missing, but loader exists, attempt to load
if ! declare -F _git > /dev/null && ! declare -F __git_wrap__git_main > /dev/null; then
  if declare -F _completion_loader > /dev/null; then
    _completion_loader git
  fi
fi

# only operate if git completion is present
if declare -F _git > /dev/null || declare -F __git_wrap__git_main > /dev/null; then

  _yadm() {

    local current=${COMP_WORDS[COMP_CWORD]}
    local penultimate
    if [ "$((COMP_CWORD-1))" -ge "0" ]; then
      penultimate=${COMP_WORDS[COMP_CWORD-1]}
    fi
    local antepenultimate
    if [ "$((COMP_CWORD-2))" -ge "0" ]; then
      antepenultimate=${COMP_WORDS[COMP_CWORD-2]}
    fi

    local -x GIT_DIR
    # shellcheck disable=SC2034
    GIT_DIR="$(yadm introspect repo 2>/dev/null)"

    case "$penultimate" in
      bootstrap)
        COMPREPLY=()
        return 0
      ;;
      config)
        COMPREPLY=( $(compgen -W "$(yadm introspect configs 2>/dev/null)") )
        return 0
		  ;;
      decrypt)
        COMPREPLY=( $(compgen -W "-l" -- "$current") )
        return 0
		  ;;
      init)
        COMPREPLY=( $(compgen -W "-f -w" -- "$current") )
        return 0
		  ;;
      introspect)
        COMPREPLY=( $(compgen -W "commands configs repo switches" -- "$current") )
        return 0
		  ;;
      help)
        COMPREPLY=() # no specific help yet
        return 0
      ;;
      list)
        COMPREPLY=( $(compgen -W "-a" -- "$current") )
        return 0
		  ;;
    esac

    case "$antepenultimate" in
      clone)
        COMPREPLY=( $(compgen -W "-f -w -b --bootstrap --no-bootstrap" -- "$current") )
        return 0
		  ;;
    esac

    local yadm_switches=( $(yadm introspect switches 2>/dev/null) )

    # this condition is so files are completed properly for --yadm-xxx options
    if [[ " ${yadm_switches[*]} " != *" $penultimate "* ]]; then
      # TODO: somehow solve the problem with [--yadm-xxx option] being
      #       incompatible with what git expects, namely [--arg=option]
      if declare -F _git > /dev/null; then
        _git
      else
        __git_wrap__git_main
      fi
    fi
    if [[ "$current" =~ ^- ]]; then
      local matching
      matching=$(compgen -W "${yadm_switches[*]}" -- "$current")
      __gitcompappend "$matching"
    fi

    # Find the index of where the sub-command argument should go.
    local command_idx
    for (( command_idx=1 ; command_idx < ${#COMP_WORDS[@]} ; command_idx++ )); do
      local command_idx_arg="${COMP_WORDS[$command_idx]}"
      if [[ " ${yadm_switches[*]} " = *" $command_idx_arg "* ]]; then
        let command_idx++
      elif [[ "$command_idx_arg" = -* ]]; then
        :
      else
        break
      fi
    done
    if [[ "$COMP_CWORD" = "$command_idx" ]]; then
      local matching
      matching=$(compgen -W "$(yadm introspect commands 2>/dev/null)" -- "$current")
      __gitcompappend "$matching"
    fi

    # remove duplicates found in COMPREPLY (a native bash way could be better)
    if [ -n "${COMPREPLY[*]}" ]; then
      COMPREPLY=($(echo "${COMPREPLY[@]}" | sort -u))
    fi

  }

	complete -o bashdefault -o default -F _yadm yadm 2>/dev/null \
		|| complete -o default -F _yadm yadm

fi
