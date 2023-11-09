"""Global tests configuration and fixtures"""

import collections
import contextlib
import copy
import os
import platform
import pwd
import shutil
from subprocess import PIPE, Popen

import py
import pytest


def pytest_addoption(parser):
    """Add options to pytest"""
    parser.addoption(
        "--force-linters",
        action="store_true",
        default=False,
        help="Run linters regardless of installed versions",
    )


@pytest.fixture(scope="session")
def shellcheck_version():
    """Version of shellcheck supported"""
    return "0.9.0"


@pytest.fixture(scope="session")
def pylint_version():
    """Version of pylint supported"""
    return "2.17.0"


@pytest.fixture(scope="session")
def isort_version():
    """Version of isort supported"""
    return "5.12.0"


@pytest.fixture(scope="session")
def flake8_version():
    """Version of flake8 supported"""
    return "6.0.0"


@pytest.fixture(scope="session")
def black_version():
    """Version of black supported"""
    return "23.1.0"


@pytest.fixture(scope="session")
def yamllint_version():
    """Version of yamllint supported"""
    return "1.30.0"


@pytest.fixture(scope="session")
def tst_user():
    """Test session's user id"""
    return pwd.getpwuid(os.getuid()).pw_name


@pytest.fixture(scope="session")
def tst_host():
    """Test session's short hostname value"""
    return platform.node().split(".")[0]


@pytest.fixture(scope="session")
def tst_distro(runner):
    """Test session's distro"""
    distro = ""
    with contextlib.suppress(Exception):
        run = runner(command=["lsb_release", "-si"], report=False)
        distro = run.out.strip()
    return distro


@pytest.fixture(scope="session")
def tst_distro_family(runner):
    """Test session's distro_family"""
    family = ""
    with contextlib.suppress(Exception):
        run = runner(command=["grep", "-oP", r"ID_LIKE=\K.+", "/etc/os-release"], report=False)
        family = run.out.strip()
    return family


@pytest.fixture(scope="session")
def tst_sys():
    """Test session's uname value"""
    return platform.system()


@pytest.fixture(scope="session")
def tst_arch():
    """Test session's uname value"""
    return platform.machine()


@pytest.fixture(scope="session")
def supported_commands():
    """List of supported commands

    This list should be updated every time yadm learns a new command.
    """
    return [
        "alt",
        "bootstrap",
        "clean",
        "clone",
        "config",
        "decrypt",
        "encrypt",
        "enter",
        "git-crypt",
        "gitconfig",
        "help",
        "init",
        "introspect",
        "list",
        "perms",
        "transcrypt",
        "upgrade",
        "version",
    ]


@pytest.fixture(scope="session")
def supported_configs():
    """List of supported config options

    This list should be updated every time yadm learns a new config.
    """
    return [
        "local.arch",
        "local.class",
        "local.hostname",
        "local.os",
        "local.user",
        "yadm.alt-copy",
        "yadm.auto-alt",
        "yadm.auto-exclude",
        "yadm.auto-perms",
        "yadm.auto-private-dirs",
        "yadm.cipher",
        "yadm.git-program",
        "yadm.gpg-perms",
        "yadm.gpg-program",
        "yadm.gpg-recipient",
        "yadm.openssl-ciphername",
        "yadm.openssl-old",
        "yadm.openssl-program",
        "yadm.ssh-perms",
        "yadm.template-read-only",
    ]


@pytest.fixture(scope="session")
def supported_switches():
    """List of supported switches

    This list should be updated every time yadm learns a new switch.
    """
    return [
        "--yadm-archive",
        "--yadm-bootstrap",
        "--yadm-config",
        "--yadm-data",
        "--yadm-dir",
        "--yadm-encrypt",
        "--yadm-repo",
        "-Y",
    ]


@pytest.fixture(scope="session")
def supported_local_configs(supported_configs):
    """List of supported local config options"""
    return [c for c in supported_configs if c.startswith("local.")]


