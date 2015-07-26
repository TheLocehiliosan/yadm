# yadm - Yet Another Dotfiles Manager
_A house that does not have one warm, comfy chair in it is soulless._ --May Sarton

When you live in a command line, configurations are a deeply personal thing. They are often crafted over years of experience, battles lost, lessons learned, advice followed, and ingenuity rewarded. When you are away from your own configurations, you are an orphaned refugee in unfamiliar and hostile surroundings. You feel clumsy and out of sorts. You are filled with a sense of longing to be back in a place you know. A place you built. A place where all the short-cuts have been worn bare by your own travels. A place you proudly call... `$HOME`.

## Introduction
_Home is an invention on which no one has yet improved._ --Ann Douglas

As so many others, I started out with a repository and a few scripts to symbolically link them around my home directory. This quickly became inadequate and I looked for solutions elsewhere. I've used two excellent tools; [homeschick](https://github.com/andsens/homeshick), and [vcsh](https://github.com/RichiH/vcsh). These tools are great, and you should check them out to understand their strengths. However, I didn't find all of the features I personally wished for in a single tool. **yadm** was written with the following goals:

  - Use a single repository
  - Few dependencies
  - Ability to use alternate files based on OS or host
  - Ability to encrypt and track confidential files
  - Stay out of the way and let Git do what it's good at

## Installation
_Seek home for rest, for home is best._ --Thomas Tusser

**yadm** can be installed using [Homebrew](https://github.com/Homebrew/homebrew).

    brew tap TheLocehiliosan/yadm && brew install yadm

Otherwise you can simply download the **yadm** script and put it into your `$PATH`.

## Getting Started
_I would not change my blest estate for all the world calls good or great._ --Isaac Watts

If you know how to use Git, then you already know how to use **yadm**.
See the [man page](yadm.md) for a comprehensive explanation of commands and options.


#### If you don't currently have a repository
Start out with an empty local repository

    yadm init
    yadm add <important file>
    yadm commit

Eventually you will want to push the local repo to a remote.

    yadm remote add origin <url>
    yadm push -u origin master

#### If you have an existing remote repository
This `clone` will attempt to merge your existing repository, but if it fails, it will do a reset instead and you'll have to decide best on how resolve the differences.


    yadm clone <url>
    yadm status

## Strategies for alternate files on different systems
_To feel at home, stay at home._ --Clifton Fadiman

Where possible, you should try to use the same file on every system. Here are a few examples:

### .vimrc

    let OS=substitute(system('uname -s'),"\n","","")
    if (OS == "Darwin")
      " do something that only makes sense on a Mac
    endif

### .tmux.conf

    # use reattach-to-user-namespace as the default command on OSX
    if-shell "test -f /usr/local/bin/reattach-to-user-namespace" 'set -g default-command "reattach-to-user-namespace -l bash"'

### .bash_profile

    system_type=$(uname -s)
    if [ "$system_type" = "Darwin" ]; then
      eval $(gdircolors $HOME/.dir_colors)
    else
      eval $(dircolors -b $HOME/.dir_colors)
    fi

However, sometimes the type of file you are using doesn't allow for this type of logic. If a configuration can do an "include", you can include a specific alternate version using **yadm**. Consider these three files:

### .gitconfig

    #---- .gitconfig -----------------
    [log]
      decorate = short
      abbrevCommit = true
    [include]
      path = .gitconfig.local

    #---- .gitconfig.local##Darwin ---
    [user]
      name = Tim Byrne
      email = tim@personal.email.org

    #---- .gitconfig.local##Linux ----
    [user]
      name = Dr. Tim Byrne
      email = dr.byrne@work.email.com

Configuring Git this way includes `.gitconfig.local` in the standard `.gitconfig`. **yadm** will automatically link the correct version based on the operation system. The bulk of your configurations can go in a single file, and you just put the exceptions in OS-specific files.

Of course, you can use **yadm** to manage completely separate files for different systems as well.

### .signature

    #---- .signature##
    - Tim
    #---- .signature##Darwin.host1
    Sent from my MacBook
    - Tim
    #---- .signature##Linux.host2
    Sincerely,
    Dr. Tim Byrne

**yadm** will link the appropriate version for the current host, or use the default `##` version.

## Example of managing SSH configurations
_We shape our dwellings, and afterwards our dwellings shape us._ --Winston Churchill

Below is an example of how **yadm** can be used to manage SSH configurations. The example demonstrates **yadm** directly managing the `config` file, managing a host-specific `authorized_keys` file, and storing the private SSH key as part of its encrypted files. This example assumes a typical working SSH configuration exists, and walks through the steps to bring it under **yadm**'s management.

    yadm add ~/.ssh/config
    mv ~/.ssh/authorized_keys ~/.ssh/authorized_keys##Linux.myhost
    yadm add ~/.ssh/authorized_keys##Linux.myhost
    echo '.ssh/id_rsa' >> ~/.yadm/encrypt
    yadm add ~/.yadm/encrypt
    yadm encrypt

    ------

    yadm status

    Changes to be committed:
      (use "git rm --cached <file>..." to unstage)

            new file:   .ssh/authorized_keys##Linux.myhost
            new file:   .ssh/config
            new file:   .yadm/encrypt
            new file:   .yadm/files.gpg

    ------

    ls ~/.ssh

    authorized_keys -> ~/.ssh/authorized_keys##Linux.myhost
    authorized_keys##Linux.myhost
    config
    rsa_id


First, the `config` file is simply added. This will cause the same `config` file to be used on other **yadm** managed hosts. The `authorized_keys` file needs to be host specific, so rename the file using the OS and hostname. After adding the renamed `authorized_keys##Linux.myhost`, **yadm** will automatically create the symlink for it. Last, the private key should be maintained in **yadm**'s encrypted files. Add a pattern to the `.yadm/encrypt` file which matches the private key. Then instruct **yadm** to encrypt all files matching the patterns found in `.yadm/encrypt`. Notice that the **yadm** repository is not tracking the private key directly, rather it tracks the collection of encrypted files `.yadm/files.gpg`. When these changes are brought onto another host, using the `yadm decrypt` command will extract the files stored.

<!-- vim: set spell lbr : -->
