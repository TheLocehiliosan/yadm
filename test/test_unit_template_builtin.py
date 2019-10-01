"""Unit tests: template_builtin"""

# these values are also testing the handling of bizarre characters
LOCAL_CLASS = "builtin_Test+@-!^Class"
LOCAL_SYSTEM = "builtin_Test+@-!^System"
LOCAL_HOST = "builtin_Test+@-!^Host"
LOCAL_USER = "builtin_Test+@-!^User"
LOCAL_DISTRO = "builtin_Test+@-!^Distro"
TEMPLATE = f'''
start of template
builtin class  = >YADM_CLASS<
builtin os     = >YADM_OS<
builtin host   = >YADM_HOSTNAME<
builtin user   = >YADM_USER<
builtin distro = >YADM_DISTRO<
YADM_IF CLASS="wrongclass1"
wrong class 1
YADM_END
YADM_IF CLASS="{LOCAL_CLASS}"
Included section for class = YADM_CLASS (YADM_CLASS repeated)
YADM_END
YADM_IF CLASS="wrongclass2"
wrong class 2
YADM_END
YADM_IF OS="wrongos1"
wrong os 1
YADM_END
YADM_IF OS="{LOCAL_SYSTEM}"
Included section for os = YADM_OS (YADM_OS repeated)
YADM_END
YADM_IF OS="wrongos2"
wrong os 2
YADM_END
YADM_IF HOSTNAME="wronghost1"
wrong host 1
YADM_END
YADM_IF HOSTNAME="{LOCAL_HOST}"
Included section for host = YADM_HOSTNAME (YADM_HOSTNAME repeated)
YADM_END
YADM_IF HOSTNAME="wronghost2"
wrong host 2
YADM_END
YADM_IF USER="wronguser1"
wrong user 1
YADM_END
YADM_IF USER="{LOCAL_USER}"
Included section for user = YADM_USER (YADM_USER repeated)
YADM_END
YADM_IF USER="wronguser2"
wrong user 2
YADM_END
YADM_IF DISTRO="wrongdistro1"
wrong distro 1
YADM_END
YADM_IF DISTRO="{LOCAL_DISTRO}"
Included section for distro = YADM_DISTRO (YADM_DISTRO repeated)
YADM_END
YADM_IF DISTRO="wrongdistro2"
wrong distro 2
YADM_END
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
Included section for host = {LOCAL_HOST} ({LOCAL_HOST} repeated)
Included section for user = {LOCAL_USER} ({LOCAL_USER} repeated)
Included section for distro = {LOCAL_DISTRO} ({LOCAL_DISTRO} repeated)
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
