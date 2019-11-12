---
title: "Upgrading from Version 1"
permalink: /docs/upgrade_from_1
---

Beginning with version 2.0.0, yadm introduced a few major changes which may
require you to adjust your configurations.

If you want to retain yadm's old behavior until you transition your
configurations, you can set an environment variable `YADM_COMPATIBILITY=1`.
Doing so will automatically use the old yadm directory, and process alternates the same as version 1.
This compatibility mode is deprecated, and will be removed in future versions.
This mode exists solely for transitioning to the new paths and naming of alternates.

## New yadm directory location
yadm now uses the [XDG Base Directory Specification][xdg-spec] to find its configurations.
For the majority of users, this means configurations will now be in
`$HOME/.config/yadm` instead of the old location of `$HOME/.yadm`.

You can customize the base directory by specifying an environment variable
named `XDG_CONFIG_HOME`.

If you previously had configurations in `$HOME/.yadm`, the easiest way
to migrate is to use the new `yadm upgrade` command. This command will move your
existing repo and configurations to the new directory, and rename any yadm
configurations that are tracked by your repo. Upgrading will also re-initialize
all submodules you have added (otherwise they will be broken when the repo
moves).

## New alternate file naming convention
The naming conventions for alternate files have been changed.
Read full details about the new naming convention [here](/docs/alternates).

This table of examples should help you understand how to translate old filenames
to new ones.

| Conditions                                             | Old suffix                  | New suffix                        |
| -                                                      | -                           | -                                 |
| Default file                                           | `##`                        | `##default`                       |
| MacOS host                                             | `##Darwin`                  | `##o.Darwin`                      |
| yadm.class = "work"                                    | `##work`                    | `##c.work`                        |
| Linux host named "dromio"                              | `##Linux.dromio`            | `##o.Linux,h.dromio`              |
| Linux host named "dromio" with user named "antipholus" | `##Linux.dromio.antipholus` | `##o.Linux,h.dromio,u.antipholus` |
| Host named "luciana"                                   | `##%.luciana`               | `##h.luciana`                     |
| Any Linux host with user named "egeon"                 | `##Linux.%.egeon`           | `##o.Linux,u.egeon`               |
| User named "balthazar"                                 | `##%.%.balthazar`           | `##u.balthazar`                   |
| A Jinja template                                       | `##yadm.j2`                 | `##template.j2`                   |

## Built-in template processing
Older versions supported Jinja templates if envtpl was installed. New versions
support _multiple_ template processors, including a built-in processor. The
built-in processor has a limited feature set, but should be sufficient for most
users needs (without having to install additional software). Read full details
[here](/docs/templates).

## Option `yadm.cygwin-copy` changed to `yadm.alt-copy`
Older versions supported a `yadm.cygwin-copy` option, because some software
doesn't work well with CYGWIN symlinks. Now that option has been renamed to
`yadm.alt-copy`, and can be used on any system, not just CYGWIN. So if you have
a system which doesn't fully support symlinks, you can have alternates created
as files instead.

[xdg-spec]: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
