---
title: "Encryption"
permalink: /docs/encryption
---
It can be useful to manage confidential files, like SSH keys, across multiple
systems. However, doing so would put plain text data into a Git repository,
which often resides on a public system. **yadm** implements a feature which can
make it easy to encrypt and decrypt a set of files so the encrypted version can
be maintained in the Git repository. This feature will only work if the gpg
command is available.
_It is recommended that you use a private repository when keeping confidential
files, even though they are encrypted._

To use this feature, a list of patterns must be created and saved as
`$HOME/.yadm/encrypt`. For example:

    .ssh/*.key

The `yadm encrypt` command will find all files matching the patterns, and
prompt for a password. Once a password has confirmed, the matching files will be
encrypted and saved as `$HOME/.yadm/files.gpg`. The patterns and files.gpg
should be added to the **yadm** repository so they are available across multiple
systems.

    yadm add .yadm/encrypt
    yadm add .yadm/files.gpg

To decrypt these files later, or on another system run `yadm decrypt` and
provide the correct password.
_By default, any decrypted files will have their "group" and "others"
permissions removed._

### Asymmetric Encryption

Symmetric encryption is used by default, but asymmetric encryption may
be enabled using the `yadm.gpg-recipient` configuration. To do so, run:

    yadm config yadm.gpg-recipient <recipient-address>

For this to work, `<recipient-address>` must exist in your gpg keyrings.
