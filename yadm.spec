Summary: Yet Another Dotfiles Manager
Name: yadm
Version: 1.02
Release: 1
URL: https://github.com/TheLocehiliosan/yadm
License: GPL
Group: Development/Tools
Packager: Tim Byrne <sultan@locehilios.com>
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires: bash
Requires: git
Source0: %{name}-%{version}.tar.gz
BuildArch: noarch

%description
yadm is a dotfile management tool with 3 main features: Manages files across
systems using a single Git repository. Provides a way to use alternate files on
a specific OS or host. Supplies a method of encrypting confidential data so it
can safely be stored in your repository.

%prep
%setup

%build

%install
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}%{_bindir}
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/man1
install -m 755 yadm   ${RPM_BUILD_ROOT}%{_bindir}
install -m 644 yadm.1 ${RPM_BUILD_ROOT}%{_mandir}/man1

%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(-,root,root)
%attr(755,root,root) %{_bindir}/yadm
%attr(644,root,root) %{_mandir}/man1/*
