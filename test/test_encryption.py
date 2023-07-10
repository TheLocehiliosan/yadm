"""Test encryption"""

import os
import shlex
import time

import pytest

KEY_FILE = "test/test_key"
KEY_FINGERPRINT = "F8BBFC746C58945442349BCEBA54FFD04C599B1A"
KEY_NAME = "yadm-test1"
KEY_TRUST = "test/ownertrust.txt"
PASSPHRASE = "ExamplePassword"

pytestmark = pytest.mark.usefixtures("config_git")


def add_asymmetric_key(runner, gnupg):
    """Add asymmetric key"""
    env = os.environ.copy()
    env["GNUPGHOME"] = gnupg.home
    runner(
        ["gpg", "--import", shlex.quote(KEY_FILE)],
        env=env,
        shell=True,
    )
    runner(
        ["gpg", "--import-ownertrust", "<", shlex.quote(KEY_TRUST)],
        env=env,
        shell=True,
    )


def remove_asymmetric_key(runner, gnupg):
    """Remove asymmetric key"""
    env = os.environ.copy()
    env["GNUPGHOME"] = gnupg.home
    runner(
        ["gpg", "--batch", "--yes", "--delete-secret-keys", shlex.quote(KEY_FINGERPRINT)],
        env=env,
        shell=True,
    )
    runner(
        ["gpg", "--batch", "--yes", "--delete-key", shlex.quote(KEY_FINGERPRINT)],
        env=env,
        shell=True,
    )


@pytest.fixture
def asymmetric_key(runner, gnupg):
    """Fixture for asymmetric key, removed in teardown"""
    add_asymmetric_key(runner, gnupg)
    yield KEY_NAME
    remove_asymmetric_key(runner, gnupg)


@pytest.fixture
def encrypt_targets(yadm_cmd, paths):
    """Fixture for setting up data to encrypt

    This fixture:
      * inits an empty repo
      * creates test files in the work tree
      * creates a ".yadm/encrypt" file for testing:
        * standard files
        * standard globs
        * directories
        * comments
        * empty lines and lines with just space
        * exclusions
      * returns a list of expected encrypted files
    """

    # init empty yadm repo
    os.system(" ".join(yadm_cmd("init", "-w", str(paths.work), "-f")))

    expected = []

    # standard files w/ dirs & spaces
    paths.work.join("inc file1").write("inc file1")
    expected.append("inc file1")
    paths.encrypt.write("inc file1\n")
    paths.work.join("inc dir").mkdir()
    paths.work.join("inc dir/inc file2").write("inc file2")
    expected.append("inc dir/inc file2")
    paths.encrypt.write("inc dir/inc file2\n", mode="a")

    # standard globs w/ dirs & spaces
    paths.work.join("globs file1").write("globs file1")
    expected.append("globs file1")
    paths.work.join("globs dir").mkdir()
    paths.work.join("globs dir/globs file2").write("globs file2")
    expected.append("globs dir/globs file2")
    paths.encrypt.write("globs*\n", mode="a")

    # blank lines
    paths.encrypt.write("\n        \n\t\n", mode="a")

    # comments
    paths.work.join("commentfile1").write("commentfile1")
    paths.encrypt.write("#commentfile1\n", mode="a")
    paths.encrypt.write("        #commentfile1\n", mode="a")

    # exclusions
    paths.work.join("extest").mkdir()
    paths.encrypt.write("extest/*\n", mode="a")  # include within extest
    paths.work.join("extest/inglob1").write("inglob1")
    paths.work.join("extest/exglob1").write("exglob1")
    paths.work.join("extest/exglob2").write("exglob2")
    paths.encrypt.write("!extest/ex*\n", mode="a")  # exclude the ex*
    expected.append("extest/inglob1")  # should be left with only in*

    return expected


@pytest.fixture(scope="session")
def decrypt_targets(tmpdir_factory, runner, gnupg):
    """Fixture for setting data to decrypt

    This fixture:
      * creates symmetric/asymmetric encrypted archives
      * creates a list of expected decrypted files
    """

    tmpdir = tmpdir_factory.mktemp("decrypt_targets")
    symmetric = tmpdir.join("symmetric.tar.gz.gpg")
    asymmetric = tmpdir.join("asymmetric.tar.gz.gpg")

    expected = []

    tmpdir.join("decrypt1").write("decrypt1")
    expected.append("decrypt1")
    tmpdir.join("decrypt2").write("decrypt2")
    expected.append("decrypt2")
    tmpdir.join("subdir").mkdir()
    tmpdir.join("subdir/decrypt3").write("subdir/decrypt3")
    expected.append("subdir/decrypt3")

    gnupg.pw(PASSPHRASE)
    env = os.environ.copy()
    env["GNUPGHOME"] = gnupg.home
    run = runner(
        ["tar", "cvf", "-"]
        + expected
        + ["|", "gpg", "--batch", "--yes", "-c"]
        + ["--output", shlex.quote(str(symmetric))],
        cwd=tmpdir,
        env=env,
        shell=True,
    )
    assert run.success

    gnupg.pw("")
    add_asymmetric_key(runner, gnupg)
    run = runner(
        ["tar", "cvf", "-"]
        + expected
        + ["|", "gpg", "--batch", "--yes", "-e"]
        + ["-r", shlex.quote(KEY_NAME)]
        + ["--output", shlex.quote(str(asymmetric))],
        cwd=tmpdir,
        env=env,
        shell=True,
    )
    assert run.success
    remove_asymmetric_key(runner, gnupg)

    return {
        "asymmetric": asymmetric,
        "expected": expected,
        "symmetric": symmetric,
    }


