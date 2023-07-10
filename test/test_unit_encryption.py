"""Unit tests: encryption functions"""

import pytest


@pytest.mark.parametrize("condition", ["default", "override"])
def test_get_cipher(runner, paths, condition):
    """Test _get_cipher()"""

    if condition == "override":
        paths.config.write("[yadm]\n\tcipher = override-cipher")

    script = f"""
        YADM_TEST=1 source {paths.pgm}
        YADM_DIR="{paths.yadm}"
        set_yadm_dirs
        configure_paths
        _get_cipher test-archive
        echo "output_archive:$output_archive"
        echo "yadm_cipher:$yadm_cipher"
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    assert "output_archive:test-archive" in run.out
    if condition == "override":
        assert "yadm_cipher:override-cipher" in run.out
    else:
        assert "yadm_cipher:gpg" in run.out


@pytest.mark.parametrize("cipher", ["gpg", "openssl", "bad"])
@pytest.mark.parametrize("mode", ["_encrypt_to", "_decrypt_from"])
def test_encrypt_decrypt(runner, paths, cipher, mode):
    """Test _encrypt_to() & _decrypt_from"""

    script = f"""
        YADM_TEST=1 source {paths.pgm}
        YADM_DIR="{paths.yadm}"
        set_yadm_dirs
        configure_paths
        function mock_openssl() {{ echo openssl $*; }}
        function mock_gpg() {{ echo gpg $*; }}
        function _get_cipher() {{
            output_archive="$1"
            yadm_cipher="{cipher}"
        }}
        OPENSSL_PROGRAM=mock_openssl
        GPG_PROGRAM=mock_gpg
        {mode} {paths.archive}
    """
    run = runner(command=["bash"], inp=script)

    if cipher != "bad":
        assert run.success
        assert run.out.startswith(cipher)
        assert str(paths.archive) in run.out
        assert run.err == ""
    else:
        assert run.failure
        assert "Unknown cipher" in run.err


@pytest.mark.parametrize("condition", ["default", "override"])
def test_get_openssl_ciphername(runner, paths, condition):
    """Test _get_openssl_ciphername()"""

    if condition == "override":
        paths.config.write("[yadm]\n\topenssl-ciphername = override-cipher")

    script = f"""
        YADM_TEST=1 source {paths.pgm}
        YADM_DIR="{paths.yadm}"
        set_yadm_dirs
        configure_paths
        result=$(_get_openssl_ciphername)
        echo "result:$result"
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    if condition == "override":
        assert run.out.strip() == "result:override-cipher"
    else:
        assert run.out.strip() == "result:aes-256-cbc"


@pytest.mark.parametrize("condition", ["old", "not-old"])
def test_set_openssl_options(runner, paths, condition):
    """Test _set_openssl_options()"""

    if condition == "old":
        paths.config.write("[yadm]\n\topenssl-old = true")

    script = f"""
        YADM_TEST=1 source {paths.pgm}
        YADM_DIR="{paths.yadm}"
        set_yadm_dirs
        configure_paths
        function _get_openssl_ciphername() {{ echo "testcipher"; }}
        _set_openssl_options
        echo "result:${{OPENSSL_OPTS[@]}}"
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    if condition == "old":
        assert "-testcipher -salt -md md5" in run.out
    else:
        assert "-testcipher -salt -pbkdf2 -iter 100000 -md sha512" in run.out


@pytest.mark.parametrize("recipient", ["ASK", "present", ""])
def test_set_gpg_options(runner, paths, recipient):
    """Test _set_gpg_options()"""

    paths.config.write(f"[yadm]\n\tgpg-recipient = {recipient}")

    script = f"""
        YADM_TEST=1 source {paths.pgm}
        YADM_DIR="{paths.yadm}"
        set_yadm_dirs
        configure_paths
        _set_gpg_options
        echo "result:${{GPG_OPTS[@]}}"
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    if recipient == "ASK":
        assert run.out.strip() == "result:--no-default-recipient -e"
    elif recipient != "":
        assert run.out.strip() == f"result:-e -r {recipient}"
    else:
        assert run.out.strip() == "result:-c"
