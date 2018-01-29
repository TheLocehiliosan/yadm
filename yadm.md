


## NAME
       yadm - Yet Another Dotfiles Manager

## SYNOPSIS
       yadm command [options]

       yadm git-command-or-alias [options]

       yadm init [-f] [-w directory]

       yadm clone url [-f] [-w directory] [--bootstrap] [--no-bootstrap]

       yadm config name [value]

       yadm config [-e]

       yadm list [-a]

       yadm bootstrap

       yadm encrypt

       yadm enter

       yadm decrypt [-l]

       yadm alt

       yadm perms

       yadm introspect category

## DESCRIPTION
       yadm  is a tool for managing a collection of files across multiple com-
       puters, using a shared Git repository.  In addition,  yadm  provides  a
       feature  to  select  alternate versions of files based on the operating
       system or host name.  Lastly, yadm supplies the  ability  to  manage  a
       subset of secure files, which are encrypted before they are included in
       the repository.

## COMMANDS
       git-command or git-alias
              Any command not internally handled by yadm is passed through  to
              git(1).   Git commands or aliases are invoked with the yadm man-
              aged repository.  The working directory for Git commands will be
              the configured work-tree (usually $HOME).

              Dotfiles  are  managed by using standard git commands; add, com-
              mit, push, pull, etc.

              The config command is not passed directly through.  Instead  use
              the gitconfig command (see below).

       alt    Create  symbolic  links and process Jinja templates for any man-
              aged files matching the naming rules described in the ALTERNATES
              and  JINJA  sections. It is usually unnecessary to run this com-
              mand, as yadm automatically  processes  alternates  by  default.
              This  automatic behavior can be disabled by setting the configu-
              ration yadm.auto-alt to "false".

       bootstrap
              Execute $HOME/.yadm/bootstrap if it exists.

       clone url
              Clone a remote repository for tracking dotfiles.  After the con-
              tents  of  the remote repository have been fetched, a "merge" of
              origin/master is attempted.   If  there  are  conflicting  files
              already  present  in  the  work-tree,  this  merge will fail and
              instead a "reset" of origin/master will be done, followed  by  a
              "stash". This "stash" operation will preserve the original data.

              You can review the stashed conflicts by running the command

                     yadm stash show -p

              from within your $HOME directory. If you  want  to  restore  the
              stashed data, you can run

                     yadm stash apply
              or
                     yadm stash pop

              The  repository  is stored in $HOME/.yadm/repo.git.  By default,
              $HOME will be used as the work-tree, but this can be  overridden
              with the -w option.  yadm can be forced to overwrite an existing
              repository by providing the -f option.  By default yadm will ask
              the  user if the bootstrap program should be run (if it exists).
              The options --bootstrap or --no-bootstrap will either force  the
              bootstrap  to  be  run,  or  prevent  it from being run, without
              prompting the user.

       config This command manages  configurations  for  yadm.   This  command
              works  exactly  they way git-config(1) does.  See the CONFIGURA-
              TION section for more details.

       decrypt
              Decrypt  all  files  stored  in  $HOME/.yadm/files.gpg.    Files
              decrypted  will be relative to the configured work-tree (usually
              $HOME).  Using the -l option will list the files stored  without
              extracting them.

       encrypt
              Encrypt    all    files   matching   the   patterns   found   in
              $HOME/.yadm/encrypt.   See  the  ENCRYPTION  section  for   more
              details.

       enter  Run  a  sub-shell with all Git variables set. Exit the sub-shell
              the same way you leave  your  normal  shell  (usually  with  the
              "exit"  command).  This sub-shell can be used to easily interact
              with your yadm repository using "git" commands.  This  could  be
              useful  if  you  are  using  a tool which uses Git directly. For
              example, Emacs Tramp and Magit can manage files  by  using  this
              configuration:
                  (add-to-list 'tramp-methods
                       '("yadm"
                         (tramp-login-program "yadm")
                         (tramp-login-args (("enter")))
                         (tramp-remote-shell "/bin/sh")
                         (tramp-remote-shell-args ("-c"))))

       gitconfig
              Pass  options to the git config command. Since yadm already uses
              the config command to manage its own configurations,  this  com-
              mand is provided as a way to change configurations of the repos-
              itory managed by yadm.  One useful case might  be  to  configure
              the  repository so untracked files are shown in status commands.
              yadm initially configures its repository so that untracked files
              are  not  shown.   If  you wish use the default Git behavior (to
              show untracked files and directories), you can remove this  con-
              figuration.

                     yadm gitconfig --unset status.showUntrackedFiles

       help   Print a summary of yadm commands.

       init   Initialize  a  new, empty repository for tracking dotfiles.  The
              repository is stored in $HOME/.yadm/repo.git.  By default, $HOME
              will  be  used as the work-tree, but this can be overridden with
              the -w option.  yadm can be  forced  to  overwrite  an  existing
              repository by providing the -f option.

       list   Print a list of files managed by yadm.  The -a option will cause
              all managed files to be listed.  Otherwise, the list  will  only
              include files from the current directory or below.

       introspect category
              Report  internal  yadm  data. Supported categories are commands,
              configs, repo, and switches.  The purpose of introspection is to
              support command line completion.

       perms  Update  permissions as described in the PERMISSIONS section.  It
              is usually unnecessary to run this command,  as  yadm  automati-
              cally processes permissions by default.  This automatic behavior
              can be disabled by setting the configuration yadm.auto-perms  to
              "false".

       version
              Print the version of yadm.