@pytest.mark.parametrize("bad_phrase", [False, True], ids=["good_phrase", "bad_phrase"])
@pytest.mark.parametrize("missing_encrypt", [False, True], ids=["encrypt_exists", "encrypt_missing"])
@pytest.mark.parametrize("overwrite", [False, True], ids=["clean", "overwrite"])
def test_symmetric_encrypt(runner, yadm_cmd, paths, encrypt_targets, gnupg, bad_phrase, overwrite, missing_encrypt):
    """Test symmetric encryption"""

    if missing_encrypt:
        paths.encrypt.remove()

    if bad_phrase:
        gnupg.pw("")
    else:
        gnupg.pw(PASSPHRASE)

    if overwrite:
        paths.archive.write("existing archive")

    env = os.environ.copy()
    env["GNUPGHOME"] = gnupg.home
    run = runner(yadm_cmd("encrypt"), env=env)

    if missing_encrypt or bad_phrase:
        assert run.failure
    else:
        assert run.success
        assert run.err == ""

    if missing_encrypt:
        assert "does not exist" in run.err
    elif bad_phrase:
        assert "Invalid IPC" in run.err
    else:
        assert encrypted_data_valid(runner, gnupg, paths.archive, encrypt_targets)


@pytest.mark.parametrize("bad_phrase", [False, True], ids=["good_phrase", "bad_phrase"])
@pytest.mark.parametrize("archive_exists", [True, False], ids=["archive_exists", "archive_missing"])
@pytest.mark.parametrize("dolist", [False, True], ids=["decrypt", "list"])
def test_symmetric_decrypt(runner, yadm_cmd, paths, decrypt_targets, gnupg, dolist, archive_exists, bad_phrase):
    """Test decryption"""

    # init empty yadm repo
    os.system(" ".join(yadm_cmd("init", "-w", str(paths.work), "-f")))

    if bad_phrase:
        gnupg.pw("")
        time.sleep(1)  # allow gpg-agent cache to expire
    else:
        gnupg.pw(PASSPHRASE)

    if archive_exists:
        decrypt_targets["symmetric"].copy(paths.archive)

    # to test overwriting
    paths.work.join("decrypt1").write("pre-existing file")

    env = os.environ.copy()
    env["GNUPGHOME"] = gnupg.home

    args = []

    if dolist:
        args.append("-l")
    run = runner(yadm_cmd("decrypt") + args, env=env)

    if archive_exists and not bad_phrase:
        assert run.success
        assert "encrypted with 1 passphrase" in run.err
        if dolist:
            for filename in decrypt_targets["expected"]:
                if filename != "decrypt1":  # this one should exist
                    assert not paths.work.join(filename).exists()
                assert filename in run.out
        else:
            for filename in decrypt_targets["expected"]:
                assert paths.work.join(filename).read() == filename
    else:
        assert run.failure


@pytest.mark.usefixtures("asymmetric_key")
@pytest.mark.parametrize("ask", [False, True], ids=["no_ask", "ask"])
@pytest.mark.parametrize("key_exists", [True, False], ids=["key_exists", "key_missing"])
@pytest.mark.parametrize("overwrite", [False, True], ids=["clean", "overwrite"])
def test_asymmetric_encrypt(runner, yadm_cmd, paths, encrypt_targets, gnupg, overwrite, key_exists, ask):
    """Test asymmetric encryption"""

    # specify encryption recipient
    if ask:
        os.system(" ".join(yadm_cmd("config", "yadm.gpg-recipient", "ASK")))
        expect = [("Enter the user ID", KEY_NAME), ("Enter the user ID", "")]
    else:
        os.system(" ".join(yadm_cmd("config", "yadm.gpg-recipient", KEY_NAME)))
        expect = []

    if overwrite:
        paths.archive.write("existing archive")

    if not key_exists:
        remove_asymmetric_key(runner, gnupg)

    env = os.environ.copy()
    env["GNUPGHOME"] = gnupg.home

    run = runner(yadm_cmd("encrypt"), env=env, expect=expect)

    if key_exists:
        assert run.success
        assert encrypted_data_valid(runner, gnupg, paths.archive, encrypt_targets)
    else:
        assert run.failure
        assert "Unable to write" in run.out if expect else run.err

    if ask:
        assert "Enter the user ID" in run.out


