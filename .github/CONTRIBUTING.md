# Introduction

Thank you for considering contributing to **yadm**. I develop this project in my
limited spare time, so help is very appreciated.

All contributors must follow our [Code of Conduct][conduct]. Please make sure
you are welcoming and friendly during your interactions, and report any
unacceptable behavior to <yadm@yadm.io>.

Contributions can take many forms, and often don’t require writing code—maybe
something could be documented more clearly, maybe a feature could be more
helpful, maybe installation could be easier. Help is welcome in any of these
areas.

To contribute, you can:

* Report [bugs](#reporting-a-bug)
* Request [features/enhancements](#suggesting-a-feature-or-enhancement)
* Contribute changes to [code, tests](#contributing-code), and [documentation](#improving-documentation)
* Maintain installation [packages](#maintaining-packages)
* Help other users by [answering support questions](#answering-support-questions)

# Reporting a bug

Notice something amiss? You’re already helping by reporting the problem! Bugs
are tracked using GitHub issues. Here are some steps you can take to help
problems get fixed quickly and effectively:

### Before submitting an issue

Please take a quick look to see whether the problem has been reported already
(there’s a list of [open issues][open-issues]). You can try the search function
with some related terms for a cursory check. If you do find a previous report,
please add a comment there instead of opening a new issue.

### Security issues

If you have found a security vulnerability, do **NOT** open an issue.

Any security issues should be emailed directly to <yadm@yadm.io>. In order to
determine whether you are dealing with a security issue, ask yourself these two
questions:

* Can I access something that's not mine, or something I shouldn't have access to?
* Can I disable something for other people?

If the answer to either of those two questions is "yes", then you're probably
dealing with a security issue.

### Submitting a (great) bug report

Choose the "[Bug report][new-bug]" issue type.

Pick a descriptive title that clearly identifies the issue.

Describe the steps that led to the problem so that we can go through the same
sequence. A clear set of steps to reproduce the problem is key to fixing an
issue. If possible, attach a [`script.gz`](#attaching-a-scriptgz) to the bug
report.

Describe what you had expected and how that differed from what happened, and
possibly, why.

Include the version numbers of your operating system, of **yadm**, and of Git.

### Attaching a script.gz

Consider trying to reproduce the bug inside a docker container using the
[yadm/testbed][] docker image. Doing so will greatly increase the likelihood of
the problem being fixed.

The easiest way to start this container, is to clone the [TheLocehiliosan/yadm
repo][yadm-repo], and use the `scripthost` make target. _(You will need `make`
and `docker` installed.)_

For example:

```text
$ git clone https://github.com/TheLocehiliosan/yadm.git
$ cd yadm
$ make scripthost version=1.12.0
Starting scripthost version="1.12.0" (recording script)
root@scripthost:~# ### run commands which
root@scripthost:~# ### demonstrate the problem
root@scripthost:~# ### a succinct set of commands is best
root@scripthost:~# exit
logout

Script saved to script.gz
$
```

A `script.gz` like this can be useful to developers to make a repeatable test
for the problem. You can attach the `script.gz` file to an issue. Look
[here][attach-help] for help with [attaching a file][attach-help].

# Suggesting a feature or enhancement

Have an idea for an improvement? Creating a feature request is a good way to
communicate it.

### Before submitting an issue

Please take a quick look to see whether your idea has been suggested already
(there’s a list of [open issues][open-issues]). You can try the search function
with some related terms for a cursory check. If you do find a previous feature
request, please add a comment there instead of opening a new issue.

### Submitting a (great) feature request

Choose the "[Feature request][new-feature]" issue type.

Summarize your idea with a clear title.

Describe your suggestion in as much detail as possible.

Explain alternatives you've considered.

# Contributing code

Wow, thank you for considering making a contribution of code!

### Before you begin

Please take a quick look to see whether a similar change is already being worked
on. A similar pull request may already exist. If the change is related to an
issue, look to see if that issue has an assignee.

Consider reaching out before you start working. It's possible developers may
have some ideas and code lying around, and might be able to give you a head
start.

[Creating a hook][hooks-help] is an easy way to begin adding features to an
already existing **yadm** operation. If the hook works well, it could be the
basis of a **yadm** feature addition. Or it might just be a [useful
hook][contrib-hooks] for someone else.

### Design principles

**yadm** was created with a few core design principles in mind. Please adhere to
these principles when making changes.

* **Single repository**
    * **yadm** is designed to maintain dotfiles in a single repository.

* **Very few dependencies**
    * **yadm** should be as portable as possible. This is one of the main
      reasons it has only two dependencies (Bash and Git). Features using other
      dependencies should gracefully downgrade instead of breaking. For example,
      encryption requires GnuPG installed, and displays that information if it
      is not.

* **Sparse configuration**
    * **yadm** should require very little configuration, and come with sensible
      defaults. Changes requiring users to define meta-data for all of their
      dotfiles will not be accepted.

* **Maintain dotfiles in place**
    * The default treatment for tracked data should be to allow it to remain a
      file, in the location it is normally kept.

* **Leverage Git**
    * Stay out of the way and let Git do what it’s good at. Git has a deep and
      rich set of features for just about every use case. Staying hands off for
      almost all Git operations will make **yadm** more flexible and
      future-proof.

### Repository branches and tags

* `master`
    * This branch will always represent the latest release of **yadm**.
* `#.#.#` _(tags)_
    * Every release of **yadm** will have a commit tagged with the version number.
* `develop`
    * This branch should be used for the basis of every change. As changes are
      accepted, they will be merged into `develop`.
* `release/*`
    * These are ephemeral branches used to prepare new releases.
* `hotfix/*`
    * These are ephemeral branches used to prepare a patch release, which only
      includes bug fixes.
* `gh-pages`
    * This branch contains the yadm.io website source.
* `dev-pages`
    * This branch should be used for the basis of every website change. As
      changes are accepted, they will be merged into dev-pages.
* `netlify/*`
    * These branches deploy configurations to Netlify websites. Currently this
      is only used to drive redirections for
      [bootstrap.yadm.io](https://bootstrap.yadm.io/).

### GitHub workflow

1. Fork the [yadm repository][yadm-repo] on GitHub.

2. Clone your fork locally.

    ```text
    $ git clone <url-to-your-fork>
    ```

3. Add the official repository (`upstream`) as a remote repository.

    ```text
    $ git remote add upstream https://github.com/TheLocehiliosan/yadm.git
    ```

4. Verify you can run the test harness. _(This will require dependencies:
   `make`, `docker`, and `docker-compose`)_.

    ```text
    $ make test
    ```

5. Create a feature branch, based off the `develop` branch.

    ```text
    $ git checkout -b <name-of-feature-branch> upstream/develop
    ```

6. Add changes to your feature branch.

7. If your changes take a few days, be sure to occasionally pull the latest
   changes from upstream, to ensure that your local branch is up-to-date.

    ```text
    $ git pull --rebase upstream develop
    ```

8. When your work is done, push your local branch to your fork.

    ```text
    $ git push origin <name-of-feature-branch>
    ```

9. [Create a pull request][pr-help] using `develop` as the "base".

### Code conventions

When updating the yadm code, please follow these guidelines:

* Code linting
    * Bash code should pass the scrutiny of [ShellCheck][shellcheck].
    * Python code must pass the scrutiny of [pylint][] and [flake8][].
    * Any YAML must pass the scrutiny of [yamllint][].
    * Running `make test_syntax.py` is an easy way to run all linters.
* Interface changes
    * Any changes to **yadm**'s interface should include a commit that updates
      the `yadm.1` man page.

### Test conventions

The test system is written in Python 3 using [pytest][]. Tests should be written
for all bugs fixed and features added. To make testing portable and uniform,
tests should be performed via the [yadm/testbed][] docker image. The `Makefile`
has several "make targets" for testing. Running `make` by itself will produce a
help page.

Please follow these guidelines while writing tests:

* Organization
    * Tests should be kept in the `test/` directory.
    * Every test module name should start with `test_`.
    * Unit tests, which test individual functions should have names that begin
      with `test_unit_`.
    * Completely new features should get their own test modules, while updates
      to existing features should have updated test modules.
* Efficiency
    * Care should be taken to make tests run as efficiently as possible.
    * Scope large, unchanging, fixtures appropriately so they do not have to be
      recreated multiple times.

### Commit conventions

When arranging your commits, please adhere to the following conventions.

* Commit messages
    * Use the "[Tim Pope][tpope-style]" style of commit messages. Here is a
      [great guide][commit-style] to writing commit messages.
* Atomic commits
    * Please create only [atomic commits][atomic-commits].
* Signed commits
    * All commits must be [cryptographically signed][signing-commits].

# Improving documentation

Wow, thank you for considering making documentation improvements!

There is overlap between the content of the man page, and the information on the
website. Consider reviewing both sets of documentation, and submitting similar
changes for both to improve consistency.

### Man page changes

The man page documentation is contained in the file `yadm.1`. This file is
formatted using [groff man macros][groff-man]. Changes to this file can be
tested using "make targets":

```text
$ make man
$ make man-wide
$ make man-ps
```

While the [markdown version of the man page][yadm-man] is generated from
`yadm.1`, please do not include changes to `yadm.md` within any pull request.
That file is only updated during software releases.

### Website changes

The yadm.io website is generated using [Jekyll][jekyll]. The bulk of the
documentation is created as an ordered collection within `_docs`. To make
website testing easy and portable, use the [yadm/jekyll][] docker image. The
`Makefile` has several "make targets" for testing. Running `make` by itself will
produce a help page.

* `make test`:
    Perform tests done by continuous integration.
* `make up`:
    Start a container to locally test the website. The test website will be
    hosted at http://localhost:4000/
* `make clean`:
    Remove previously built data any any Jekyll containers.

When making website changes, be sure to adhere to [code](#code-conventions) and
[commit](#commit-conventions) conventions. Use the same [GitHub
workflow](#github-workflow) when creating a pull request. However use the
`dev-pages` branch as a base instead of `develop`.

# Maintaining packages

Maintaining installation packages is very important for making **yadm**
accessible to as many people as possible. Thank you for considering contributing
in this way. Please consider the following:

* Watch releases
    * GitHub allows users to "watch" a project for "releases". Doing so will
      provide you with notifications when a new version of **yadm** has been
      released.
* Include License
    * Any package of **yadm** should include the license file from the
      repository.
* Dependencies
    * Be sure to include dependencies in a manner appropriate to the packaging
      system being used. **yadm** won't work very well without Git. :)

# Answering support questions

Are you an experienced **yadm** user, with an advanced knowledge of Git? Your
expertise could be useful to someone else who is starting out or struggling with
a problem. Consider reviewing the list of [open support questions][questions] to
see if you can help.

[atomic-commits]: https://www.google.com/search?q=atomic+commits
[attach-help]: https://help.github.com/en/articles/file-attachments-on-issues-and-pull-requests
[commit-style]: https://chris.beams.io/posts/git-commit/#seven-rules
[conduct]: CODE_OF_CONDUCT.md
[contrib-hooks]: https://github.com/TheLocehiliosan/yadm/tree/master/contrib/hooks
[flake8]: https://pypi.org/project/flake8/
[groff-man]: https://www.gnu.org/software/groff/manual/html_node/man.html
[hooks-help]: https://github.com/TheLocehiliosan/yadm/blob/master/yadm.md#hooks
[html-proofer]: https://github.com/gjtorikian/html-proofer
[jekyll]: https://jekyllrb.com
[new-bug]: https://github.com/TheLocehiliosan/yadm/issues/new?template=BUG_REPORT.md
[new-feature]: https://github.com/TheLocehiliosan/yadm/issues/new?template=FEATURE_REQUEST.md
[open-issues]: https://github.com/TheLocehiliosan/yadm/issues
[pr-help]: https://help.github.com/en/articles/creating-a-pull-request-from-a-fork
[pylint]: https://pylint.org/
[pytest]: https://pytest.org/
[questions]: https://github.com/TheLocehiliosan/yadm/labels/question
[refactor]: https://github.com/TheLocehiliosan/yadm/issues/146
[shellcheck]: https://www.shellcheck.net
[signing-commits]: https://help.github.com/en/articles/signing-commits
[tpope-style]: https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
[yadm-man]: https://github.com/TheLocehiliosan/yadm/blob/master/yadm.md
[yadm-repo]: https://github.com/TheLocehiliosan/yadm
[yadm/jekyll]: https://hub.docker.com/r/yadm/jekyll
[yadm/testbed]: https://hub.docker.com/r/yadm/testbed
[yamllint]: https://github.com/adrienverge/yamllint