class Runner:
    """Class for running commands

    Within yadm tests, this object should be used when running commands that
    require:

      * Acting on the status code
      * Parsing the output of the command
      * Passing input to the command

    Other instances of simply running commands should use os.system().
    """

    def __init__(self, command, inp=None, shell=False, cwd=None, env=None, expect=None, report=True):
        if shell:
            self.command = " ".join([str(cmd) for cmd in command])
        else:
            self.command = command
        if env is None:
            env = {}
        merged_env = os.environ.copy()
        merged_env.update(env)
        self.inp = inp
        self.wrap(expect)
        with Popen(
            self.command,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            shell=shell,
            cwd=cwd,
            env=merged_env,
        ) as process:
            input_bytes = self.inp
            if self.inp:
                input_bytes = self.inp.encode()
            (out_bstream, err_bstream) = process.communicate(input=input_bytes)
            self.out = out_bstream.decode()
            self.err = err_bstream.decode()
            self.code = process.wait()
        self.success = self.code == 0
        self.failure = self.code != 0
        if report:
            self.report()

    def __repr__(self):
        return f"Runner({self.command})"

    def report(self):
        """Print code/stdout/stderr"""
        print(f"{self}")
        print(f"  RUN: code:{self.code}")
        if self.inp:
            print(f"  RUN: input:\n{self.inp}")
        print(f"  RUN: stdout:\n{self.out}")
        print(f"  RUN: stderr:\n{self.err}")

    def wrap(self, expect):
        """Wrap command with expect"""
        if not expect:
            return
        cmdline = " ".join([f'"{w}"' for w in self.command])
        expect_script = f"set timeout 2\nspawn {cmdline}\n"
        for question, answer in expect:
            expect_script += "expect {\n" f'"{question}" {{send "{answer}\\r"}}\n' "timeout {close;exit 128}\n" "}\n"
        expect_script += "expect eof\n" "foreach {pid spawnid os_error_flag value} [wait] break\n" "exit $value"
        self.inp = expect_script
        print(f"EXPECT:{expect_script}")
        self.command = ["expect"]


@pytest.fixture(scope="session")
def runner():
    """Class for running commands"""
    return Runner


@pytest.fixture(scope="session")
def config_git():
    """Configure global git configuration, if missing"""
    os.system("git config init.defaultBranch || git config --global init.defaultBranch master")
    os.system('git config user.name || git config --global user.name "test"')
    os.system('git config user.email || git config --global user.email "test@test.test"')


@pytest.fixture()
def repo_config(runner, paths):
    """Function to query a yadm repo configuration value"""

    def query_func(key):
        """Query a yadm repo configuration value"""
        run = runner(
            command=("git", "config", "--local", key),
            env={"GIT_DIR": paths.repo},
            report=False,
        )
        return run.out.rstrip()

    return query_func


@pytest.fixture(scope="session")
def yadm():
    """Path to yadm program to be tested"""
    full_path = os.path.realpath("yadm")
    assert os.path.isfile(full_path), "yadm program file isn't present"
    return full_path


@pytest.fixture()
def paths(tmpdir, yadm):
    """Function scoped test paths"""

    dir_root = tmpdir.mkdir("root")
    dir_remote = dir_root.mkdir("remote")
    dir_work = dir_root.mkdir("work")
    dir_xdg_data = dir_root.mkdir("xdg_data")
    dir_xdg_home = dir_root.mkdir("xdg_home")
    dir_data = dir_xdg_data.mkdir("yadm")
    dir_yadm = dir_xdg_home.mkdir("yadm")
    dir_hooks = dir_yadm.mkdir("hooks")
    dir_repo = dir_data.mkdir("repo.git")
    file_archive = dir_data.join("archive")
    file_bootstrap = dir_yadm.join("bootstrap")
    file_config = dir_yadm.join("config")
    file_encrypt = dir_yadm.join("encrypt")
    paths = collections.namedtuple(
        "Paths",
        [
            "pgm",
            "root",
            "remote",
            "work",
            "xdg_data",
            "xdg_home",
            "data",
            "yadm",
            "hooks",
            "repo",
            "archive",
            "bootstrap",
            "config",
            "encrypt",
        ],
    )
    os.environ["XDG_CONFIG_HOME"] = str(dir_xdg_home)
    os.environ["XDG_DATA_HOME"] = str(dir_xdg_data)
    return paths(
        yadm,
        dir_root,
        dir_remote,
        dir_work,
        dir_xdg_data,
        dir_xdg_home,
        dir_data,
        dir_yadm,
        dir_hooks,
        dir_repo,
        file_archive,
        file_bootstrap,
        file_config,
        file_encrypt,
    )


