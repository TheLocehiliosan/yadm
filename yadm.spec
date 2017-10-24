Summary: Yet Another Dotfiles Manager
Name: yadm
Version: 1.12.0
Release: 1%{?dist}
URL: https://github.com/TheLocehiliosan/yadm
License: GPLv3
BuildRequires: hostname git gnupg bats expect
Requires: bash hostname git
Source: https://github.com/TheLocehiliosan/%{name}/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildArch: noarch

%description
yadm is a tool for managing a collection of files across multiple computers,
using a shared Git repository. In addition, yadm provides a feature to select
alternate versions of files based on the operation system or host name. Lastly,
yadm supplies the ability to manage a subset of secure files, which are
encrypted before they are included in the repository.

%prep
%setup -q

%build

%check
bats test

%install
mkdir -p ${RPM_BUILD_ROOT}%{_bindir}
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/man1
install -m 755 yadm   ${RPM_BUILD_ROOT}%{_bindir}
install -m 644 yadm.1 ${RPM_BUILD_ROOT}%{_mandir}/man1

%files
%attr(755,root,root) %{_bindir}/yadm
%attr(644,root,root) %{_mandir}/man1/*
%license LICENSE
%doc CHANGES CONTRIBUTORS README.md completion/*

%changelog
* Wed Oct 25 2017 Tim Byrne <sultan@locehilios.com> - 1.12.0-1
- Bump version to 1.12.0
- Include zsh completion

* Wed Aug 23 2017 Tim Byrne <sultan@locehilios.com> - 1.11.1-1
- Bump version to 1.11.1

* Mon Jul 10 2017 Tim Byrne <sultan@locehilios.com> - 1.11.0-1
- Bump version to 1.11.0

* Wed May 10 2017 Tim Byrne <sultan@locehilios.com> - 1.10.0-1
- Bump version to 1.10.0
- Transition to semantic versioning

* Thu May  4 2017 Tim Byrne <sultan@locehilios.com> - 1.09-1
- Bump version to 1.09
- Add yadm.bash_completion

* Mon Apr  3 2017 Tim Byrne <sultan@locehilios.com> - 1.08-1
- Bump version to 1.08

* Fri Feb 10 2017 Tim Byrne <sultan@locehilios.com> - 1.07-1
- Bump version to 1.07

* Fri Jan 13 2017 Tim Byrne <sultan@locehilios.com> - 1.06-1
- Bump version to 1.06

* Tue May 17 2016 Tim Byrne <sultan@locehilios.com> - 1.04-3
- Add missing docs
- Fix changelog format
- Remove file attribute for docs and license

* Mon May 16 2016 Tim Byrne <sultan@locehilios.com> - 1.04-2
- Add %%check
- Add %%{?dist}
- Add build dependencies
- Add license and docs
- Remove %%defattr
- Remove group tag
- Sync RPM description with man page

* Fri Apr 22 2016 Tim Byrne <sultan@locehilios.com> - 1.04-1
- Initial RPM release
