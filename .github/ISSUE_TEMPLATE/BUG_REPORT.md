---
name: Bug report
about: Create a report to help improve yadm
title: ''
labels: bug
assignees: ''

---
<!--
Before submitting, please search open and closed issues at
https://github.com/TheLocehiliosan/yadm/issues to avoid duplication.

If you have found a security vulnerability, do NOT open an issue.
Email yadm@yadm.io instead.
-->

### Describe the bug

[A clear and concise description of what the bug is.]

### To reproduce

Can this be reproduced with the yadm/testbed docker image: [Yes/No]
<!--
Consider trying to reproduce the bug inside a docker container using the
yadm/testbed docker image. https://hub.docker.com/r/yadm/testbed

The easiest way to start this container, is to clone the TheLocehiliosan/yadm
repo, and use the "scripthost" make target. For example:

  $ git clone https://github.com/TheLocehiliosan/yadm.git
  $ cd yadm
  $ make scripthost version=1.11.0
  Starting scripthost version="1.11.0" (recording script)
  root@scripthost:~# ### run commands which
  root@scripthost:~# ### demonstrate the problem
  root@scripthost:~# ### a succinct set of commands is best
  root@scripthost:~# exit
  logout

  Script saved to script.gz
  $

A script like this can be useful to developers to make a repeatable test for the
problem. You can attach a script.gz file to an issue.
https://help.github.com/en/articles/file-attachments-on-issues-and-pull-requests
-->

Steps to reproduce the behavior:

1. Run command '....'
2. Run command '....'
3. Run command '....'
4. See error

### Expected behavior

[A clear and concise description of what you expected to happen.]

### Environment

 - Operating system: [Ubuntu 18.04, yadm/testbed, etc.]
 - Version yadm: [found via `yadm version`]
 - Version Git: [found via `git --version`]

### Additional context

[Add any other context about the problem here.]
