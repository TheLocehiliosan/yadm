---
title: "Installation"
permalink: /docs/install
---
{% include toc title="Platforms" %}

## OSX

yadm can be installed using [Homebrew][homebrew].

```
brew install yadm
```

## RPM Based Installations

For RPM based systems like Fedora, Red Hat, CentOS, openSUSE, etc, there are
repositories hosted by openSUSE Build Service.

Follow this link for [repositories and installation instructions][OBS].

## Ubuntu/Debian

A version of yadm is available via standard package repositories. Use `apt-get` to install.

## Arch Linux

yadm is available in the Arch User Repos and can be installed with AUR helper or Makepkg.

```
yaourt -S yadm-git
```

## Gentoo Linux

yadm is available in the main gentoo portage tree, simply use `emerge` to install it.

```
emerge -atv app-admin/yadm
```

## Void Linux

yadm is available in the official repository, simply use `xbps-install` to install it.

```
xbps-install yadm
```

## FreeBSD

yadm is available in the FreeBSD ports. Use `pkg` to install it from a prebuilt binary package:

```
pkg install yadm
```

## Download

You *can* simply download the yadm script and put it into your `$PATH`. Something like this:

```
curl -fLo /usr/local/bin/yadm https://github.com/TheLocehiliosan/yadm/raw/master/yadm && chmod a+x /usr/local/bin/yadm
```

Of course, you can change the file paths above to be appropriate for your `$PATH` and situation.

## Clone

You might wish to clone the yadm project and symlink `yadm` into your
`$PATH`.

```
git clone https://github.com/TheLocehiliosan/yadm.git ~/.yadm-project
ln -s ~/.yadm-project/yadm ~/bin/yadm
```

Now you can pull the latest updates to yadm using Git. Again, adjust the
file paths above to be appropriate for your `$PATH` and situation.

## Submodule

If you are comfortable with how Git submodules  work, another option is to add
the yadm project as a submodule and symlink `yadm` into your `$PATH`.

```
cd ~
yadm submodule add https://github.com/TheLocehiliosan/yadm.git .yadm-project
yadm submodule update --init --recursive
ln -s ~/.yadm-project/yadm ~/bin/yadm
yadm add .yadm-project .gitmodules bin/yadm
yadm commit
```
When using submodules, you need to initialize them each time you do a fresh
`clone` of your dotfiles.

```
yadm submodule update --init --recursive
```

Updating to a newer version of yadm would use commands similar to this.

```
cd ~/.yadm-project
git pull
yadm add ~/.yadm-project
yadm commit
```

Again, adjust the file paths above to be appropriate for your `$PATH` and
situation.

You can find more information about Git submodules by reading the
[git-submodule][git-submodule] man page.

[OBS]: https://software.opensuse.org//download.html?project=home%3ATheLocehiliosan%3Ayadm&package=yadm
[git-submodule]: https://git-scm.com/docs/git-submodule
[homebrew]: https://github.com/Homebrew/homebrew
