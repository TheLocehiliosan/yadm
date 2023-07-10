"""Unit tests: remove_stale_links"""
import os

import pytest


@pytest.mark.parametrize("linked", [True, False])
@pytest.mark.parametrize("kind", ["file", "symlink"])
def test_remove_stale_links(runner, yadm, tmpdir, kind, linked):
    """Test remove_stale_links()"""

    source_file = tmpdir.join("source_file")
    source_file.write("source file", ensure=True)
    link = tmpdir.join("link")

    if kind == "file":
        link.write("link file", ensure=True)
    else:
        os.system(f"ln -s {source_file} {link}")

    alt_linked = ""
    if linked:
        alt_linked = source_file

    script = f"""
        YADM_TEST=1 source {yadm}
        possible_alts=({link})
        alt_linked=({alt_linked})
        function rm() {{ echo rm "$@"; }}
        remove_stale_links
    """

    run = runner(command=["bash"], inp=script)
    assert run.err == ""
    if kind == "symlink" and not linked:
        assert f"rm -f {link}" in run.out
    else:
        assert run.out == ""
