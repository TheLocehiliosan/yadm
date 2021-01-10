"""Unit tests: template_esh"""
import os

FILE_MODE = 0o754

LOCAL_CLASS = "esh_Test+@-!^Class"
LOCAL_CLASS2 = "esh_Test+@-|^2nd_Class withSpace"
LOCAL_ARCH = "esh_Test+@-!^Arch"
LOCAL_SYSTEM = "esh_Test+@-!^System"
LOCAL_HOST = "esh_Test+@-!^Host"
LOCAL_USER = "esh_Test+@-!^User"
LOCAL_DISTRO = "esh_Test+@-!^Distro"
TEMPLATE = f'''
start of template
esh class  = ><%=$YADM_CLASS%><
esh arch   = ><%=$YADM_ARCH%><
esh os     = ><%=$YADM_OS%><
esh host   = ><%=$YADM_HOSTNAME%><
esh user   = ><%=$YADM_USER%><
esh distro = ><%=$YADM_DISTRO%><
<% if [ "$YADM_CLASS" = "wrongclass1" ]; then -%>
wrong class 1
<% fi -%>
<% if [ "$YADM_CLASS" = "{LOCAL_CLASS}" ]; then -%>
Included section for class = <%=$YADM_CLASS%> (<%=$YADM_CLASS%> repeated)
<% fi -%>
<% if [ "$YADM_CLASS" = "wrongclass2" ]; then -%>
wrong class 2
<% fi -%>
<% echo "$YADM_CLASSES" | while IFS='' read cls; do
   if [ "$cls" = "{LOCAL_CLASS2}" ]; then -%>
Included section for second class
<% fi; done -%>
<% if [ "$YADM_ARCH" = "wrongarch1" ]; then -%>
wrong arch 1
<% fi -%>
<% if [ "$YADM_ARCH" = "{LOCAL_ARCH}" ]; then -%>
Included section for arch = <%=$YADM_ARCH%> (<%=$YADM_ARCH%> repeated)
<% fi -%>
<% if [ "$YADM_ARCH" = "wrongarch2" ]; then -%>
wrong arch 2
<% fi -%>
<% if [ "$YADM_OS" = "wrongos1" ]; then -%>
wrong os 1
<% fi -%>
<% if [ "$YADM_OS" = "{LOCAL_SYSTEM}" ]; then -%>
Included section for os = <%=$YADM_OS%> (<%=$YADM_OS%> repeated)
<% fi -%>
<% if [ "$YADM_OS" = "wrongos2" ]; then -%>
wrong os 2
<% fi -%>
<% if [ "$YADM_HOSTNAME" = "wronghost1" ]; then -%>
wrong host 1
<% fi -%>
<% if [ "$YADM_HOSTNAME" = "{LOCAL_HOST}" ]; then -%>
Included section for host = <%=$YADM_HOSTNAME%> (<%=$YADM_HOSTNAME%> again)
<% fi -%>
<% if [ "$YADM_HOSTNAME" = "wronghost2" ]; then -%>
wrong host 2
<% fi -%>
<% if [ "$YADM_USER" = "wronguser1" ]; then -%>
wrong user 1
<% fi -%>
<% if [ "$YADM_USER" = "{LOCAL_USER}" ]; then -%>
Included section for user = <%=$YADM_USER%> (<%=$YADM_USER%> repeated)
<% fi -%>
<% if [ "$YADM_USER" = "wronguser2" ]; then -%>
wrong user 2
<% fi -%>
<% if [ "$YADM_DISTRO" = "wrongdistro1" ]; then -%>
wrong distro 1
<% fi -%>
<% if [ "$YADM_DISTRO" = "{LOCAL_DISTRO}" ]; then -%>
Included section for distro = <%=$YADM_DISTRO%> (<%=$YADM_DISTRO%> again)
<% fi -%>
<% if [ "$YADM_DISTRO" = "wrongdistro2" ]; then -%>
wrong distro 2
<% fi -%>
end of template
'''
EXPECTED = f'''
start of template
esh class  = >{LOCAL_CLASS}<
esh arch   = >{LOCAL_ARCH}<
esh os     = >{LOCAL_SYSTEM}<
esh host   = >{LOCAL_HOST}<
esh user   = >{LOCAL_USER}<
esh distro = >{LOCAL_DISTRO}<
Included section for class = {LOCAL_CLASS} ({LOCAL_CLASS} repeated)
Included section for second class
Included section for arch = {LOCAL_ARCH} ({LOCAL_ARCH} repeated)
Included section for os = {LOCAL_SYSTEM} ({LOCAL_SYSTEM} repeated)
Included section for host = {LOCAL_HOST} ({LOCAL_HOST} again)
Included section for user = {LOCAL_USER} ({LOCAL_USER} repeated)
Included section for distro = {LOCAL_DISTRO} ({LOCAL_DISTRO} again)
end of template
'''


def test_template_esh(runner, yadm, tmpdir):
    """Test processing by esh"""

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
        local_classes=("{LOCAL_CLASS2}" "{LOCAL_CLASS}")
        local_arch="{LOCAL_ARCH}"
        local_system="{LOCAL_SYSTEM}"
        local_host="{LOCAL_HOST}"
        local_user="{LOCAL_USER}"
        local_distro="{LOCAL_DISTRO}"
        template_esh "{input_file}" "{output_file}"
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert output_file.read().strip() == str(EXPECTED).strip()
    assert os.stat(output_file).st_mode == os.stat(input_file).st_mode


def test_source(runner, yadm, tmpdir):
    """Test YADM_SOURCE"""

    input_file = tmpdir.join('input')
    input_file.write('<%= $YADM_SOURCE %>', ensure=True)
    input_file.chmod(FILE_MODE)
    output_file = tmpdir.join('output')

    script = f"""
        YADM_TEST=1 source {yadm}
        template_esh "{input_file}" "{output_file}"
    """
    run = runner(command=['bash'], inp=script)
    assert run.success
    assert run.err == ''
    assert output_file.read().strip() == str(input_file)
    assert os.stat(output_file).st_mode == os.stat(input_file).st_mode
