---
title: "Installation"
permalink: /docs/install
---
{% include toc title="Platforms" %}

## OSX

**yadm** can be installed using [Homebrew](https://github.com/Homebrew/homebrew).

```
brew install yadm
```

## Fedora/Red Hat/ CentOS (YUM/RPM)

Several yum repositories are on Copr. Follow this link for [repositories and installation instructions](https://copr.fedorainfracloud.org/coprs/thelocehiliosan/yadm/).

## Ubuntu

Beginning with Ubuntu 16.10 _(yakkety)_, a version of **yadm** is available via
standard package repositories.

---

If using an older Ubuntu release, or to get a more up-to-date version of **yadm**, a PPA containing **yadm** exists
[here](https://launchpad.net/~flexiondotorg/+archive/ubuntu/yadm). These
commands should be sufficient to install:

```
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:flexiondotorg/yadm
sudo apt-get update
sudo apt-get -y install yadm
```
---

Otherwise, the instructions for Debian below should also work for Ubuntu.

## Debian

**yadm** is currently in the "testing" release of Debian. If you are using the "stable" release, you can still install **yadm** using the following process.

* First, add the following to `/etc/apt/sources.list`

```
deb http://ftp.debian.org/debian testing main contrib non-free
```

* Next, run `apt-get update -y`

* Last, run `apt-get -t testing install yadm`

If you are using the "unstable" or "testing" release of Debian, you should be able to install **yadm** as you normally install software with `apt-get`.

## Arch Linux

**yadm** is available in the Arch User Repos and can be installed with AUR helper or Makepkg

```
yaourt -S yadm
```

## Gentoo Linux

**yadm** is available in the main gentoo portage tree, simply use `emerge` to install it

```
emerge -atv app-admin/yadm
```

## Other

You *can* simply download the **yadm** script and put it into your `$PATH`. Something like this:

```
curl -fLo /usr/local/bin/yadm https://github.com/TheLocehiliosan/yadm/raw/master/yadm && chmod a+x /usr/local/bin/yadm
```