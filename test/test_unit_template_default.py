"""Unit tests: template_default"""
import os

FILE_MODE = 0o754

# these values are also testing the handling of bizarre characters
LOCAL_CLASS = "default_Test+@-!^Class"
LOCAL_ARCH = "default_Test+@-!^Arch"
LOCAL_OS = "default_Test+@-!^System"
LOCAL_HOSTNAME = "default_Test+@-!^Host"
LOCAL_USER = "default_Test+@-!^User"
LOCAL_DISTRO = "default_Test+@-!^Distro"
TEMPLATE = f'''
start of template
default class  = >{{{{yadm.class}}}}<
default arch   = >{{{{yadm.arch}}}}<
default os     = >{{{{yadm.os}}}}<
default host   = >{{{{yadm.hostname}}}}<
default user   = >{{{{yadm.user}}}}<
default distro = >{{{{yadm.distro}}}}<
{{% if yadm.class == "else1" %}}
wrong else 1
{{% else %}}
Included section from else
{{% endif %}}
{{% if yadm.class == "wrongclass1" %}}
wrong class 1
{{% endif %}}
{{% if yadm.class == "{LOCAL_CLASS}" %}}
Included section for class = {{{{yadm.class}}}} ({{{{yadm.class}}}} repeated)
Multiple lines
{{% else %}}
Should not be included...
{{% endif %}}
{{% if yadm.class == "wrongclass2" %}}
wrong class 2
{{% endif %}}
{{% if yadm.arch == "wrongarch1" %}}
wrong arch 1
{{% endif %}}
{{% if yadm.arch == "{LOCAL_ARCH}" %}}
Included section for arch = {{{{yadm.arch}}}} ({{{{yadm.arch}}}} repeated)
{{% endif %}}
{{% if yadm.arch == "wrongarch2" %}}
wrong arch 2
{{% endif %}}
{{% if yadm.os == "wrongos1" %}}
wrong os 1
{{% endif %}}
{{% if yadm.os == "{LOCAL_OS}" %}}
Included section for os = {{{{yadm.os}}}} ({{{{yadm.os}}}} repeated)
{{% endif %}}
{{% if yadm.os == "wrongos2" %}}
wrong os 2
{{% endif %}}
{{% if yadm.hostname == "wronghost1" %}}
wrong host 1
{{% endif %}}
{{% if yadm.hostname == "{LOCAL_HOSTNAME}" %}}
Included section for host = {{{{yadm.hostname}}}} ({{{{yadm.hostname}}}} again)
{{% endif %}}
{{% if yadm.hostname == "wronghost2" %}}
wrong host 2
{{% endif %}}
{{% if yadm.user == "wronguser1" %}}
wrong user 1
{{% endif %}}
{{% if yadm.user == "{LOCAL_USER}" %}}
Included section for user = {{{{yadm.user}}}} ({{{{yadm.user}}}} repeated)
{{% endif %}}
{{% if yadm.user == "wronguser2" %}}
wrong user 2
{{% endif %}}
{{% if yadm.distro == "wrongdistro1" %}}
wrong distro 1
{{% endif %}}
{{% if yadm.distro == "{LOCAL_DISTRO}" %}}
Included section for distro = {{{{yadm.distro}}}} ({{{{yadm.distro}}}} again)
{{% endif %}}
{{% if yadm.distro == "wrongdistro2" %}}
wrong distro 2
{{% endif %}}
end of template
'''
EXPECTED = f'''
start of template
default class  = >{LOCAL_CLASS}<
default arch   = >{LOCAL_ARCH}<
default os     = >{LOCAL_OS}<
default host   = >{LOCAL_HOSTNAME}<
default user   = >{LOCAL_USER}<
default distro = >{LOCAL_DISTRO}<
Included section from else
Included section for class = {LOCAL_CLASS} ({LOCAL_CLASS} repeated)
Multiple lines
Included section for arch = {LOCAL_ARCH} ({LOCAL_ARCH} repeated)
Included section for os = {LOCAL_OS} ({LOCAL_OS} repeated)
Included section for host = {LOCAL_HOSTNAME} ({LOCAL_HOSTNAME} again)
Included section for user = {LOCAL_USER} ({LOCAL_USER} repeated)
Included section for distro = {LOCAL_DISTRO} ({LOCAL_DISTRO} again)
end of template
'''

INCLUDE_BASIC = 'basic\n'
INCLUDE_VARIABLES = '''\
included <{{ yadm.class }}> file

empty line above
'''
INCLUDE_NESTED = 'no newline at the end'

TEMPLATE_INCLUDE = '''\
The first line
{% include empty %}
An empty file removes the line above
{%include basic%}
{% include "./variables.{{ yadm.os }}"  %}
{% include dir/nested %}
Include basic again:
{% include basic %}
'''
EXPECTED_INCLUDE = f'''\
The first line
An empty file removes the line above
basic
included <{LOCAL_CLASS}> file

empty line above
no newline at the end
Include basic again:
basic
'''


def test_template_default(runner, yadm, tmpdir):
    """Test template_default"""

    input_file = tmpdir.join('input')
    input_file.write(TEMPLATE, ensure=True)
    input_file.chmod(FILE_MODE)
    output_file = tmpdir.join('output')

    # ensure overwrite works when file exists as read-only (there is some
    # special processing when this is encountered because some environments do
    # not properly overwrite read-only files)
    output_file.write('existing')
    output_file.chmod(0o400)

    script = f"""
        YADM_TEST=1 source {yadm}
        set_awk
        YADM_CLASS="{LOCAL_CLASS}"
        YADM_ARCH="{LOCAL_ARCH}"
        YADM_OS="{LOCAL_OS}"
        YADM_HOSTNAME="{LOCAL_HOSTNAME}"
        YADM_USER="{LOCAL_USER}"
        YADM_DISTRO="{LOCAL_DISTRO}"
        template_default "{input_file}" "{output_file}"
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert output_file.read() == EXPECTED
    assert os.stat(output_file).st_mode == os.stat(input_file).st_mode


def test_source(runner, yadm, tmpdir):
    """Test yadm.source"""

    input_file = tmpdir.join('input')
    input_file.write('{{yadm.source}}', ensure=True)
    input_file.chmod(FILE_MODE)
    output_file = tmpdir.join('output')

    script = f"""
        YADM_TEST=1 source {yadm}
        set_awk
        template_default "{input_file}" "{output_file}"
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert output_file.read().strip() == str(input_file)
    assert os.stat(output_file).st_mode == os.stat(input_file).st_mode


def test_include(runner, yadm, tmpdir):
    """Test include"""

    empty_file = tmpdir.join('empty')
    empty_file.write('', ensure=True)

    basic_file = tmpdir.join('basic')
    basic_file.write(INCLUDE_BASIC)

    variables_file = tmpdir.join(f'variables.{LOCAL_OS}')
    variables_file.write(INCLUDE_VARIABLES)

    nested_file = tmpdir.join('dir').join('nested')
    nested_file.write(INCLUDE_NESTED, ensure=True)

    input_file = tmpdir.join('input')
    input_file.write(TEMPLATE_INCLUDE)
    input_file.chmod(FILE_MODE)
    output_file = tmpdir.join('output')

    script = f"""
        YADM_TEST=1 source {yadm}
        set_awk
        YADM_CLASS="{LOCAL_CLASS}"
        YADM_OS="{LOCAL_OS}"
        template_default "{input_file}" "{output_file}"
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert output_file.read() == EXPECTED_INCLUDE
    assert os.stat(output_file).st_mode == os.stat(input_file).st_mode