@pytest.mark.usefixtures("asymmetric_key")
@pytest.mark.usefixtures("encrypt_targets")
def test_multi_key(runner, yadm_cmd, gnupg):
    """Test multiple recipients"""

    # specify two encryption recipient
    os.system(" ".join(yadm_cmd("config", "yadm.gpg-recipient", f'"second-key {KEY_NAME}"')))

    env = os.environ.copy()
    env["GNUPGHOME"] = gnupg.home

    run = runner(yadm_cmd("encrypt"), env=env)

    assert run.failure
    assert "second-key: skipped: No public key" in run.err


@pytest.mark.usefixtures("asymmetric_key")
@pytest.mark.parametrize("key_exists", [True, False], ids=["key_exists", "key_missing"])
@pytest.mark.parametrize("dolist", [False, True], ids=["decrypt", "list"])
def test_asymmetric_decrypt(runner, yadm_cmd, paths, decrypt_targets, gnupg, dolist, key_exists):
    """Test decryption"""

    # init empty yadm repo
    os.system(" ".join(yadm_cmd("init", "-w", str(paths.work), "-f")))

    decrypt_targets["asymmetric"].copy(paths.archive)

    # to test overwriting
    paths.work.join("decrypt1").write("pre-existing file")

    if not key_exists:
        remove_asymmetric_key(runner, gnupg)

    args = []

    if dolist:
        args.append("-l")
    env = os.environ.copy()
    env["GNUPGHOME"] = gnupg.home
    run = runner(yadm_cmd("decrypt") + args, env=env)

    if key_exists:
        assert run.success
        if dolist:
            for filename in decrypt_targets["expected"]:
                if filename != "decrypt1":  # this one should exist
                    assert not paths.work.join(filename).exists()
                assert filename in run.out
        else:
            for filename in decrypt_targets["expected"]:
                assert paths.work.join(filename).read() == filename
    else:
        assert run.failure
        assert "Unable to extract encrypted files" in run.err


@pytest.mark.parametrize("untracked", [False, "y", "n"], ids=["tracked", "untracked_answer_y", "untracked_answer_n"])
def test_offer_to_add(runner, yadm_cmd, paths, encrypt_targets, gnupg, untracked):
    """Test offer to add encrypted archive

    All the other encryption tests use an archive outside of the work tree.
    However, the archive is often inside the work tree, and if it is, there
    should be an offer to add it to the repo if it is not tracked.
    """

    worktree_archive = paths.work.join("worktree-archive.tar.gpg")

    expect = []

    gnupg.pw(PASSPHRASE)
    env = os.environ.copy()
    env["GNUPGHOME"] = gnupg.home

    if untracked:
        expect.append(("add it now", untracked))
    else:
        worktree_archive.write("exists")
        os.system(" ".join(yadm_cmd("add", str(worktree_archive))))

    run = runner(yadm_cmd("encrypt", "--yadm-archive", str(worktree_archive)), env=env, expect=expect)

    assert run.success
    assert run.err == ""
    assert encrypted_data_valid(runner, gnupg, worktree_archive, encrypt_targets)

    run = runner(yadm_cmd("status", "--porcelain", "-uall", str(worktree_archive)))
    assert run.success
    assert run.err == ""

    if untracked == "y":
        # should be added to the index
        assert f"A  {worktree_archive.basename}" in run.out
    elif untracked == "n":
        # should NOT be added to the index
        assert f"?? {worktree_archive.basename}" in run.out
    else:
        # should appear modified in the index
        assert f"AM {worktree_archive.basename}" in run.out


@pytest.mark.usefixtures("ds1_copy")
def test_encrypt_added_to_exclude(runner, yadm_cmd, paths, gnupg):
    """Confirm that .config/yadm/encrypt is added to exclude"""

    gnupg.pw(PASSPHRASE)
    env = os.environ.copy()
    env["GNUPGHOME"] = gnupg.home

    exclude_file = paths.repo.join("info/exclude")
    paths.encrypt.write("test-encrypt-data\n")
    paths.work.join("test-encrypt-data").write("")
    exclude_file.write("original-data", ensure=True)

    run = runner(yadm_cmd("encrypt"), env=env)

    assert "test-encrypt-data" in paths.repo.join("info/exclude").read()
    assert "original-data" in paths.repo.join("info/exclude").read()
    assert run.success
    assert run.err == ""


def encrypted_data_valid(runner, gnupg, encrypted, expected):
    """Verify encrypted data matches expectations"""
    gnupg.pw(PASSPHRASE)
    env = os.environ.copy()
    env["GNUPGHOME"] = gnupg.home
    run = runner(
        ["gpg", "-d", shlex.quote(str(encrypted)), "2>/dev/null", "|", "tar", "t"], env=env, shell=True, report=False
    )
    file_count = 0
    for filename in run.out.splitlines():
        if filename.endswith("/"):
            continue
        file_count += 1
        assert filename in expected, f"Unexpected file in archive: {filename}"
    assert file_count == len(expected), "Number of files in archive does not match expected"
    return True