@pytest.fixture()
def yadm_cmd(paths):
    """Generate custom command_list function"""

    def command_list(*args):
        """Produce params for running yadm with -Y"""
        return [paths.pgm] + list(args)

    return command_list


class NoRelativePath(Exception):
    """Exception when finding relative paths"""


class DataFile:
    """Datafile object"""

    def __init__(self, path, tracked=True, private=False):
        self.__path = path
        self.__parent = None
        self.__tracked = tracked
        self.__private = private

    @property
    def path(self):
        """Path property"""
        return self.__path

    @property
    def relative(self):
        """Relative path property"""
        if self.__parent:
            return self.__parent.join(self.path)
        raise NoRelativePath("Unable to provide relative path, no parent")

    @property
    def tracked(self):
        """Tracked property"""
        return self.__tracked

    @property
    def private(self):
        """Private property"""
        return self.__private

    def relative_to(self, parent):
        """Update all relative paths to this py.path"""
        self.__parent = parent


class DataSet:
    """Dataset object"""

    def __init__(self):
        self.__files = []
        self.__dirs = []
        self.__tracked_dirs = []
        self.__private_dirs = []
        self.__relpath = None

    def __repr__(self):
        return f"[DS with {len(self)} files; " f"{len(self.tracked)} tracked, " f"{len(self.private)} private]"

    def __iter__(self):
        return iter(self.__files)

    def __len__(self):
        return len(self.__files)

    def __contains__(self, datafile):
        if [f for f in self.__files if f.path == datafile]:
            return True
        if datafile in self.__files:
            return True
        return False

    @property
    def files(self):
        """List of DataFiles in DataSet"""
        return list(self.__files)

    @property
    def tracked(self):
        """List of tracked DataFiles in DataSet"""
        return [f for f in self.__files if f.tracked]

    @property
    def private(self):
        """List of private DataFiles in DataSet"""
        return [f for f in self.__files if f.private]

    @property
    def dirs(self):
        """List of directories in DataSet"""
        return list(self.__dirs)

    @property
    def plain_dirs(self):
        """List of directories in DataSet not starting with '.'"""
        return [d for d in self.dirs if not d.startswith(".")]

    @property
    def hidden_dirs(self):
        """List of directories in DataSet starting with '.'"""
        return [d for d in self.dirs if d.startswith(".")]

    @property
    def tracked_dirs(self):
        """List of directories in DataSet not starting with '.'"""
        return [d for d in self.__tracked_dirs if not d.startswith(".")]

    @property
    def private_dirs(self):
        """List of directories in DataSet considered 'private'"""
        return list(self.__private_dirs)

    def add_file(self, path, tracked=True, private=False):
        """Add file to data set"""
        if path not in self:
            datafile = DataFile(path, tracked, private)
            if self.__relpath:
                datafile.relative_to(self.__relpath)
            self.__files.append(datafile)

        dname = os.path.dirname(path)
        if dname and dname not in self.__dirs:
            self.__dirs.append(dname)
            if tracked:
                self.__tracked_dirs.append(dname)
            if private:
                self.__private_dirs.append(dname)

    def relative_to(self, relpath):
        """Update all relative paths to this py.path"""
        self.__relpath = relpath
        for datafile in self.files:
            datafile.relative_to(self.__relpath)


@pytest.fixture(scope="session")
def ds1_dset(tst_sys):
    """Meta-data for dataset one files"""
    dset = DataSet()
    dset.add_file("t1")
    dset.add_file("d1/t2")
    dset.add_file(f"test_alt_copy##os.{tst_sys}")
    dset.add_file("u1", tracked=False)
    dset.add_file("d2/u2", tracked=False)
    dset.add_file(".ssh/p1", tracked=False, private=True)
    dset.add_file(".ssh/.p2", tracked=False, private=True)
    dset.add_file(".gnupg/p3", tracked=False, private=True)
    dset.add_file(".gnupg/.p4", tracked=False, private=True)
    return dset


