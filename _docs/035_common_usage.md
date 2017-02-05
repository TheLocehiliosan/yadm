---
title: "Common Commands"
permalink: /docs/common_commands
---
Most of these operations will look like Git commands; because they are.
**yadm** wraps Git, allowing it to perform all of Git's operations. The
difference is your `$HOME` directory becomes the working directory, and you can
run the commands from any directory.

Commands below which are special to **yadm** are denoted with
<i class="fa fa-fw fa-asterisk" aria-hidden="true"></i>,
and those which are passed directly through to Git are denoted with
<i class="fa fa-fw fa-git-square" aria-hidden="true"></i>.

<i class="fa fa-fw fa-asterisk" aria-hidden="true"></i> `man yadm`
: Display **yadm**'s
[manual](https://github.com/TheLocehiliosan/yadm/blob/master/yadm.md).

<i class="fa fa-fw fa-git-square" aria-hidden="true"></i> `yadm status`
: Show the repository status; added, changed, removed files. Because a `$HOME`
directory often more than only dotfiles, by default
**yadm** ignores untracked files when displaying status.

<i class="fa fa-fw fa-git-square" aria-hidden="true"></i> `yadm push`, `yadm fetch`
: Send or retrive commits to/from your remote repository .

<i class="fa fa-fw fa-git-square" aria-hidden="true"></i> `yadm commit --amend`
: Replace the last commit with a new one. Allows you to change your commit
message or add staged changes to the previous commit.

<i class="fa fa-fw fa-git-square" aria-hidden="true"></i> `yadm diff`
: View changes (uncommitted) you've made to your dotfiles.

<i class="fa fa-fw fa-git-square" aria-hidden="true"></i> `yadm diff --cached`
: View changes staged with `yadm add`. These changes will be added with the next
commit.

<i class="fa fa-fw fa-asterisk" aria-hidden="true"></i> `yadm list -a`
: Print  a list of files managed by **yadm**.  The -a option will cause all managed
files to be listed.  Otherwise, the list will only include files from the
current directory or below.

<i class="fa fa-fw fa-asterisk" aria-hidden="true"></i> `yadm alt`
: Create symbolic links for any managed files matching the alternate naming rules.
Read about [alternate files](alternates) for more details. 

<i class="fa fa-fw fa-asterisk" aria-hidden="true"></i> `yadm encrypt`
: Encrypt all files matching the patterns found in `$HOME/.yadm/encrypt`. Read
about [encryption](encryption) for more details.

<i class="fa fa-fw fa-asterisk" aria-hidden="true"></i> `yadm decrypt`, `yadm decrypt -l`
: Decrypt files stored in `$HOME/.yadm/files.gpg`. Using the `-l` option will
only list the files (without decrypting them). Read about
[encryption](encryption) for more details.

<i class="fa fa-fw fa-asterisk" aria-hidden="true"></i> `yadm clone --bootstrap <URL>`
: Clone the repository from `<URL>`, and automatically run bootstrap if
successful. Read about [bootstrap](bootstrap) for more details.

<i class="fa fa-fw fa-git-square" aria-hidden="true"></i> `yadm remote -v`
: Display detailed information about all configured remote repositories.

<i class="fa fa-fw fa-git-square" aria-hidden="true"></i> `yadm checkout -- <file>`
: Abandon local changes to `<file>`, replacing it with the `HEAD` revision of
`<file>`.

<i class="fa fa-fw fa-git-square" aria-hidden="true"></i> `yadm checkout -b <branch-name>`
: Create a branch called `<branch-name>`, and check the branch out.
