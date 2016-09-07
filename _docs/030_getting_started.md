---
title: "Getting Started"
permalink: /docs/getting_started
---
Starting out with **yadm** should be just a few easy steps.

### If you don't currently have a repository
Start out with an empty local repository

    yadm init
    yadm add <important file>
    yadm commit

Eventually you will want to push the local repo to a remote.

    yadm remote add origin <url>
    yadm push -u origin master

### If you have an existing remote repository
Clone your existing repo using **yadm**.

    yadm clone <url>
    yadm status

The `clone` command will attempt to `merge` your existing repository, but if it
fails, it will do a `reset` instead and you'll have to decide best on how
resolve the differences. See
[this question](faq#i-just-cloned-my-repository-but-yadm-status-shows-conflicts-why)
in the FAQ if you need help.

---

That's all it takes to start. Now most Git commands can be used as
`yadm <git command>`.
Read about [common commands](common_commands) for ideas.
