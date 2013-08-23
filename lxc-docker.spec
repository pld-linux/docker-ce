Summary:	Docker: the Linux container engine
Name:		lxc-docker
Version:	0.6.0
Release:	1
License:	Apache v2.0
Group:		Applications/System
Source0:	https://github.com/dotcloud/docker/archive/v%{version}.tar.gz
# Source0-md5:	1aedc1fcbb743cd44330a54334db221e
Source100:	https://raw.github.com/dotcloud/docker/v0.5.3/Makefile
# Source100-md5:	44cc86a37fc5dfe59596076d346da20d
Source1:	https://github.com/gorilla/context/archive/master.tar.gz?/gorilla-context.tgz
# Source1-md5:	621f599f7a49f56ca89c25a6d01ecc3a
Source2:	https://github.com/gorilla/mux/archive/master.tar.gz?/gorilla-mux.tgz
# Source2-md5:	e908c7da6b4b8b61b4733d4a348f015c
Source3:	https://github.com/kr/pty/archive/master.tar.gz?/kr-pty.tgz
# Source3-md5:        ffdcacc582c7b6404e71c2dce638869e
Source4:	https://github.com/dotcloud/tar/archive/master.tar.gz?/tar.tgz
# Source4-md5:	7458ecaa777e56d124b61638d597b37f
# $ PKG=code.google.com/p/go.net/ REV=84a4013f96e0; hg clone http://$PKG go.net && cd go.net && hg checkout $REV && cd .. && tar -cjf go.net.tar.gz2 --exclude-vcs go.net
Source5:	go.net.tar.bz2
# Source5-md5:	c8fd9d068430ddfa42d28d4772260eda
URL:		http://github.com/dotcloud/docker
BuildRequires:	golang >= 1.1
Requires:	iptables
Requires:	lxc
Requires:	uname(release) >= 3.8
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		bash_compdir	%{_datadir}/bash-completion/completions

# binary stripped or something
%define		_enable_debug_packages 0

%description
Docker complements LXC with a high-level API which operates at the
process level. It runs unix processes with strong guarantees of
isolation and repeatability across servers.

Docker is a great building block for automating distributed systems:
large-scale web deployments, database clusters, continuous deployment
systems, private PaaS, service-oriented architectures, etc.

%package -n bash-completion-lxc-docker
Summary:	bash-completion for Docker
Summary(pl.UTF-8):	bashowe uzupełnianie nazw dla Dockera
Group:		Applications/Shells
Requires:	%{name}
Requires:	bash-completion >= 2.0
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n bash-completion-lxc-docker
This package provides bash-completion for Docker.

%description -n bash-completion-lxc-docker -l pl.UTF-8
Pakiet ten dostarcza bashowe uzupełnianie nazw dla Dockera.

%prep
%setup -q -n docker-%{version} -a1 -a2 -a3 -a4 -a5
cp -p %{SOURCE100} .

# handle external deps offline, these are taken from Dockerfile
install -d .gopath/src/github.com/{gorilla,kr,dotcloud}
# git clone https://github.com/gorilla/context .gopath/src/github.com/gorilla/context
mv context-master .gopath/src/github.com/gorilla/context
# git clone https://github.com/gorilla/mux .gopath/src/github.com/gorilla/mux
mv mux-master .gopath/src/github.com/gorilla/mux
# git clone https://github.com/kr/pty .gopath/src/github.com/kr/pty
mv pty-master .gopath/src/github.com/kr/pty
# git clone https://github.com/dotcloud/tar .gopath/src/github.com/dotcloud/tar
mv tar-master .gopath/src/github.com/dotcloud/tar
# PKG=code.google.com/p/go.net/
install -d .gopath/src/code.google.com/p
mv go.net .gopath/src/code.google.com/p/go.net

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

# bash completion
install -d $RPM_BUILD_ROOT%{bash_compdir}
cp -p contrib/docker.bash $RPM_BUILD_ROOT%{bash_compdir}/lxc-docker
ln -s lxc-docker $RPM_BUILD_ROOT%{bash_compdir}/docker

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

%files -n bash-completion-lxc-docker
%defattr(644,root,root,755)
%{bash_compdir}/lxc-docker
%{bash_compdir}/docker
