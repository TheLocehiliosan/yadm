---
title: "Upgrading from Version 2"
permalink: /docs/upgrade_from_2
---

Beginning with version 3.0.0, yadm introduced a few major changes which may
require you to adjust your configurations.

## New name for yadm's encrypted archive

yadm now supports openssl in addition to gpg for encryption. Along with this
change, the encrypted archive is now called `archive` instead of the old name
`files.gpg`.

## New locations for data
yadm now uses the [XDG Base Directory Specification][xdg-spec] to find its data.
For the majority of users, this means data will now be in
`$HOME/.local/share/yadm/` instead of the old location of `$HOME/.config/yadm/`.

This location is used for the local repository and encrypted archive.

The easiest way to adopt these new paths is to use the `yadm upgrade` command.
This command will move your existing repo and encrypted archive to the new
directory. Upgrading will also re-initialize all submodules you have added
(otherwise they will be broken when the repo moves).

## Option `yadm.cygwin-copy` is no longer supported
Use the option `yadm.alt-copy` instead.

## Env variable `YADM_COMPATIBILITY=1` is no longer supported
Version 2 supported a version 1 compatibility mode, but this has been removed
from version 3.

[xdg-spec]: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