## OPTIONS
       yadm  supports a set of universal options that alter the paths it uses.
       The default paths are documented in the FILES section.  Any path speci-
       fied  by  these options must be fully qualified.  If you always want to
       override one or more of these paths, it may  be  useful  to  create  an
       alias  for the yadm command.  For example, the following alias could be
       used to override the repository directory.

              alias yadm='yadm --yadm-repo /alternate/path/to/repo'

       The following is the full  list  of  universal  options.   Each  option
       should be followed by a fully qualified path.

       -Y,--yadm-dir
              Override  the  yadm directory.  yadm stores its data relative to
              this directory.

       --yadm-repo
              Override the location of the yadm repository.

       --yadm-config
              Override the location of the yadm configuration file.

       --yadm-encrypt
              Override the location of the yadm encryption configuration.

       --yadm-archive
              Override the location of the yadm encrypted files archive.

       --yadm-bootstrap
              Override the location of the yadm bootstrap program.

## CONFIGURATION
       yadm uses a configuration file  named  $HOME/.yadm/config.   This  file
       uses  the same format as git-config(1).  Also, you can control the con-
       tents of the configuration file via  the  yadm  config  command  (which
       works exactly like git-config).  For example, to disable alternates you
       can run the command:

              yadm config yadm.auto-alt false

       The following is the full list of supported configurations:

       yadm.auto-alt
              Disable the automatic linking described in  the  section  ALTER-
              NATES.  If disabled, you may still run yadm alt manually to cre-
              ate the alternate links.  This feature is enabled by default.

       yadm.auto-perms
              Disable the automatic permission changes described in  the  sec-
              tion  PERMISSIONS.   If  disabled,  you may still run yadm perms
              manually to update permissions.   This  feature  is  enabled  by
              default.

       yadm.auto-private-dirs
              Disable  the automatic creating of private directories described
              in the section PERMISSIONS.

       yadm.ssh-perms
              Disable the permission changes to $HOME/.ssh/*.  This feature is
              enabled by default.

       yadm.gpg-perms
              Disable  the permission changes to $HOME/.gnupg/*.  This feature
              is enabled by default.

       yadm.gpg-recipient
              Asymmetrically encrypt files with a gpg public/private key pair.
              Provide  a "key ID" to specify which public key to encrypt with.
              The key must exist in your public keyrings.  If  left  blank  or
              not  provided,  symmetric encryption is used instead.  If set to
              "ASK", gpg will  interactively  ask  for  recipients.   See  the
              ENCRYPTION  section  for more details.  This feature is disabled
              by default.

       yadm.gpg-program
              Specify an alternate  program  to  use  instead  of  "gpg".   By
              default, the first "gpg" found in $PATH is used.

       yadm.git-program
              Specify  an  alternate  program  to  use  instead  of "git".  By
              default, the first "git" found in $PATH is used.

       yadm.cygwin-copy
              If set to "true", for Cygwin  hosts,  alternate  files  will  be
              copies  instead  of  symbolic  links.  This  might be desirable,
              because non-Cygwin software may not  properly  interpret  Cygwin
              symlinks.

       These   last   four  "local"  configurations  are  not  stored  in  the
       $HOME/.yadm/config, they are stored in the local repository.


       local.class
              Specify a CLASS for the purpose of symlinking  alternate  files.
              By default, no CLASS will be matched.

       local.os
              Override the OS for the purpose of symlinking alternate files.

       local.hostname
              Override  the  HOSTNAME  for the purpose of symlinking alternate
              files.

       local.user
              Override the USER for the purpose of symlinking alternate files.

## ALTERNATES
       When managing a set of files across different systems, it can be useful
       to have an automated way of choosing an alternate version of a file for
       a different operating system, host, or user.  yadm implements a feature
       which will automatically create a symbolic link to the appropriate ver-
       sion  of  a  file,  as long as you follow a specific naming convention.
       yadm can detect files with names ending in any of the following:

         ##
         ##CLASS
         ##CLASS.OS
         ##CLASS.OS.HOSTNAME
         ##CLASS.OS.HOSTNAME.USER
         ##OS
         ##OS.HOSTNAME
         ##OS.HOSTNAME.USER

       If there are any files managed  by  yadm's  repository,  or  listed  in
       $HOME/.yadm/encrypt, which match this naming convention, symbolic links
       will be created for the most appropriate version.   This  may  best  be
       demonstrated  by  example.  Assume  the  following files are managed by
       yadm's repository:

         - $HOME/path/example.txt##
         - $HOME/path/example.txt##Work
         - $HOME/path/example.txt##Darwin
         - $HOME/path/example.txt##Darwin.host1
         - $HOME/path/example.txt##Darwin.host2
         - $HOME/path/example.txt##Linux
         - $HOME/path/example.txt##Linux.host1
         - $HOME/path/example.txt##Linux.host2

       If running on a Macbook named "host2", yadm will create a symbolic link
       which looks like this:

       $HOME/path/example.txt -> $HOME/path/example.txt##Darwin.host2

       However, on another Mackbook named "host3", yadm will create a symbolic
       link which looks like this:

       $HOME/path/example.txt -> $HOME/path/example.txt##Darwin

       Since the hostname doesn't match any of the  managed  files,  the  more
       generic version is chosen.

       If running on a Linux server named "host4", the link will be:

       $HOME/path/example.txt -> $HOME/path/example.txt##Linux

       If running on a Solaris server, the link use the default "##" version:

       $HOME/path/example.txt -> $HOME/path/example.txt##

       If running on a system, with CLASS set to "Work", the link will be:

       $HOME/path/example.txt -> $HOME/path/example.txt##WORK

       If no "##" version exists and no files match the current CLASS/OS/HOST-
       NAME/USER, then no link will be created.

       Links are also created for directories named this way, as long as  they
       have at least one yadm managed file within them.

       CLASS  must  be manually set using yadm config local.class <class>.  OS
       is determined by running uname -s, HOSTNAME by  running  hostname,  and
       USER  by  running id -u -n.  yadm will automatically create these links
       by default. This can be disabled using the yadm.auto-alt configuration.
       Even if disabled, links can be manually created by running yadm alt.

       It  is possible to use "%" as a "wildcard" in place of CLASS, OS, HOST-
       NAME, or USER. For example, The following file could be linked for  any
       host when the user is "harvey".

       $HOME/path/example.txt##%.%.harvey

       CLASS  is  a special value which is stored locally on each host (inside
       the local repository). To use alternate symlinks using CLASS, you  must
       set  the  value  of class using the configuration local.class.  This is
       set like any other yadm configuration with the yadm config command. The
       following sets the CLASS to be "Work".

         yadm config local.class Work

       Similarly,  the  values of OS, HOSTNAME, and USER can be manually over-
       ridden using the configuration options  local.os,  local.hostname,  and
       local.user.


## JINJA
       If  the  envtpl command is available, Jinja templates will also be pro-
       cessed to create or overwrite real files.  yadm will treat files ending
       in

         ##yadm.j2

       as  Jinja templates. During processing, the following variables are set
       according to the rules explained in the ALTERNATES section:

         YADM_CLASS
         YADM_OS
         YADM_HOSTNAME
         YADM_USER

       In addition YADM_DISTRO is exposed as the value of lsb_release  -si  if
       lsb_release is locally available.

       For example, a file named whatever##yadm.j2 with the following content

         {% if YADM_USER == 'harvey' -%}
         config={{YADM_CLASS}}-{{ YADM_OS }}
         {% else -%}
         config=dev-whatever
         {% endif -%}

       would  output  a  file named whatever with the following content if the
       user is "harvey":

         config=work-Linux

       and the following otherwise:

         config=dev-whatever

       See http://jinja.pocoo.org/ for an overview of Jinja.


## ENCRYPTION
       It can be useful to manage confidential files, like SSH  or  GPG  keys,
       across  multiple  systems.  However, doing so would put plain text data
       into a Git repository, which often resides on a  public  system.   yadm
       implements  a  feature  which can make it easy to encrypt and decrypt a
       set of files so the encrypted version can  be  maintained  in  the  Git
       repository.   This  feature  will  only  work  if the gpg(1) command is
       available.

       To use this feature, a list of patterns must be created  and  saved  as
       $HOME/.yadm/encrypt.   This  list of patterns should be relative to the
       configured work-tree (usually $HOME).  For example:

                  .ssh/*.key
                  .gnupg/*.gpg

       Standard filename expansions (*,  ?,  [)  are  supported.  Other  shell
       expansions  like brace and tilde are not supported. Spaces in paths are
       supported, and should not be quoted. If a directory is  specified,  its
       contents  will be included, but not recursively. Paths beginning with a
       "!" will be excluded.

       The yadm encrypt command will find all files matching the patterns, and
       prompt  for  a  password.  Once  a password has confirmed, the matching
       files will be encrypted and saved as $HOME/.yadm/files.gpg.   The  pat-
       terns  and files.gpg should be added to the yadm repository so they are
       available across multiple systems.

       To decrypt these files later, or on another system run yadm decrypt and
       provide  the  correct password.  After files are decrypted, permissions
       are automatically updated as described in the PERMISSIONS section.

       Symmetric encryption is used by default, but asymmetric encryption  may
       be enabled using the yadm.gpg-recipient configuration.

       NOTE:  It is recommended that you use a private repository when keeping
       confidential files, even though they are encrypted.

## PERMISSIONS
       When files are checked out of a Git repository, their  initial  permis-
       sions  are  dependent upon the user's umask. Because of this, yadm will
       automatically update the permissions of some file  paths.  The  "group"
       and "others" permissions will be removed from the following files:

       - $HOME/.yadm/files.gpg

       - All files matching patterns in $HOME/.yadm/encrypt

       - The SSH directory and files, .ssh/*

       - The GPG directory and files, .gnupg/*

       yadm will automatically update permissions by default. This can be dis-
       abled using the yadm.auto-perms configuration. Even if  disabled,  per-
       missions  can  be  manually  updated  by  running yadm perms.  The .ssh
       directory processing can be disabled using the yadm.ssh-perms  configu-
       ration.  The  .gnupg  directory  processing  can  be disabled using the
       yadm.gpg-perms configuration.

       When cloning a repo which includes data in a .ssh or .gnupg  directory,
       if  those  directories  do  not exist at the time of cloning, yadm will
       create the directories with mask 0700 prior to merging the fetched data
       into the work-tree.

       When running a Git command and .ssh or .gnupg directories do not exist,
       yadm will create those directories with mask 0700 prior to running  the
       Git  command.   This  can  be disabled using the yadm.auto-private-dirs
       configuration.

## HOOKS
       For every command yadm supports, a  program  can  be  provided  to  run
       before  or  after that command. These are referred to as "hooks".  yadm
       looks for hooks in the directory $HOME/.yadm/hooks.  Each hook is named
       using  a  prefix of pre_ or post_, followed by the command which should
       trigger the hook. For example, to create a  hook  which  is  run  after
       every  yadm  pull  command,  create a hook named post_pull.  Hooks must
       have the executable file permission set.

       If a pre_ hook is defined, and the hook terminates with a non-zero exit
       status,  yadm  will  refuse  to run the yadm command. For example, if a
       pre_commit hook is defined, but that command ends with a non-zero  exit
       status,  the  yadm commit will never be run. This allows one to "short-
       circuit" any operation using a pre_ hook.

       Hooks have the following environment variables  available  to  them  at
       runtime:

       YADM_HOOK_COMMAND
              The command which triggered the hook

       YADM_HOOK_EXIT
              The exit status of the yadm command

       YADM_HOOK_FULL_COMMAND
              The yadm command with all command line arguments

       YADM_HOOK_REPO
              The path to the yadm repository

       YADM_HOOK_WORK
              The path to the work-tree

## FILES
       The  following are the default paths yadm uses for its own data.  These
       paths can be altered using universal options.  See the OPTIONS  section
       for details.

       $HOME/.yadm
              The yadm directory. By default, all data yadm stores is relative
              to this directory.

       $YADM_DIR/config
              Configuration file for yadm.

       $YADM_DIR/repo.git
              Git repository used by yadm.

       $YADM_DIR/encrypt
              List of globs used for encrypt/decrypt

       $YADM_DIR/files.gpg
              All files encrypted with yadm encrypt are stored in this file.

## EXAMPLES
       yadm init
              Create an empty repo for managing files

       yadm add .bash_profile ; yadm commit
              Add .bash_profile to the Git index and create a new commit

       yadm remote add origin <url>
              Add a remote origin to an existing repository

       yadm push -u origin master
              Initial push of master to origin

       echo .ssh/*.key >> $HOME/.yadm/encrypt
              Add a new pattern to the list of encrypted files

       yadm encrypt ; yadm add ~/.yadm/files.gpg ; yadm commit
              Commit a new set of encrypted files

## REPORTING BUGS
       Report issues or create pull requests at GitHub:

       https://github.com/TheLocehiliosan/yadm/issues

## AUTHOR
       Tim Byrne <sultan@locehilios.com>

## SEE ALSO
       git(1), gpg(1)

       https://thelocehiliosan.github.io/yadm/



