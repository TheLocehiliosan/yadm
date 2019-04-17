%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}
Name: yadm
Summary: Yet Another Dotfiles Manager
Version: 1.12.0
Group: Development/Tools
Release: 1%{?dist}
URL: https://yadm.io
License: GPL-3.0-only
Requires: bash
Requires: git
%if 0%{?fedora} || 0%{?rhel_version} || 0%{?centos_version} >= 700
Requires: /usr/bin/hostname
%else
Requires: /bin/hostname
%endif

Source: %{name}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-build
BuildArch: noarch

%description
yadm is a tool for managing a collection of files across multiple computers,
using a shared Git repository. In addition, yadm provides a feature to select
alternate versions of files based on the operation system or host name. Lastly,
yadm supplies the ability to manage a subset of secure files, which are
encrypted before they are included in the repository.

%prep
%setup -c

%build

%install

# this is done to allow paths other than yadm-x.x.x (for example, when building
# from branches instead of release tags)
cd *yadm-*

%{__mkdir} -p %{buildroot}%{_bindir}
%{__cp}  yadm %{buildroot}%{_bindir}

%{__mkdir} -p  %{buildroot}%{_mandir}/man1
%{__cp} yadm.1 %{buildroot}%{_mandir}/man1

%{__mkdir} -p                        %{buildroot}%{_pkgdocdir}
%{__cp} README.md                    %{buildroot}%{_pkgdocdir}/README
%{__cp} CHANGES CONTRIBUTORS LICENSE %{buildroot}%{_pkgdocdir}
%{__cp} -r completion contrib        %{buildroot}%{_pkgdocdir}

%files
%attr(755,root,root) %{_bindir}/yadm
%attr(644,root,root) %{_mandir}/man1/*
%doc %{_pkgdocdir}

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
