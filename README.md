# yadm - Yet Another Dotfiles Manager

[![Latest Version][releases-badge]][releases-link]
[![Homebrew Version][homebrew-badge]][homebrew-link]
[![OBS Version][obs-badge]][obs-link]
[![Arch Version][aur-badge]][aur-link]
[![License][license-badge]][license-link]<br />
[![Master Update][master-date]][master-commits]
[![Develop Update][develop-date]][develop-commits]
[![Website Update][website-date]][website-commits]<br />
[![Master Status][master-badge]][workflow-master]
[![Develop Status][develop-badge]][workflow-develop]
[![GH Pages Status][gh-pages-badge]][workflow-gh-pages]
[![Dev Pages Status][dev-pages-badge]][workflow-dev-pages]

[https://yadm.io/][website-link]

**yadm** is a tool for managing [dotfiles][].

* Based on [Git][], with full range of Git's features
* Supports system-specific alternative files or templated files
* Encryption of private data using [GnuPG][], [OpenSSL][], [transcrypt][], or
  [git-crypt][]
* Customizable initialization (bootstrapping)
* Customizable hooks for before and after any operation

Complete features, usage, examples and installation instructions can be found on
the [yadm.io][website-link] website.

## A very quick tour

    # Initialize a new repository
    yadm init

    # Clone an existing repository
    yadm clone <url>

    # Add files/changes
    yadm add <important file>
    yadm commit

    # Encrypt your ssh key
    echo '.ssh/id_rsa' > ~/.config/yadm/encrypt
    yadm encrypt

    # Later, decrypt your ssh key
    yadm decrypt

    # Create different files for Linux vs MacOS
    yadm add path/file.cfg##os.Linux
    yadm add path/file.cfg##os.Darwin

If you enjoy using yadm, consider adding a star to the repository on GitHub.
The star count helps others discover yadm.

[Git]: https://git-scm.com/
[GnuPG]: https://gnupg.org/
[OpenSSL]: https://www.openssl.org/
[aur-badge]: https://img.shields.io/aur/version/yadm.svg
[aur-link]: https://aur.archlinux.org/packages/yadm
[dev-pages-badge]: https://img.shields.io/github/workflow/status/TheLocehiliosan/yadm/Test%20Site/dev-pages?label=dev-pages
[develop-badge]: https://img.shields.io/github/workflow/status/TheLocehiliosan/yadm/Tests/develop?label=develop
[develop-commits]: https://github.com/TheLocehiliosan/yadm/commits/develop
[develop-date]: https://img.shields.io/github/last-commit/TheLocehiliosan/yadm/develop.svg?label=develop
[dotfiles]: https://en.wikipedia.org/wiki/Hidden_file_and_hidden_directory
[gh-pages-badge]: https://img.shields.io/github/workflow/status/TheLocehiliosan/yadm/Test%20Site/gh-pages?label=gh-pages
[git-crypt]: https://github.com/AGWA/git-crypt
[homebrew-badge]: https://img.shields.io/homebrew/v/yadm.svg
[homebrew-link]: https://formulae.brew.sh/formula/yadm
[license-badge]: https://img.shields.io/github/license/TheLocehiliosan/yadm.svg
[license-link]: https://github.com/TheLocehiliosan/yadm/blob/master/LICENSE
[master-badge]: https://img.shields.io/github/workflow/status/TheLocehiliosan/yadm/Tests/master?label=master
[master-commits]: https://github.com/TheLocehiliosan/yadm/commits/master
[master-date]: https://img.shields.io/github/last-commit/TheLocehiliosan/yadm/master.svg?label=master
[obs-badge]: https://img.shields.io/badge/OBS-v3.1.0-blue
[obs-link]: https://software.opensuse.org//download.html?project=home%3ATheLocehiliosan%3Ayadm&package=yadm
[releases-badge]: https://img.shields.io/github/tag/TheLocehiliosan/yadm.svg?label=latest+release
[releases-link]: https://github.com/TheLocehiliosan/yadm/releases
[transcrypt]: https://github.com/elasticdog/transcrypt
[travis-ci]: https://travis-ci.com/TheLocehiliosan/yadm/branches
[website-commits]: https://github.com/TheLocehiliosan/yadm/commits/gh-pages
[website-date]: https://img.shields.io/github/last-commit/TheLocehiliosan/yadm/gh-pages.svg?label=website
[website-link]: https://yadm.io/
[workflow-dev-pages]: https://github.com/thelocehiliosan/yadm/actions?query=workflow%3a%22test+site%22+branch%3adev-pages
[workflow-develop]: https://github.com/TheLocehiliosan/yadm/actions?query=workflow%3ATests+branch%3Adevelop
[workflow-gh-pages]: https://github.com/thelocehiliosan/yadm/actions?query=workflow%3a%22test+site%22+branch%3agh-pages
[workflow-master]: https://github.com/TheLocehiliosan/yadm/actions?query=workflow%3ATests+branch%3Amaster
