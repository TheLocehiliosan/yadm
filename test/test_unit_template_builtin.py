"""Unit tests: template_builtin"""

# these values are also testing the handling of bizarre characters
LOCAL_CLASS = "builtin_Test+@-!^Class"
LOCAL_SYSTEM = "builtin_Test+@-!^System"
LOCAL_HOST = "builtin_Test+@-!^Host"
LOCAL_USER = "builtin_Test+@-!^User"
LOCAL_DISTRO = "builtin_Test+@-!^Distro"
TEMPLATE = f'''
start of template
builtin class  = >{{{{yadm.class}}}}<
builtin os     = >{{{{yadm.os}}}}<
builtin host   = >{{{{yadm.hostname}}}}<
builtin user   = >{{{{yadm.user}}}}<
builtin distro = >{{{{yadm.distro}}}}<
{{% if yadm.class == "wrongclass1" %}}
wrong class 1
{{% endif %}}
{{% if yadm.class == "{LOCAL_CLASS}" %}}
Included section for class = {{{{yadm.class}}}} ({{{{yadm.class}}}} repeated)
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
builtin class  = >{LOCAL_CLASS}<
builtin os     = >{LOCAL_SYSTEM}<
builtin host   = >{LOCAL_HOST}<
builtin user   = >{LOCAL_USER}<
builtin distro = >{LOCAL_DISTRO}<
Included section for class = {LOCAL_CLASS} ({LOCAL_CLASS} repeated)
Included section for os = {LOCAL_SYSTEM} ({LOCAL_SYSTEM} repeated)
Included section for host = {LOCAL_HOST} ({LOCAL_HOST} again)
Included section for user = {LOCAL_USER} ({LOCAL_USER} repeated)
Included section for distro = {LOCAL_DISTRO} ({LOCAL_DISTRO} again)
end of template
'''


def test_template_builtin(runner, yadm, tmpdir):
    """Test template_builtin"""

    input_file = tmpdir.join('input')
    input_file.write(TEMPLATE, ensure=True)
    output_file = tmpdir.join('output')

    script = f"""
        YADM_TEST=1 source {yadm}
        local_class="{LOCAL_CLASS}"
        local_system="{LOCAL_SYSTEM}"
        local_host="{LOCAL_HOST}"
        local_user="{LOCAL_USER}"
        local_distro="{LOCAL_DISTRO}"
        template_builtin "{input_file}" "{output_file}"
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert output_file.read() == EXPECTED
