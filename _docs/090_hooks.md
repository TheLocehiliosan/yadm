---
title: "Hooks"
permalink: /docs/hooks
---
For every command yadm supports, a program can be provided to run before or
after that command. These are referred to as "hooks". yadm looks for hooks in
the directory
`$HOME/.config/yadm/hooks`.
Each hook is named using a prefix of `pre_` or `post_`, followed by the command
which should trigger the hook. For example, to create a hook which is run after
every `yadm pull` command, create a hook named `post_pull`.
Hooks must have the executable file permission set.

If a `pre_` hook is defined, and the hook terminates with a non-zero exit
status, yadm will refuse to run the yadm command. For example, if a
`pre_commit` hook is defined, but that command ends with a non-zero exit status,
the `yadm commit` will never be run. This allows one to "short-circuit" any
operation using a `pre_` hook.

Hooks have the following environment variables available to them at runtime:

YADM_HOOK_COMMAND
: The command which triggered the hook

YADM_HOOK_EXIT
: The exit status of the yadm command

YADM_HOOK_FULL_COMMAND
: The yadm command with all command line arguments
  (Parameters are space delimited, and any space, tab or backslash will be
  escaped with a backslash. An example of parsing this variable with Bash can be
  found [here][parse-example].)

YADM_HOOK_REPO
: The path to the yadm repository

YADM_HOOK_WORK
: The path to the work-tree

[parse-example]: https://github.com/TheLocehiliosan/yadm/blob/master/contrib/hooks/parsing_full_command_example/pre_log
