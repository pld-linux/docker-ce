#
# Conditional build:
%bcond_with	tests		# build without tests

Summary:	Docker: the open-source application container engine
Name:		docker
Version:	1.3.3
Release:	0.1
License:	Apache v2.0
Group:		Applications/System
Source0:	https://github.com/docker/docker/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	3fdcb25a498961f6eb14a9c1d81e9244
Source5:	%{name}.service
Source6:	%{name}.init
URL:		https://github.com/docker/docker
BuildRequires:	btrfs-progs-devel
BuildRequires:	device-mapper-devel
BuildRequires:	golang >= 1.3.1
BuildRequires:	rpmbuild(macros) >= 1.228
BuildRequires:	sqlite3-devel >= 3.7.9
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires:	iproute2 >= 3.5
Requires:	iptables
Requires:	lxc >= 0.8
Requires:	rc-scripts >= 0.4.0.10
Requires:	tar >= 1:1.26
Requires:	uname(release) >= 3.8
Requires:	xz
Suggests:	git-core >= 1.7
Suggests:	libcgroup
Suggests:	xz >= 1:4.9
Provides:	group(docker)
Obsoletes:	lxc-docker < 1.1.1
Patch0:		lxc-%{name}-nosha.patch
# only runs on x64 hosts for now:
# https://github.com/docker/docker/issues/136
# https://github.com/docker/docker/issues/611
ExclusiveArch:	%{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		bash_compdir	%{_datadir}/bash-completion/completions
%define		_vimdatadir		%{_datadir}/vim

# binary stripped or something
%define		_enable_debug_packages 0

%description
Docker is an open source project to pack, ship and run any application
as a lightweight container

Docker containers are both hardware-agnostic and platform-agnostic.
This means that they can run anywhere, from your laptop to the largest
EC2 compute instance and everything in between - and they don't
require that you use a particular language, framework or packaging
system. That makes them great building blocks for deploying and
scaling web apps, databases and backend services without depending on
a particular stack or provider.

Docker is an open-source implementation of the deployment engine which
powers dotCloud, a popular Platform-as-a-Service. It benefits directly
from the experience accumulated over several years of large-scale
operation and support of hundreds of thousands of applications and
databases.

%package -n bash-completion-%{name}
Summary:	bash-completion for Docker
Summary(pl.UTF-8):	bashowe uzupełnianie nazw dla Dockera
Group:		Applications/Shells
Requires:	%{name}
Requires:	bash-completion >= 2.0
Obsoletes:	bash-completion-lxc-docker < 1.1.1
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n bash-completion-%{name}
This package provides bash-completion for Docker.

%description -n bash-completion-%{name} -l pl.UTF-8
Pakiet ten dostarcza bashowe uzupełnianie nazw dla Dockera.

%package -n vim-syntax-%{name}
Summary:	Vim syntax: Docker
Group:		Applications/Editors/Vim
Requires:	%{name} = %{version}-%{release}
Requires:	vim-rt >= 4:7.2.170
Obsoletes:	vim-syntax-lxc-docker < 1.1.1
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n vim-syntax-%{name}
This plugin provides syntax highlighting in Dockerfile.

%prep
%setup -q
%patch0 -p1

install -d vendor/src/github.com/docker
ln -s $(pwd) vendor/src/github.com/docker/docker

%build
export GOPATH=$(pwd)/vendor
install -d build
cd build
DOCKER_PKG="github.com/docker/docker"
VERSION=%{version}
GITCOMMIT=pld-%{version}-%{release} # use RPM_PACKAGE_RELEASE for this
# Use these flags when compiling the tests and final binary
# without '-d', as that fails now
LDFLAGS="-X $DOCKER_PKG/dockerversion.GITCOMMIT $GITCOMMIT -X $DOCKER_PKG/dockerversion.VERSION $VERSION -w"
go build -v -ldflags "$LDFLAGS" -a github.com/docker/docker/docker
go build -v -ldflags "$LDFLAGS" -a ../dockerinit/dockerinit.go

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1,/etc/rc.d/init.d,%{systemdunitdir},/var/lib/docker/{containers,graph,volumes}}
install -p build/docker $RPM_BUILD_ROOT%{_bindir}/docker
install -p build/dockerinit $RPM_BUILD_ROOT%{_bindir}/dockerinit
install -p %{SOURCE5} $RPM_BUILD_ROOT%{systemdunitdir}
install -p %{SOURCE6} $RPM_BUILD_ROOT/etc/rc.d/init.d/docker
#cp -p packaging/debian/lxc-docker.1 $RPM_BUILD_ROOT%{_mandir}/man1

# bash completion
install -d $RPM_BUILD_ROOT%{bash_compdir}
cp -p contrib/completion/bash/docker $RPM_BUILD_ROOT%{bash_compdir}/docker

# vim syntax
install -d $RPM_BUILD_ROOT%{_vimdatadir}
cp -a contrib/syntax/vim/* $RPM_BUILD_ROOT%{_vimdatadir}
%{__rm} $RPM_BUILD_ROOT%{_vimdatadir}/{LICENSE,README.md}

%pre
%groupadd -g 296 docker

%post
/sbin/chkconfig --add %{name}
%service -n %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
	%groupremove docker
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md CHANGELOG.md CONTRIBUTING.md LICENSE AUTHORS NOTICE MAINTAINERS
%{systemdunitdir}/docker.service
%attr(754,root,root) /etc/rc.d/init.d/docker
%attr(755,root,root) %{_bindir}/docker
%attr(755,root,root) %{_bindir}/dockerinit
#%{_mandir}/man1/lxc-docker.1*
%dir %attr(700,root,root) /var/lib/docker
%dir %attr(700,root,root) /var/lib/docker/containers
%dir %attr(700,root,root) /var/lib/docker/graph
%dir %attr(700,root,root) /var/lib/docker/volumes

%files -n bash-completion-%{name}
%defattr(644,root,root,755)
%{bash_compdir}/docker

%files -n vim-syntax-%{name}
%defattr(644,root,root,755)
%doc contrib/syntax/vim/{README.md,LICENSE}
%{_vimdatadir}/doc/dockerfile.txt
%{_vimdatadir}/ftdetect/dockerfile.vim
%{_vimdatadir}/syntax/dockerfile.vim
