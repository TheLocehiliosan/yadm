


## NAME
       yadm - Yet Another Dotfiles Manager

## SYNOPSIS
       yadm command [options]

       yadm git-command-or-alias [options]

       yadm init [-f]

       yadm clone url [-f] [-w directory]

       yadm config name [value]

       yadm config [-e]

       yadm list [-a]

       yadm encrypt

       yadm decrypt [-l]

       yadm alt

       yadm perms

## DESCRIPTION
       yadm  is a tool for managing a collection of files across multiple com-
       puters, using a shared Git repository.  In addition,  yadm  provides  a
       feature  to  select  alternate versions of files based on the operation
       system or host name.  Lastly, yadm supplies the  ability  to  manage  a
       subset of secure files, which are encrypted before they are included in
       the repository.

## COMMANDS
       git-command or git-alias
              Any command not internally handled by yadm is passed through  to
              git(1).   Git commands or aliases are invoked with the yadm man-
              aged repository.  The working directory for git commands will be
              the configured work-tree (usually $HOME).

              Dotfiles  are  managed by using standard git commands; add, com-
              mit, push, pull, etc.

              The config command is not passed directly through.  Instead  use
              the gitconfig command (see below).

       alt    Create  symbolic links for any managed files matching the naming
              rules describe in the ALTERNATES section.  It is usually  unnec-
              essary  to  run  this  command,  as yadm automatically processes
              alternates by default.  This automatic behavior can be  disabled
              by setting the configuration yadm.auto-alt to "false".

       clone url
              Clone a remote repository for tracking dotfiles.  After the con-
              tents of the remote repository have been fetched, a  "merge"  of
              origin/master  is  attempted.   If  there  are conflicting files
              already present in the  work-tree,  this  merge  will  fail  and
              instead  a  "reset"  of origin/master will be done.  It is up to
              the user to resolve these conflicts, but if the  desired  action
              is to have the contents in the repository overwrite the existing
              files, then a "hard reset" should accomplish that:

                     yadm reset --hard origin/master

              The repository is stored in $HOME/.yadm/repo.git.   By  default,
              $HOME  will be used as the work-tree, but this can be overridden
              with the -w option.  yadm can be forced to overwrite an existing
              repository by providing the -f option.

       config This  command  manages  configurations  for  yadm.  This command
              works exactly they way git-config(1) does.  See  the  CONFIGURA-
              TION section for more details.

       decrypt
              Decrypt   all  files  stored  in  $HOME/.yadm/files.gpg.   Files
              decrypted will be relative to the configured work-tree  (usually
              $HOME).   Using the -l option will list the files stored without
              extracting them.

       encrypt
              Encrypt   all   files   matching   the   patterns    found    in
              $HOME/.yadm/encrypt.    See  the  ENCRYPTION  section  for  more
              details.

       gitconfig
              Pass options to the git config command. Since yadm already  uses
              the  config  command to manage its own configurations, this com-
              mand is provided as a way to change configurations of the repos-
              itory  managed  by  yadm.  One useful case might be to configure
              the repository so untracked files are shown in status  commands.
              yadm initially configures its repository so that untracked files
              are not shown.  If you wish use the  default  git  behavior  (to
              show  untracked files and directories), you can remove this con-
              figuration.

                     yadm gitconfig --unset status.showUntrackedFiles

       help   Print a summary of yadm commands.

       init   Initialize a new, empty repository for tracking  dotfiles.   The
              repository is stored in $HOME/.yadm/repo.git.  By default, $HOME
              will be used as the work-tree, but this can be  overridden  with
              the  -w  option.   yadm  can  be forced to overwrite an existing
              repository by providing the -f option.

       list   Print a list of files managed by yadm.  The -a option will cause
              all  managed  files to be listed.  Otherwise, the list will only
              include files from the current directory or below.

       perms  Update permissions as described in the PERMISSIONS section.   It
              is  usually  unnecessary  to run this command, as yadm automati-
              cally processes permissions by default.  This automatic behavior
              can  be disabled by setting the configuration yadm.auto-perms to
              "false".

       version
              Print the version of yadm.

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

       yadm.ssh-perms
              Disable the permission changes to $HOME/.ssh/*.  This feature is
              enabled by default.

       yadm.gpg-perms
              Disable the permission changes to $HOME/.gnupg/*.  This  feature
              is enabled by default.

## ALTERNATES
       When managing a set of files across different systems, it can be useful
       to have an automated way of choosing an alternate version of a file for
       a  different  operation  system  or  simply for a different host.  yadm
       implements a feature which will automatically create a symbolic link to
       the  appropriate  version  of  a file, as long as you follow a specific
       naming convention.  yadm can detect files with names ending in:

              ##OS.HOSTNAME or ##OS or ##

       If there are any files managed by yadm's repository  which  match  this
       naming  convention,  symbolic links will be created for the most appro-
       priate version.  This may best be demonstrated by example.  Assume  the
       following files are managed by yadm's repository:

         - $HOME/path/example.txt##
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

       Since  the  hostname  doesn't  match any of the managed files, the more
       generic version is chosen.

       If running on a Linux server named "host4", the link will be:

       $HOME/path/example.txt -> $HOME/path/example.txt##Linux

       If running on a Solaris server, the link use the default "##" version:

       $HOME/path/example.txt -> $HOME/path/example.txt##

       If no "##" version exists and no files match the current  OS  or  HOST-
       NAME, then no link will be created.

       OS  is  determined  by  running uname -s, and HOSTNAME by running host-
       name -s.  yadm will automatically create these links by  default.  This
       can  be  disabled  using the yadm.auto-alt configuration.  Even if dis-
       abled, links can be manually created by running yadm alt.

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

       The yadm encrypt command will find all files matching the patterns, and
       prompt  for  a  password.  Once  a password has confirmed, the matching
       files will be encrypted and saved as $HOME/.yadm/files.gpg.   The  pat-
       terns  and files.gpg should be added to the yadm repository so they are
       available across multiple systems.

       To decrypt these files later, or on another system run yadm decrypt and
       provide  the  correct password.  After files are decrypted, permissions
       are automatically updated as described in the PERMISSIONS section.

       NOTE: It is recommended that you use a private repository when  keeping
       confidential files, even though they are encrypted.

## PERMISSIONS
       When  files  are checked out of a Git repository, their initial permis-
       sions are dependent upon the user's umask. This can result in confiden-
       tial files with lax permissions.

       To prevent this, yadm will automatically update the permissions of con-
       fidential files.  The "group" and "others" permissions will be  removed
       from the following files:

       - $HOME/.yadm/files.gpg

       - All files matching patterns in $HOME/.yadm/encrypt

       - The SSH directory and files, .ssh/*

       - The GPG directory and files, .gnupg/*

       yadm will automatically update permissions by default. This can be dis-
       abled using the yadm.auto-perms configuration.  Even if disabled,  per-
       missions can be manually updated by running yadm perms.  The SSH direc-
       tory processing can be disabled using the yadm.ssh-perms configuration.

## FILES
       $HOME/.yadm/config
              Configuration file for yadm.

       $HOME/.yadm/repo.git
              Git repository used by yadm.

       $HOME/.yadm/encrypt
              List of globs used for encrypt/decrypt

       $HOME/.yadm/files.gpg
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

       https://github.com/TheLocehiliosan/yadm

## AUTHOR
       Tim Byrne <sultan@locehilios.com>

## SEE ALSO
       git(1), gpg(1)

       Other management tools which inspired the creation of yadm:

       homeshick <https://github.com/andsens/homeshick>

       vcsh <https://github.com/RichiH/vcsh>



