Summary:	Docker: the Linux container engine
Name:		lxc-docker
Version:	0.5.3
Release:	0.1
License:	Apache v2.0
Group:		Applications/System
Source0:	https://github.com/dotcloud/docker/archive/v%{version}.tar.gz
# Source0-md5:	ff7b814574bbaf9e55dfe1c266ae991e
Source1:	https://github.com/gorilla/context/archive/master.tar.gz?/gorilla-context.tgz
# Source1-md5:	621f599f7a49f56ca89c25a6d01ecc3a
Source2:	https://github.com/gorilla/mux/archive/master.tar.gz?/gorilla-mux.tgz
# Source2-md5:	e908c7da6b4b8b61b4733d4a348f015c
Source3:	https://github.com/kr/pty/archive/master.tar.gz?/kr-pty.tgz
# Source3-md5:	ffdcacc582c7b6404e71c2dce638869e
URL:		http://github.com/dotcloud/docker
BuildRequires:	git-core
BuildRequires:	golang >= 1.1
Requires:	lxc
Requires:	uname(release) >= 3.8
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# binary stripped or something
%define		_enable_debug_packages 0

%description
Docker complements LXC with a high-level API which operates at the
process level. It runs unix processes with strong guarantees of
isolation and repeatability across servers.

Docker is a great building block for automating distributed systems:
large-scale web deployments, database clusters, continuous deployment
systems, private PaaS, service-oriented architectures, etc.

%prep
%setup -q -n docker-%{version} -a1 -a2 -a3

# handle external deps offline
install -d .gopath/src/github.com/{gorilla,kr}
# git clone https://github.com/gorilla/context .gopath/src/github.com/gorilla/context
mv context-master .gopath/src/github.com/gorilla/context
# git clone https://github.com/gorilla/mux .gopath/src/github.com/gorilla/mux
mv mux-master .gopath/src/github.com/gorilla/mux
# git clone https://github.com/kr/pty .gopath/src/github.com/kr/pty
mv pty-master .gopath/src/github.com/kr/pty

%build
# avoid interfering with builder env
unset GIT_WORK_TREE
unset GIT_DIR
%{__make} VERBOSE=1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1,/var/lib/docker/{containers,graph,volumes}}
install -p bin/docker $RPM_BUILD_ROOT%{_bindir}/lxc-docker
ln -s lxc-docker $RPM_BUILD_ROOT%{_bindir}/docker
cp -p packaging/debian/lxc-docker.1 $RPM_BUILD_ROOT%{_mandir}/man1

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md CHANGELOG.md CONTRIBUTING.md FIXME LICENSE AUTHORS NOTICE MAINTAINERS
%attr(755,root,root) %{_bindir}/lxc-docker
%attr(755,root,root) %{_bindir}/docker
%{_mandir}/man1/lxc-docker.1*
%dir %attr(700,root,root) /var/lib/docker
%dir %attr(700,root,root) /var/lib/docker/containers
%dir %attr(700,root,root) /var/lib/docker/graph
%dir %attr(700,root,root) /var/lib/docker/volumes