@pytest.fixture(scope="session")
def ds1_data(tmpdir_factory, config_git, ds1_dset, runner):
    """A set of test data, worktree & repo"""
    # pylint: disable=unused-argument
    # This is ignored because
    # @pytest.mark.usefixtures('config_git')
    # cannot be applied to another fixture.

    data = tmpdir_factory.mktemp("ds1")

    work = data.mkdir("work")
    for datafile in ds1_dset:
        work.join(datafile.path).write(datafile.path, ensure=True)

    repo = data.mkdir("repo.git")
    env = os.environ.copy()
    env["GIT_DIR"] = str(repo)
    runner(command=["git", "init", "--shared=0600", "--bare", str(repo)], report=False)
    runner(command=["git", "config", "core.bare", "false"], env=env, report=False)
    runner(command=["git", "config", "status.showUntrackedFiles", "no"], env=env, report=False)
    runner(command=["git", "config", "yadm.managed", "true"], env=env, report=False)
    runner(command=["git", "config", "core.worktree", str(work)], env=env, report=False)
    runner(command=["git", "add"] + [str(work.join(f.path)) for f in ds1_dset if f.tracked], env=env)
    runner(command=["git", "commit", "--allow-empty", "-m", "Initial commit"], env=env, report=False)

    data = collections.namedtuple("Data", ["work", "repo"])
    return data(work, repo)


@pytest.fixture()
def ds1_work_copy(ds1_data, paths):
    """Function scoped copy of ds1_data.work"""
    shutil.copytree(str(ds1_data.work), str(paths.work), dirs_exist_ok=True)


@pytest.fixture()
def ds1_repo_copy(runner, ds1_data, paths):
    """Function scoped copy of ds1_data.repo"""
    shutil.copytree(str(ds1_data.repo), str(paths.repo), dirs_exist_ok=True)
    env = os.environ.copy()
    env["GIT_DIR"] = str(paths.repo)
    runner(command=["git", "config", "core.worktree", str(paths.work)], env=env, report=False)


@pytest.fixture()
def ds1_copy(ds1_work_copy, ds1_repo_copy):
    """Function scoped copy of ds1_data"""
    # pylint: disable=unused-argument
    # This is ignored because
    # @pytest.mark.usefixtures('ds1_work_copy', 'ds1_repo_copy')
    # cannot be applied to another fixture.
    return None


@pytest.fixture()
def ds1(ds1_work_copy, paths, ds1_dset):
    """Function scoped ds1_dset w/paths"""
    # pylint: disable=unused-argument
    # This is ignored because
    # @pytest.mark.usefixtures('ds1_copy')
    # cannot be applied to another fixture.
    dscopy = copy.deepcopy(ds1_dset)
    dscopy.relative_to(copy.deepcopy(paths.work))
    return dscopy


@pytest.fixture(scope="session")
def gnupg(tmpdir_factory, runner):
    """Location of GNUPGHOME"""

    def register_gpg_password(password):
        """Publish a new GPG mock password"""
        py.path.local("/tmp/mock-password").write(password)

    home = tmpdir_factory.mktemp("gnupghome")
    home.chmod(0o700)
    conf = home.join("gpg.conf")
    conf.write("no-secmem-warning\n")
    conf.chmod(0o600)
    agentconf = home.join("gpg-agent.conf")
    agentconf.write(f'pinentry-program {os.path.abspath("test/pinentry-mock")}\n' "max-cache-ttl 0\n")
    agentconf.chmod(0o600)
    data = collections.namedtuple("GNUPG", ["home", "pw"])
    env = os.environ.copy()
    env["GNUPGHOME"] = home

    # this pre-populates std files in the GNUPGHOME
    runner(["gpg", "-k"], env=env)

    return data(home, register_gpg_password)
