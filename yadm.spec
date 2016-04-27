Summary: Yet Another Dotfiles Manager
Name: yadm
Version: 1.04
Release: 1
URL: https://github.com/TheLocehiliosan/yadm
License: GPLv3
Group: Development/Tools
Requires: bash
Requires: git
Source: https://github.com/TheLocehiliosan/%{name}/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildArch: noarch

%description
yadm is a dotfile management tool with 3 main features: Manages files across
systems using a single Git repository. Provides a way to use alternate files on
a specific OS or host. Supplies a method of encrypting confidential data so it
can safely be stored in your repository.

%prep
%setup -q

%build

%install
mkdir -p ${RPM_BUILD_ROOT}%{_bindir}
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/man1
install -m 755 yadm   ${RPM_BUILD_ROOT}%{_bindir}
install -m 644 yadm.1 ${RPM_BUILD_ROOT}%{_mandir}/man1

%files
%defattr(-,root,root)
%attr(755,root,root) %{_bindir}/yadm
%attr(644,root,root) %{_mandir}/man1/*

%changelog
* Fri Apr 22 2016 Tim Byrne <sultan@locehilios.com> 1.04-1
- Support alternate paths for yadm data
- Support asymmetric encryption
- Prevent the mixing of output and gpg prompts
