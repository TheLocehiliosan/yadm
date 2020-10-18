---
title: "Alternate Files"
permalink: /docs/alternates
---

When possible, it is best to use the same files across all systems. However,
there are occasions when you need different files in some places. Below are
features and strategies for dealing with those occasions.

## Symlink alternates

It can be useful to have an automated way of choosing an alternate version of a
file for a different operating system, host, user, etc.

yadm will automatically create a symbolic link to the appropriate version of a
file, when a valid suffix is appended to the filename. The suffix contains the
conditions that must be met for that file to be used.

The suffix begins with `##`, followed by any number of conditions separated by
commas.

    ##<condition>[,<condition>,…]

Each condition is an attribute/value pair, separated by a period. Some
conditions do not require a "value", and in that case, the period and value can
be omitted. Most attributes can be abbreviated as a single letter.

| Attribute | Meaning |
| - | - |
| `template`, `t` | Valid when the value matches a supported template processor. See the [Templates](/docs/templates) section for more details. |
| `user`, `u` | Valid if the value matches the current user. Current user is calculated by running <code>id&nbsp;&#8209;u&nbsp;&#8209;n</code>. |
| `distro`, `d` | Valid if the value matches the distro. Distro is calculated by running <code>lsb_release&nbsp;&#8209;si</code> or inspecting <code>/etc/os-release</code> |
| `os`, `o` | Valid if the value matches the OS. OS is calculated by running <code>uname&nbsp;&#8209;s</code>. <sup>*</sup> |
| `class`, `c` | Valid if the value matches the local.class configuration. Class must be manually set using <code>yadm&nbsp;config&nbsp;local.class&nbsp;&lt;class&gt;</code>. |
| `hostname`, `h` | Valid if the value matches the short hostname. Hostname is calculated by running `hostname`, and trimming off any domain. |
| `default` | Valid when no other alternate is valid. |

<sub><sup>*
The OS for "Windows Subsystem for Linux" is reported as "WSL", even though uname identifies as "Linux".
<br/>
*
If `lsb_release` is not available, "distro" will be the ID specified in `/etc/os-release`.
</sup></sub>

You may use any number of conditions, in any order. An alternate will only be
used if _ALL_ conditions are valid. For all files managed by yadm's repository
or listed in `$HOME/.config/yadm/encrypt`, if they match this naming convention,
symbolic links will be created for the most appropriate version.

The "most appropriate" version is determined by calculating a score for each
version of a file. A [template](/docs/templates) is always scored higher than
any symlink condition. The number of conditions is the next largest factor in
scoring. Files with more conditions will always be favored. Any invalid
condition will disqualify that file completely.

If you don't care to have all versions of alternates stored in the same
directory as the generated symlink, you can place them in the
`$HOME/.config/yadm/alt` directory. The generated symlink or processed template
will be created using the same relative path.

Alternate linking may best be demonstrated by example. Assume the following
files are managed by yadm's repository:

    $HOME/path/example.txt##default
    $HOME/path/example.txt##class.Work
    $HOME/path/example.txt##os.Darwin
    $HOME/path/example.txt##os.Darwin,hostname.host1
    $HOME/path/example.txt##os.Darwin,hostname.host2
    $HOME/path/example.txt##os.Linux
    $HOME/path/example.txt##os.Linux,hostname.host1
    $HOME/path/example.txt##os.Linux,hostname.host2

If running on a Macbook named `host2`, yadm will create a symbolic link which looks like this:

`$HOME/path/example.txt` → `$HOME/path/example.txt##os.Darwin,hostname.host2`

However, on another Mackbook named `host3`, yadm will create a symbolic link which looks like this:

`$HOME/path/example.txt` → `$HOME/path/example.txt##os.Darwin`

Since the hostname doesn't match any of the managed files, the more generic
version is chosen. If running on a Linux server named `host4`, the link will be:

`$HOME/path/example.txt` → `$HOME/path/example.txt##os.Linux`

If running on a Solaris server, the link will use the default version:

`$HOME/path/example.txt` → `$HOME/path/example.txt##default`

If running on a system, with class set to `Work`, the link will be:

`$HOME/path/example.txt` → `$HOME/path/example.txt##class.Work`

If no `##default` version exists and no files have valid conditions, then no
link will be created.

Links are also created for directories named this way, as long as they have at
least one yadm managed file within them.

yadm will automatically create these links by default. This can be disabled
using the `yadm.auto-alt` configuration. Even if disabled, links can be manually
created by running `yadm alt`.

## Class and Overrides

Class is a special value which is stored locally on each host (inside the local
repository). To use alternate symlinks using `##class.<CLASS>`, you must set the
value of class using the configuration `local.class`. This is set like any other
yadm configuration—with the `yadm config` command. The following sets the
`local.class` to be "Work".

    yadm config local.class Work

Similarly, the values of `os`, `hostname`, and `user` can be manually overridden
using the configuration options `local.os`, `local.hostname`, and `local.user`.

## Templates

Templates are another powerful tool for creating alternate content on each host.
See the [Templates](/docs/templates) documentation for full details.

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
alternate version using yadm. Consider these three files:

`.gitconfig`

```ini
[log]
    decorate = short
    abbrevCommit = true
[include]
    path = .gitconfig.local
```

`.gitconfig.local##os.Darwin`

```ini
[user]
    name = Tim Byrne
    email = tim@personal.email.org
```

`.gitconfig.local##os.Linux`

```ini
[user]
    name = Dr. Tim Byrne
    email = dr.byrne@work.email.com
```

Configuring Git this way includes `.gitconfig.local` in the standard
`.gitconfig`. yadm will automatically link the correct version based on the
operating system. The bulk of your configurations can go in a single file, and
you just put the exceptions in OS-specific files.
