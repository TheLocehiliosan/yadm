"""Unit tests: template_default"""
import os

FILE_MODE = 0o754

# these values are also testing the handling of bizarre characters
LOCAL_CLASS = "default_Test+@-!^Class"
LOCAL_SYSTEM = "default_Test+@-!^System"
LOCAL_HOST = "default_Test+@-!^Host"
LOCAL_USER = "default_Test+@-!^User"
LOCAL_DISTRO = "default_Test+@-!^Distro"
TEMPLATE = f'''
start of template
default class  = >{{{{yadm.class}}}}<
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
{{% if yadm.os == "wrongos1" %}}
wrong os 1
{{% endif %}}
{{% if yadm.os == "{LOCAL_SYSTEM}" %}}
Included section for os = {{{{yadm.os}}}} ({{{{yadm.os}}}} repeated)
{{% endif %}}
{{% if yadm.os == "wrongos2" %}}
wrong os 2
{{% endif %}}
{{% if yadm.hostname == "wronghost1" %}}
wrong host 1
{{% endif %}}
{{% if yadm.hostname == "{LOCAL_HOST}" %}}
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
default os     = >{LOCAL_SYSTEM}<
default host   = >{LOCAL_HOST}<
default user   = >{LOCAL_USER}<
default distro = >{LOCAL_DISTRO}<
Included section from else
Included section for class = {LOCAL_CLASS} ({LOCAL_CLASS} repeated)
Multiple lines
Included section for os = {LOCAL_SYSTEM} ({LOCAL_SYSTEM} repeated)
Included section for host = {LOCAL_HOST} ({LOCAL_HOST} again)
Included section for user = {LOCAL_USER} ({LOCAL_USER} repeated)
Included section for distro = {LOCAL_DISTRO} ({LOCAL_DISTRO} again)
end of template
'''


def test_template_default(runner, yadm, tmpdir):
    """Test template_default"""

    input_file = tmpdir.join('input')
    input_file.write(TEMPLATE, ensure=True)
    input_file.chmod(FILE_MODE)
    output_file = tmpdir.join('output')

    script = f"""
        YADM_TEST=1 source {yadm}
        set_awk
        local_class="{LOCAL_CLASS}"
        local_system="{LOCAL_SYSTEM}"
        local_host="{LOCAL_HOST}"
        local_user="{LOCAL_USER}"
        local_distro="{LOCAL_DISTRO}"
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
