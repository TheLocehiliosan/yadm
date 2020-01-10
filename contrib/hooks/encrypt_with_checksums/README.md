## Track checksums of encrypted files

Contributed by Martin Zuther

Hook         | Description
----         | -----------
post_encrypt | Collects the checksums of encrypted files, and stores them in .config/yadm/files.checksums
post_list    | Prints the names of encrypted files
post_status  | Reports untracked changes within encrypted files
