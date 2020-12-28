# Installation

### Prerequisites

Bash and Zsh completion only works if Git completions are also enabled.

## Homebrew

If using `homebrew` to install yadm, Bash, Zsh, and Fish completions should
automatically be installed. For Bash and Zsh, you also must install
`bash-completion` or `zsh-completions`. This might require you to include the
main completion script in your own shell configuration like this:

```bash
[ -f /usr/local/etc/bash_completion ] && source /usr/local/etc/bash_completion
```

## Bash (manual installation)

Copy the completion script locally, and add this to you bashrc:

```bash
[ -f /path/to/yadm/completion/bash/yadm ] && source /path/to/yadm/completion/bash/yadm
```

## Zsh (manual installation)

Add the `completion/zsh` folder to `$fpath` in `.zshrc`:

```zsh
fpath=(/path/to/yadm/completion/zsh $fpath)
autoload -U compinit
compinit
```

## Zsh (using [zplug](https://github.com/b4b4r07/zplug))

Load `_yadm` as a plugin in your `.zshrc`:

```zsh
fpath=("$ZPLUG_HOME/bin" $fpath)
zplug "TheLocehiliosan/yadm", use:"completion/zsh/_yadm", as:command, defer:2
```

## Fish (manual installation)

Copy the completion script `yadm.fish` to any folder within `$fish_complete_path`. For example, for local installation, you can copy it to `$HOME/.config/fish/completions/` and it will be loaded when `yadm` is invoked.
