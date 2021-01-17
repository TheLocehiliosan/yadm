"""Unit tests: score_file"""
import pytest

CONDITION = {
    'default': {
        'labels': ['default'],
        'modifier': 0,
        },
    'arch': {
        'labels': ['a', 'arch', 'architecture'],
        'modifier': 1,
        },
    'os': {
        'labels': ['o', 'os'],
        'modifier': 2,
        },
    'distro': {
        'labels': ['d', 'distro'],
        'modifier': 4,
        },
    'class': {
        'labels': ['c', 'class'],
        'modifier': 8,
        },
    'hostname': {
        'labels': ['h', 'hostname'],
        'modifier': 16,
        },
    'user': {
        'labels': ['u', 'user'],
        'modifier': 32,
        },
    }
TEMPLATE_LABELS = ['t', 'template', 'yadm']


def calculate_score(filename):
    """Calculate the expected score"""
    # pylint: disable=too-many-branches
    score = 0

    _, conditions = filename.split('##', 1)

    for condition in conditions.split(','):
        label = condition
        value = None
        if '.' in condition:
            label, value = condition.split('.', 1)
        if label in CONDITION['default']['labels']:
            score += 1000
        elif label in CONDITION['arch']['labels']:
            if value == 'testarch':
                score += 1000 + CONDITION['arch']['modifier']
            else:
                score = 0
                break
        elif label in CONDITION['os']['labels']:
            if value == 'testos':
                score += 1000 + CONDITION['os']['modifier']
            else:
                score = 0
                break
        elif label in CONDITION['distro']['labels']:
            if value == 'testdistro':
                score += 1000 + CONDITION['distro']['modifier']
            else:
                score = 0
                break
        elif label in CONDITION['class']['labels']:
            if value == 'testclass':
                score += 1000 + CONDITION['class']['modifier']
            else:
                score = 0
                break
        elif label in CONDITION['hostname']['labels']:
            if value == 'testhost':
                score += 1000 + CONDITION['hostname']['modifier']
            else:
                score = 0
                break
        elif label in CONDITION['user']['labels']:
            if value == 'testuser':
                score += 1000 + CONDITION['user']['modifier']
            else:
                score = 0
                break
        elif label in TEMPLATE_LABELS:
            score = 0
            break
    return score


@pytest.mark.parametrize(
    'default', ['default', None], ids=['default', 'no-default'])
@pytest.mark.parametrize(
    'arch', ['arch', None], ids=['arch', 'no-arch'])
@pytest.mark.parametrize(
    'system', ['os', None], ids=['os', 'no-os'])
@pytest.mark.parametrize(
    'distro', ['distro', None], ids=['distro', 'no-distro'])
@pytest.mark.parametrize(
    'cla', ['class', None], ids=['class', 'no-class'])
@pytest.mark.parametrize(
    'host', ['hostname', None], ids=['hostname', 'no-host'])
@pytest.mark.parametrize(
    'user', ['user', None], ids=['user', 'no-user'])
