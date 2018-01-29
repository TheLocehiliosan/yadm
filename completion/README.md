# Installation

## Bash completions
### Prerequisites
**yadm** completion only works if Git completions are also enabled.

### Homebrew
If using `homebrew` to install **yadm**, completions should automatically be handled if you also install `brew install bash-completion`. This might require you to include the main completion script in your own bashrc file like this:
```
[ -f /usr/local/etc/bash_completion ] && source /usr/local/etc/bash_completion
```

### Manual installation
Copy the completion script locally, and add this to you bashrc:
```
[ -f /full/path/to/yadm.bash_completion ] && source /full/path/to/yadm.bash_completion
```

## Zsh completions
### Homebrew
If using `homebrew` to install **yadm**, completions should handled automatically.

### Manual installation
Copy the completion script `yadm.zsh_completion` locally, rename it to `_yadm`, and add the containing folder to `$fpath` in `.zshrc`:
```
fpath=(/path/to/folder/containing_yadm $fpath)
autoload -U compinit
compinit
```

### Installation using [zplug](https://github.com/b4b4r07/zplug)
Load `_yadm` as a plugin in your `.zshrc`:
```
fpath=("$ZPLUG_HOME/bin" $fpath)
zplug "TheLocehiliosan/yadm", rename-to:_yadm, use:"completion/yadm.zsh_completion", as:command, defer:2
```
