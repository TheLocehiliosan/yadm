---
title: "Alternate Files"
permalink: /docs/alternates
---

When possible, it is best to use the same files across all systems. However,
there are occasions when you need different files in some places. Below are
features and strategies for dealing with those occasions.

## Symlink alternates

It can be useful to have an automated way of choosing an alternate version of a
file for a different operating system, host, or user. **yadm** implements a
feature which will automatically create a symbolic link to the appropriate
version of a file, as long as you follow a specific naming convention. yadm can
detect files with names ending in:

| `##`                 | Default file linked             |
| `##OS`               | Matching OS                     |
| `##OS.HOSTNAME`      | Matching OS & Hostname          |
| `##OS.HOSTNAME.USER` | Matching OS, Hostname, and User |

If there are any files managed by yadm's repository, or listed in
`$HOME/.yadm/encrypt`, which match this naming convention, symbolic links will
be created for the most appropriate version. This may best be demonstrated by
example. Assume the following files are managed by yadm's repository:

    $HOME/path/example.txt##
    $HOME/path/example.txt##Darwin
    $HOME/path/example.txt##Darwin.host1
    $HOME/path/example.txt##Darwin.host2
    $HOME/path/example.txt##Linux
    $HOME/path/example.txt##Linux.host1
    $HOME/path/example.txt##Linux.host2

If running on a Macbook named `host2`, yadm will create a symbolic link which
looks like this:

`$HOME/path/example.txt` → `$HOME/path/example.txt##Darwin.host2`

However, on another Macbook named `host3`, yadm will create a symbolic link
which looks like this:

`$HOME/path/example.txt` → `$HOME/path/example.txt##Darwin`

Since the hostname doesn't match any of the  managed  files,  the  more generic
version is chosen.

If running on a Linux server named `host4`, the link will be:

`$HOME/path/example.txt` → `$HOME/path/example.txt##Linux`

If running on a Solaris server, the link use the default `##` version:

`$HOME/path/example.txt` → `$HOME/path/example.txt##`

If no `##` version exists and no files match the current OS/HOST- NAME/USER,
then no link will be created.

| OS is determined by running `uname -s`, HOSTNAME by running `hostname -s`, and USER by running `id -u -n`. **yadm** will automatically create these links by default. This can be disabled using the yadm.auto-alt configuration. Even if disabled, links can be manually created by running **yadm** alt.

## Strategies for alternate files on different systems

Where possible, you should try to use the same file on every system. Here are a few examples:

### .vimrc

```vim
let OS=substitute(system('uname -s'),"\n","","")
if (OS == "Darwin")
    " do something that only makes sense on a Mac
endif
```

### .tmux.conf

    # use reattach-to-user-namespace as the default command on OSX
    if-shell "test -f /usr/local/bin/reattach-to-user-namespace" 'set -g default-command "reattach-to-user-namespace -l bash"'

### .bash_profile

```bash
system_type=$(uname -s)
if [ "$system_type" = "Darwin" ]; then
    eval $(gdircolors $HOME/.dir_colors)
else
    eval $(dircolors -b $HOME/.dir_colors)
fi
```

### .gitconfig

However, sometimes the type of file you are using doesn't allow for this type of
logic. If a configuration can do an "_include_", you can include a specific
alternate version using **yadm**. Consider these three files:

`.gitconfig`

```ini
[log]
    decorate = short
    abbrevCommit = true
[include]
    path = .gitconfig.local
```

`.gitconfig.local##Darwin`

```ini
[user]
    name = Tim Byrne
    email = tim@personal.email.org
```

`.gitconfig.local##Linux`

```ini
[user]
    name = Dr. Tim Byrne
    email = dr.byrne@work.email.com
```

Configuring Git this way includes `.gitconfig.local` in the standard
`.gitconfig`. **yadm** will automatically link the correct version based on the
operating system. The bulk of your configurations can go in a single file, and
you just put the exceptions in OS-specific files.