def test_score_values(
        runner, yadm, default, arch, system, distro, cla, host, user):
    """Test score results"""
    # pylint: disable=too-many-branches
    local_class = 'testclass'
    local_arch = 'testarch'
    local_os = 'testos'
    local_distro = 'testdistro'
    local_hostname = 'testhost'
    local_user = 'testuser'
    filenames = {'filename##': 0}

    if default:
        for filename in list(filenames):
            for label in CONDITION[default]['labels']:
                newfile = filename
                if not newfile.endswith('##'):
                    newfile += ','
                newfile += label
                filenames[newfile] = calculate_score(newfile)
    if arch:
        for filename in list(filenames):
            for match in [True, False]:
                for label in CONDITION[arch]['labels']:
                    newfile = filename
                    if not newfile.endswith('##'):
                        newfile += ','
                    newfile += '.'.join([
                        label,
                        local_arch if match else 'badarch'
                        ])
                    filenames[newfile] = calculate_score(newfile)
    if system:
        for filename in list(filenames):
            for match in [True, False]:
                for label in CONDITION[system]['labels']:
                    newfile = filename
                    if not newfile.endswith('##'):
                        newfile += ','
                    newfile += '.'.join([
                        label,
                        local_os if match else 'bados'
                        ])
                    filenames[newfile] = calculate_score(newfile)
    if distro:
        for filename in list(filenames):
            for match in [True, False]:
                for label in CONDITION[distro]['labels']:
                    newfile = filename
                    if not newfile.endswith('##'):
                        newfile += ','
                    newfile += '.'.join([
                        label,
                        local_distro if match else 'baddistro'
                        ])
                    filenames[newfile] = calculate_score(newfile)
    if cla:
        for filename in list(filenames):
            for match in [True, False]:
                for label in CONDITION[cla]['labels']:
                    newfile = filename
                    if not newfile.endswith('##'):
                        newfile += ','
                    newfile += '.'.join([
                        label,
                        local_class if match else 'badclass'
                        ])
                    filenames[newfile] = calculate_score(newfile)
    if host:
        for filename in list(filenames):
            for match in [True, False]:
                for label in CONDITION[host]['labels']:
                    newfile = filename
                    if not newfile.endswith('##'):
                        newfile += ','
                    newfile += '.'.join([
                        label,
                        local_hostname if match else 'badhost'
                        ])
                    filenames[newfile] = calculate_score(newfile)
    if user:
        for filename in list(filenames):
            for match in [True, False]:
                for label in CONDITION[user]['labels']:
                    newfile = filename
                    if not newfile.endswith('##'):
                        newfile += ','
                    newfile += '.'.join([
                        label,
                        local_user if match else 'baduser'
                        ])
                    filenames[newfile] = calculate_score(newfile)

    script = f"""
        YADM_TEST=1 source {yadm}
        score=0
        YADM_CLASS={local_class}
        YADM_ARCH={local_arch}
        YADM_OS={local_os}
        YADM_DISTRO={local_distro}
        YADM_HOSTNAME={local_hostname}
        YADM_USER={local_user}
    """
    expected = ''
    for filename in filenames:
        script += f"""
            score_file "{filename}"
            echo "{filename}"
            echo "$score"
        """
        expected += filename + '\n'
        expected += str(filenames[filename]) + '\n'
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert run.out == expected


@pytest.mark.parametrize('ext', [None, 'e', 'extension'])
def test_extensions(runner, yadm, ext):
    """Verify extensions do not effect scores"""
    local_user = 'testuser'
    filename = f'filename##u.{local_user}'
    if ext:
        filename += f',{ext}.xyz'
    expected = ''
    script = f"""
        YADM_TEST=1 source {yadm}
        score=0
        YADM_USER={local_user}
        score_file "{filename}"
        echo "$score"
    """
    expected = f'{1000 + CONDITION["user"]["modifier"]}\n'
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert run.out == expected


def test_score_values_templates(runner, yadm):
    """Test score results"""
    local_class = 'testclass'
    local_arch = 'arch'
    local_os = 'testos'
    local_distro = 'testdistro'
    local_hostname = 'testhost'
    local_user = 'testuser'
    filenames = {'filename##': 0}

    for filename in list(filenames):
        for label in TEMPLATE_LABELS:
            newfile = filename
            if not newfile.endswith('##'):
                newfile += ','
            newfile += '.'.join([label, 'testtemplate'])
            filenames[newfile] = calculate_score(newfile)

    script = f"""
        YADM_TEST=1 source {yadm}
        score=0
        YADM_CLASS={local_class}
        YADM_ARCH={local_arch}
        YADM_OS={local_os}
        YADM_DISTRO={local_distro}
        YADM_HOSTNAME={local_hostname}
        YADM_USER={local_user}
    """
    expected = ''
    for filename in filenames:
        script += f"""
            score_file "{filename}"
            echo "{filename}"
            echo "$score"
        """
        expected += filename + '\n'
        expected += str(filenames[filename]) + '\n'
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert run.out == expected


@pytest.mark.parametrize(
    'cmd_generated',
    [True, False],
    ids=['supported-template', 'unsupported-template'])
def test_template_recording(runner, yadm, cmd_generated):
    """Template should be recorded if choose_template_cmd outputs a command"""

    mock = 'function choose_template_cmd() { return; }'
    expected = ''
    if cmd_generated:
        mock = 'function choose_template_cmd() { echo "test_cmd"; }'
        expected = 'template recorded'

    script = f"""
        YADM_TEST=1 source {yadm}
        function record_template() {{ echo "template recorded"; }}
        {mock}
        score_file "testfile##template.kind"
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert run.out.rstrip() == expected
