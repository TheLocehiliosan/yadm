"""Unit tests: private_dirs"""
import pytest


@pytest.mark.parametrize(
    'gnupghome',
    [True, False],
    ids=['gnupghome-set', 'gnupghome-unset'],
)
@pytest.mark.parametrize('param', ['all', 'gnupg'])
def test_relative_path(runner, paths, gnupghome, param):
    """Test translate_to_relative"""

    alt_gnupghome = 'alt/gnupghome'
    env_gnupghome = paths.work.join(alt_gnupghome)

    script = f"""
        YADM_TEST=1 source {paths.pgm}
        YADM_WORK={paths.work}
        private_dirs {param}
    """

    env = {}
    if gnupghome:
        env['GNUPGHOME'] = env_gnupghome

    expected = alt_gnupghome if gnupghome else '.gnupg'
    if param == 'all':
        expected = f'.ssh {expected}'

    run = runner(command=['bash'], inp=script, env=env)
    assert run.success
    assert run.err == ''
    assert run.out.strip() == expected
