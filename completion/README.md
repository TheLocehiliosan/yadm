# Prerequisites

**yadm** completion only works if Git completions are also enabled.

# Installation

## Homebrew

If using `homebrew` to install **yadm**, completions should automatically be handled if you also install `brew install bash-completion`. This might require you to include the main completion script in your own bashrc file like this:

```
[ -f /usr/local/etc/bash_completion ] && source /usr/local/etc/bash_completion
```

## Manual installation
Copy the completion script locally, and add this to you bashrc:
```
[ -f /full/path/to/yadm.bash_completion ] && source /full/path/to/yadm.bash_completion
```
