# TODO:
# - handle network downloads:
#  - github.com/gorilla/mux (download)
#  - github.com/gorilla/context (download)
#  - github.com/kr/pty (download)
Summary:	Docker: the Linux container engine
Name:		lxc-docker
Version:	0.5.3
Release:	0.1
License:	Apache v2.0
Group:		Applications/System
Source0:	https://github.com/dotcloud/docker/archive/v%{version}.tar.gz
# Source0-md5:	ff7b814574bbaf9e55dfe1c266ae991e
URL:		http://github.com/dotcloud/docker
BuildRequires:	golang
Requires:	lxc
Requires:	uname(release) >= 3.8
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Docker complements LXC with a high-level API which operates at the
process level. It runs unix processes with strong guarantees of
isolation and repeatability across servers.

Docker is a great building block for automating distributed systems:
large-scale web deployments, database clusters, continuous deployment
systems, private PaaS, service-oriented architectures, etc.

%prep
%setup -q -n docker-%{version}

%build
%{__make} VERBOSE=1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1}
install -p bin/docker $RPM_BUILD_ROOT%{_bindir}/lxc-docker
cp -p packaging/debian/lxc-docker.1 $RPM_BUILD_ROOT%{_mandir}/man1

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md CHANGELOG.md CONTRIBUTING.md FIXME LICENSE AUTHORS NOTICE MAINTAINERS
%attr(755,root,root) %{_bindir}/lxc-docker
%{_mandir}/man1/lxc-docker.1*
