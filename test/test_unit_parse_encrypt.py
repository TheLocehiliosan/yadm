"""Unit tests: parse_encrypt"""

import pytest


def test_not_called(runner, paths):
    """Test parse_encrypt (not called)"""
    run = run_parse_encrypt(runner, paths, skip_parse=True)
    assert run.success
    assert run.err == ''
    assert 'EIF:unparsed' in run.out, 'EIF should be unparsed'
    assert 'EIF_COUNT:1' in run.out, 'Only value of EIF should be unparsed'


def test_short_circuit(runner, paths):
    """Test parse_encrypt (short-circuit)"""
    run = run_parse_encrypt(runner, paths, twice=True)
    assert run.success
    assert run.err == ''
    assert 'PARSE_ENCRYPT_SHORT=parse_encrypt() not reprocessed' in run.out, (
        'parse_encrypt() should short-circuit')


@pytest.mark.parametrize(
    'encrypt', [
        ('missing'),
        ('empty'),
    ])
def test_empty(runner, paths, encrypt):
    """Test parse_encrypt (file missing/empty)"""

    # write encrypt file
    if encrypt == 'missing':
        assert not paths.encrypt.exists(), 'Encrypt should be missing'
    else:
        paths.encrypt.write('')
        assert paths.encrypt.exists(), 'Encrypt should exist'
        assert paths.encrypt.size() == 0, 'Encrypt should be empty'

    # run parse_encrypt
    run = run_parse_encrypt(runner, paths)
    assert run.success
    assert run.err == ''

    # validate parsing result
    assert 'EIF_COUNT:0' in run.out, 'EIF should be empty'


@pytest.mark.usefixtures('ds1_repo_copy')
def test_file_parse_encrypt(runner, paths):
    """Test parse_encrypt

    Test an array of supported features of the encrypt configuration.
    """

    edata = ''
    expected = set()

    # empty line
    edata += '\n'

    # simple comments
    edata += '# a simple comment\n'
    edata += '    # a comment with leading space\n'

    # unreferenced directory
    paths.work.join('unreferenced').mkdir()

    # simple files
    edata += 'simple_file\n'
    edata += 'simple.file\n'
    paths.work.join('simple_file').write('')
    paths.work.join('simple.file').write('')
    paths.work.join('simple_file2').write('')
    paths.work.join('simple.file2').write('')
    expected.add('simple_file')
    expected.add('simple.file')

    # simple files in directories
    edata += 'simple_dir/simple_file\n'
    paths.work.join('simple_dir/simple_file').write('', ensure=True)
    paths.work.join('simple_dir/simple_file2').write('', ensure=True)
    expected.add('simple_dir/simple_file')

    # paths with spaces
    edata += 'with space/with space\n'
    paths.work.join('with space/with space').write('', ensure=True)
    paths.work.join('with space/with space2').write('', ensure=True)
    expected.add('with space/with space')

    # hidden files
    edata += '.hidden\n'
    paths.work.join('.hidden').write('')
    expected.add('.hidden')

    # hidden files in directories
    edata += '.hidden_dir/.hidden_file\n'
    paths.work.join('.hidden_dir/.hidden_file').write('', ensure=True)
    expected.add('.hidden_dir/.hidden_file')

    # wildcards
    edata += 'wild*\n'
    paths.work.join('wildcard1').write('', ensure=True)
    paths.work.join('wildcard2').write('', ensure=True)
    expected.add('wildcard1')
    expected.add('wildcard2')

    edata += 'dirwild*\n'
    paths.work.join('dirwildcard/file1').write('', ensure=True)
    paths.work.join('dirwildcard/file2').write('', ensure=True)
    expected.add('dirwildcard')

    # excludes
    edata += 'exclude*\n'
    edata += 'ex ex/*\n'
    paths.work.join('exclude_file1').write('')
    paths.work.join('exclude_file2.ex').write('')
    paths.work.join('exclude_file3.ex3').write('')
    expected.add('exclude_file1')
    expected.add('exclude_file3.ex3')
    edata += '!*.ex\n'
    edata += '!ex ex/*.txt\n'
    paths.work.join('ex ex/file4').write('', ensure=True)
    paths.work.join('ex ex/file5.txt').write('', ensure=True)
    paths.work.join('ex ex/file6.text').write('', ensure=True)
    expected.add('ex ex/file4')
    expected.add('ex ex/file6.text')

    # write encrypt file
    print(f'ENCRYPT:\n---\n{edata}---\n')
    paths.encrypt.write(edata)
    assert paths.encrypt.isfile()

    # run parse_encrypt
    run = run_parse_encrypt(runner, paths)
    assert run.success
    assert run.err == ''

    assert f'EIF_COUNT:{len(expected)}' in run.out, 'EIF count wrong'
    for expected_file in expected:
        assert f'EIF:{expected_file}\n' in run.out


def run_parse_encrypt(
        runner, paths,
        skip_parse=False,
        twice=False):
    """Run parse_encrypt

    A count of ENCRYPT_INCLUDE_FILES will be reported as EIF_COUNT:X. All
    values of ENCRYPT_INCLUDE_FILES will be reported as individual EIF:value
    lines.
    """
    parse_cmd = 'parse_encrypt'
    if skip_parse:
        parse_cmd = ''
    if twice:
        parse_cmd = 'parse_encrypt; parse_encrypt'
    script = f"""
        YADM_TEST=1 source {paths.pgm}
        YADM_ENCRYPT={paths.encrypt}
        export YADM_ENCRYPT
        GIT_DIR={paths.repo}
        export GIT_DIR
        {parse_cmd}
        export ENCRYPT_INCLUDE_FILES
        export PARSE_ENCRYPT_SHORT
        env
        echo EIF_COUNT:${{#ENCRYPT_INCLUDE_FILES[@]}}
        for value in "${{ENCRYPT_INCLUDE_FILES[@]}}"; do
            echo "EIF:$value"
        done
    """
    run = runner(command=['bash'], inp=script)
    return run
