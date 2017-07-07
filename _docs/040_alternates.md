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
version of a file, as long as you follow a specific naming convention. **yadm** can
detect files with names ending in:

| `##`                       | Default file linked                  |
| `##CLASS`                  | Matching Class                       |
| `##CLASS.OS`               | Matching Class & OS                  |
| `##CLASS.OS.HOSTNAME`      | Matching Class, OS & Hostname        |
| `##CLASS.OS.HOSTNAME.USER` | Matching Class, OS, Hostname, & User |
| `##OS`                     | Matching OS                          |
| `##OS.HOSTNAME`            | Matching OS & Hostname               |
| `##OS.HOSTNAME.USER`       | Matching OS, Hostname, & User        |

If there are any files managed by **yadm**'s repository, or listed in
`$HOME/.yadm/encrypt`, which match this naming convention, symbolic links will
be created for the most appropriate version. This may best be demonstrated by
example. Assume the following files are managed by **yadm**'s repository:

    $HOME/path/example.txt##
    $HOME/path/example.txt##Work
    $HOME/path/example.txt##Darwin
    $HOME/path/example.txt##Darwin.host1
    $HOME/path/example.txt##Darwin.host2
    $HOME/path/example.txt##Linux
    $HOME/path/example.txt##Linux.host1
    $HOME/path/example.txt##Linux.host2

If running on a Macbook named `host2`, **yadm** will create a symbolic link which
looks like this:

`$HOME/path/example.txt` → `$HOME/path/example.txt##Darwin.host2`

However, on another Macbook named `host3`, **yadm** will create a symbolic link
which looks like this:

`$HOME/path/example.txt` → `$HOME/path/example.txt##Darwin`

Since the host name doesn't match any of the  managed  files,  the  more generic
version is chosen.

If running on a Linux server named `host4`, the link will be:

`$HOME/path/example.txt` → `$HOME/path/example.txt##Linux`

If running on a Solaris server, the link use the default `##` version:

`$HOME/path/example.txt` → `$HOME/path/example.txt##`

If running on a system, with `CLASS` set to "Work" ([see below](alternates#class-and-overrides)), the link will be:

`$HOME/path/example.txt` → `$HOME/path/example.txt##Work`

If no `##` version exists and no files match the current CLASS/OS/HOSTNAME/USER,
then no link will be created.

| **CLASS** must be manually set using `yadm config local.class <class>`.
| **OS** is determined by running `uname -s`.
| **HOSTNAME** by running `hostname` and removing any domain.
| **USER** by running `id -u -n`.

**yadm** will automatically create these links by default. This can be disabled using the `yadm.auto-alt` configuration. Even if disabled, links can be manually created by running **yadm** alt.

## Wildcards

It is possible to use `%` as a "wildcard" in place of `CLASS`, `OS`, `HOSTNAME`,
or `USER`. For example, The following file could be linked for *any host* when the
user is "harvey".

```
$HOME/path/example.txt##%.%.harvey
```

## Class and Overrides

Class is a special value which is stored locally on each host (inside the local
repository). To use alternate symlinks using `CLASS`, you must set the value of
class using the configuration `local.class`. This is set like any other **yadm**
configuration—with the `yadm config` command. The following sets the `CLASS` to
be "Work".

    yadm config local.class Work

Similarly, the values of `OS`, `HOSTNAME`, and `USER` can be manually
overridden using the configuration options `local.os`, `local.hostname`, and
`local.user`.

## Jinja templates

If the `envtpl` command is available, Jinja templates will also be processed to
create or overwrite real files. **yadm** will treat files ending in `##yadm.j2`
as Jinja templates. During processing, the following variables are set according
to the rules explained in the [Alternates section](alternates#symlink-alternates):

* `YADM_CLASS`
* `YADM_OS`
* `YADM_HOSTNAME`
* `YADM_USER`

In addition `YADM_DISTRO` is exposed as the value of `lsb_release -si` if
**lsb_release** is locally available.

For example, a file named `whatever##yadm.j2` with the following content

    {% raw %}
    {% if YADM_USER == 'harvey' -%}
    config={{YADM_CLASS}}-{{ YADM_OS }}
    {% else -%}
    config=dev-whatever
    {% endif -%}
    {% endraw %}

would write a file named `whatever` with the following content if the user is
"harvey":

    config=work-Linux

and the following otherwise:

    config=dev-whatever

See [andreasjansson/envtpl](https://github.com/andreasjansson/envtpl) for more information about
`envtpl`, and see [jinja.pocoo.org](http://jinja.pocoo.org/) for an overview of
Jinja.

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
