"""Unit tests: template_j2cli & template_envtpl"""
import os
import pytest

FILE_MODE = 0o754

LOCAL_CLASS = "j2_Test+@-!^Class"
LOCAL_ARCH = "j2_Test+@-!^Arch"
LOCAL_SYSTEM = "j2_Test+@-!^System"
LOCAL_HOST = "j2_Test+@-!^Host"
LOCAL_USER = "j2_Test+@-!^User"
LOCAL_DISTRO = "j2_Test+@-!^Distro"
TEMPLATE = f'''
start of template
j2 class  = >{{{{YADM_CLASS}}}}<
j2 arch   = >{{{{YADM_ARCH}}}}<
j2 os     = >{{{{YADM_OS}}}}<
j2 host   = >{{{{YADM_HOSTNAME}}}}<
j2 user   = >{{{{YADM_USER}}}}<
j2 distro = >{{{{YADM_DISTRO}}}}<
{{%- if YADM_CLASS == "wrongclass1" %}}
wrong class 1
{{%- endif %}}
{{%- if YADM_CLASS == "{LOCAL_CLASS}" %}}
Included section for class = {{{{YADM_CLASS}}}} ({{{{YADM_CLASS}}}} repeated)
{{%- endif %}}
{{%- if YADM_CLASS == "wrongclass2" %}}
wrong class 2
{{%- endif %}}
{{%- if YADM_ARCH == "wrongarch1" %}}
wrong arch 1
{{%- endif %}}
{{%- if YADM_ARCH == "{LOCAL_ARCH}" %}}
Included section for arch = {{{{YADM_ARCH}}}} ({{{{YADM_ARCH}}}} repeated)
{{%- endif %}}
{{%- if YADM_ARCH == "wrongarch2" %}}
wrong arch 2
{{%- endif %}}
{{%- if YADM_OS == "wrongos1" %}}
wrong os 1
{{%- endif %}}
{{%- if YADM_OS == "{LOCAL_SYSTEM}" %}}
Included section for os = {{{{YADM_OS}}}} ({{{{YADM_OS}}}} repeated)
{{%- endif %}}
{{%- if YADM_OS == "wrongos2" %}}
wrong os 2
{{%- endif %}}
{{%- if YADM_HOSTNAME == "wronghost1" %}}
wrong host 1
{{%- endif %}}
{{%- if YADM_HOSTNAME == "{LOCAL_HOST}" %}}
Included section for host = {{{{YADM_HOSTNAME}}}} ({{{{YADM_HOSTNAME}}}} again)
{{%- endif %}}
{{%- if YADM_HOSTNAME == "wronghost2" %}}
wrong host 2
{{%- endif %}}
{{%- if YADM_USER == "wronguser1" %}}
wrong user 1
{{%- endif %}}
{{%- if YADM_USER == "{LOCAL_USER}" %}}
Included section for user = {{{{YADM_USER}}}} ({{{{YADM_USER}}}} repeated)
{{%- endif %}}
{{%- if YADM_USER == "wronguser2" %}}
wrong user 2
{{%- endif %}}
{{%- if YADM_DISTRO == "wrongdistro1" %}}
wrong distro 1
{{%- endif %}}
{{%- if YADM_DISTRO == "{LOCAL_DISTRO}" %}}
Included section for distro = {{{{YADM_DISTRO}}}} ({{{{YADM_DISTRO}}}} again)
{{%- endif %}}
{{%- if YADM_DISTRO == "wrongdistro2" %}}
wrong distro 2
{{%- endif %}}
end of template
'''
EXPECTED = f'''
start of template
j2 class  = >{LOCAL_CLASS}<
j2 arch   = >{LOCAL_ARCH}<
j2 os     = >{LOCAL_SYSTEM}<
j2 host   = >{LOCAL_HOST}<
j2 user   = >{LOCAL_USER}<
j2 distro = >{LOCAL_DISTRO}<
Included section for class = {LOCAL_CLASS} ({LOCAL_CLASS} repeated)
Included section for arch = {LOCAL_ARCH} ({LOCAL_ARCH} repeated)
Included section for os = {LOCAL_SYSTEM} ({LOCAL_SYSTEM} repeated)
Included section for host = {LOCAL_HOST} ({LOCAL_HOST} again)
Included section for user = {LOCAL_USER} ({LOCAL_USER} repeated)
Included section for distro = {LOCAL_DISTRO} ({LOCAL_DISTRO} again)
end of template
'''


@pytest.mark.parametrize('processor', ('j2cli', 'envtpl'))
def test_template_j2(runner, yadm, tmpdir, processor):
    """Test processing by j2cli & envtpl"""

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
        local_class="{LOCAL_CLASS}"
        local_arch="{LOCAL_ARCH}"
        local_system="{LOCAL_SYSTEM}"
        local_host="{LOCAL_HOST}"
        local_user="{LOCAL_USER}"
        local_distro="{LOCAL_DISTRO}"
        template_{processor} "{input_file}" "{output_file}"
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert output_file.read() == EXPECTED
    assert os.stat(output_file).st_mode == os.stat(input_file).st_mode


@pytest.mark.parametrize('processor', ('j2cli', 'envtpl'))
def test_source(runner, yadm, tmpdir, processor):
    """Test YADM_SOURCE"""

    input_file = tmpdir.join('input')
    input_file.write('{{YADM_SOURCE}}', ensure=True)
    input_file.chmod(FILE_MODE)
    output_file = tmpdir.join('output')

    script = f"""
        YADM_TEST=1 source {yadm}
        template_{processor} "{input_file}" "{output_file}"
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert output_file.read().strip() == str(input_file)
    assert os.stat(output_file).st_mode == os.stat(input_file).st_mode
