---
title: "Overview"
permalink: /docs/overview
---
> You've spent time tweaking your computing environment. Everything operates the
  way you want. That's fantastic! Then your hard drive fails, and the computer
  needs to be rebuilt. **yadm** can restore you configurations.

> You get a new computer, and you want to recreate that environment. You
  probably want to keep both machines' configurations in sync. **yadm** can help
  you coordinate the configurations between your machines.

> You begin experimenting with new changes to your configurations, and now
  everything is broken. **yadm** can help you determine what changed or simply
  revert all of your changes.

**yadm** is like having a version of Git, that only operates on your dotfiles.
 If you know how to use Git, you already know how to use yadm.

* It doesn't matter if your current directory is another Git-managed repository
* You don't have to move your dotfiles, or have them symlinked from another
  location.
* **yadm** automatically inherits all of Git's features, allowing you to branch,
  merge, rebase, use submodules, etc.

As so many others, I started out with a repository of dotfiles and a few scripts
to symbolically link them around my home directory. This quickly became
inadequate and I looked for solutions elsewhere. I've tried other tools, but I
didn't find all of the features I personally wished for in a single tool. This
led to **yadm** being written with the following goals:

* Use a single repository
* Few dependencies
* Ability to use alternate files based on OS or host
* Ability to encrypt and track confidential files
* Stay out of the way and let Git do what it's good at

Follow these links to [install](install) **yadm**
or
learn some simple steps for [getting started](getting_started) with **yadm**.
