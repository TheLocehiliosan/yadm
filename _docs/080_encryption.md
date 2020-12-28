---
title: "Encryption"
permalink: /docs/encryption
---
It can be useful to manage confidential files, like SSH keys, across multiple
systems. However, doing so would put plain text data into a Git repository,
which often resides on a public system. yadm implements a feature which can
make it easy to encrypt and decrypt a set of files so the encrypted version can
be maintained in the Git repository. This feature will only work if the gpg or
openssl commands are available. To use OpenSSL see the section lower on this
page.
_It is recommended that you use a private repository when keeping confidential
files, even though they are encrypted._

To use this feature, a list of patterns must be created and saved as
`$HOME/.config/yadm/encrypt`. For example:

    .ssh/*.key

The `yadm encrypt` command will find all files matching the patterns, and prompt
for a password. Once a password has confirmed, the matching files will be
encrypted and saved as `$HOME/.local/share/yadm/archive`. The patterns and
`archive` should be added to the yadm repository so they are available across
multiple systems.

    yadm add .config/yadm/encrypt
    yadm add .local/share/yadm/archive

To decrypt these files later, or on another system run `yadm decrypt` and
provide the correct password.
_By default, any decrypted files will have their "group" and "others"
permissions removed._

### Asymmetric Encryption

Symmetric encryption is used by default, but asymmetric encryption may
be enabled using the `yadm.gpg-recipient` configuration. To do so, run:

    yadm config yadm.gpg-recipient <recipient-address>

For this to work, `<recipient-address>` must exist in your gpg keyrings.

## OpenSSL

OpenSSL can be used instead of gpg by specifying the option `yadm.cipher`,
setting it to "openssl".

    yadm config yadm.cipher openssl

There are a few other options to control how the OpenSSL archive is created.

* `yadm.openssl-ciphername` determines the cipher algorithm used. "aes-256-cbc"
  is used by default.
* `yadm.openssl-old` is a boolean option that uses parameters more suitable for
  older versions of OpenSSL. This option defaults to "false".

## transcrypt & git-crypt

transcrypt & git-crypt are tools that enable transparent encryption and
decryption of files in a Git repository. If installed, you can use either of
these tools with your yadm repository.

Simply use it normally, prefacing the `transcrypt` or `git-crypt` commands with
`yadm`.

Learn more about these tools here:

* [transcrypt](https://github.com/elasticdog/transcrypt)
* [git-crypt](https://github.com/AGWA/git-crypt)
