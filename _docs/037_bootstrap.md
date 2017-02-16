---
title: "Bootstrap"
permalink: /docs/bootstrap
---

Often there is more to set up once your dotfiles repository has been cloned. For
example, if your repository has submodules, you may wish to initialize them. On
MacOS, you may wish to install **Homebrew** and process a `.Brewfile`. These types
of additional steps are generally referred to as "bootstrapping".

Though everyone may have a different set of bootstrap operations they need to
perform, **yadm** has a standard command for executing them.

    yadm bootstrap

This command will execute the program named `$HOME/.yadm/bootstrap`. You must
provide this program yourself, and it must be made executable. But those are the
only constraints.

After **yadm** successfully clones a repository, if there is a bootstrap program
available, it will offer to run it for you.

    Found .yadm/bootstrap
    It appears that a bootstrap program exists.
    Would you like to execute it now? (y/n)

You can prevent this prompting by using the `--bootstrap` or `--no-bootstrap`
options when cloning.

It is best to make the logic of your bootstrap idempotent—allowing it to be
re-run in the future when you merge changes made on other hosts.

## Examples

Curious about the possibilities? See some examples below. These are all written
in Bash, but you can use any executable file as a bootstrap.

### Initialize submodules

If you've added repositories as submodules for the **yadm** repository, you can
initialize them after a successful clone.

```bash
#!/bin/bash

# Because Git submodule commands cannot operate without a work tree, they must
# be run from within $HOME (assuming this is the root of your dotfiles)
cd "$HOME"

echo "Init submodules"
yadm submodule update --recursive --init
```

### Install [Homebrew](http://brew.sh/) and a bundle of recipes

```bash
#!/bin/bash

system_type=$(uname -s)

if [ "$system_type" = "Darwin" ]; then

  # install homebrew if it's missing
  if ! command -v brew >/dev/null 2>&1; then
    echo "Installing homebrew"
    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
  fi

  if [ -f "$HOME/.Brewfile" ]; then
    echo "Updating homebrew bundle"
    brew bundle --global
  fi

fi
```

### Configure [iTerm2](http://www.iterm2.com/) to use your configuration

```bash
#!/bin/bash

system_type=$(uname -s)

if [ "$system_type" = "Darwin" ]; then

  # possibly add something here to ensure iTerm2 is installed using Homebrew
  # cask like in the previous example

  if [ -d "$HOME/.iterm2" ]; then
    echo "Setting iTerm preference folder"
    defaults write com.googlecode.iterm2 PrefsCustomFolder "$HOME/.iterm2"
  fi

fi
```

### Compile a custom terminfo file

```bash
#!/bin/bash

if [ -f "$HOME/.terminfo/custom.terminfo" ]; then
  echo "Updating terminfo"
  tic "$HOME/.terminfo/custom.terminfo"
fi
```

### Update the **yadm** repo origin URL

You might initially clone your repo using `https`, but ssh configurations may be
available after cloning. If so, you could update the **yadm** repo origin to use
`ssh` instead.

```bash
#!/bin/bash

echo "Updating the yadm repo origin URL"
yadm remote set-url origin "git@github.com:MyUser/dotfiles.git"
```

### Install [vim](http://www.vim.org/) plugins managed with [vim-plug](https://github.com/junegunn/vim-plug)

**vim-plug** can be used in your `.vimrc` to enable plugins. The example here will
automatically download **vim-plug** and run the `:PlugInstall` command if
**vim-plug** is missing when **vim** starts.

```vim
" download vim-plug if missing
if empty(glob("~/.vim/autoload/plug.vim"))
  silent! execute '!curl --create-dirs -fsSLo ~/.vim/autoload/plug.vim https://raw.github.com/junegunn/vim-plug/master/plug.vim'
  autocmd VimEnter * silent! PlugInstall
endif

" declare plugins
silent! if plug#begin()

  Plug 'airblade/vim-gitgutter'
  Plug 'c9s/perlomni.vim', { 'for': 'perl' }
  Plug 'ctrlpvim/ctrlp.vim'
  Plug 'vim-syntastic/syntastic'
  Plug 'yggdroot/indentLine'

  " ignore these on older versions of vim
  if v:version >= 703
    Plug 'gorodinskiy/vim-coloresque'
    Plug 'jamessan/vim-gnupg'
  endif
  if v:version >= 704
    Plug 'vim-pandoc/vim-pandoc-syntax'
  endif

  call plug#end()
endif
```

You can enhance this scheme by having your bootstrap program initialize
**vim-plug** when you clone, instead of when you first run **vim**. This example
will install any new plugins, and also remove any plugins now deleted from your
`.vimrc`.

```bash
#!/bin/bash

if command -v vim >/dev/null 2>&1; then
  echo "Bootstraping Vim"
  vim '+PlugUpdate' '+PlugClean!' '+PlugUpdate' '+qall'
fi
```

---

_If you have suggestions for useful bootstrapping logic, let me know..._
