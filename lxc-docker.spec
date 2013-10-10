#
# Conditional build:
%bcond_with	tests		# build without tests

Summary:	Docker: the Linux container engine
Name:		lxc-docker
Version:	0.6.3
Release:	3
License:	Apache v2.0
Group:		Applications/System
Source0:	https://github.com/dotcloud/docker/archive/v%{version}/docker-%{version}.tar.gz
# Source0-md5:	7926f24106b4299ffbb669d42fd7e375
Source6:	%{name}.init
URL:		http://github.com/dotcloud/docker
BuildRequires:	golang >= 1.1.2
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires:	iptables
Requires:	lxc
Requires:	rc-scripts >= 0.4.0.10
Requires:	tar
Requires:	uname(release) >= 3.8
Requires:	xz
Provides:	group(docker)
# only runs on x64 hosts for now:
# https://github.com/dotcloud/docker/issues/136
# https://github.com/dotcloud/docker/issues/611
ExclusiveArch:	%{x8664}
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
%setup -q -n docker-%{version}

install -d vendor/src/github.com/dotcloud
ln -s $(pwd) vendor/src/github.com/dotcloud/docker

%build
export GOPATH=$(pwd)/vendor
install -d build
cd build
VERSION=%{version}
GITCOMMIT=pld-%{release} # use RPM_PACKAGE_RELEASE for this
# Use these flags when compiling the tests and final binary
# without '-d', as that fails now
LDFLAGS="-X main.GITCOMMIT $GITCOMMIT -X main.VERSION $VERSION -w"
go build -v -ldflags "$LDFLAGS" -a github.com/dotcloud/docker/docker

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1,/etc/rc.d/init.d,/var/lib/docker/{containers,graph,volumes}}
install -p build/docker $RPM_BUILD_ROOT%{_bindir}/lxc-docker
install -p %{SOURCE6} $RPM_BUILD_ROOT/etc/rc.d/init.d/lxc-docker
ln -s lxc-docker $RPM_BUILD_ROOT%{_bindir}/docker
cp -p packaging/debian/lxc-docker.1 $RPM_BUILD_ROOT%{_mandir}/man1

# bash completion
install -d $RPM_BUILD_ROOT%{bash_compdir}
cp -p contrib/docker.bash $RPM_BUILD_ROOT%{bash_compdir}/lxc-docker
ln -s lxc-docker $RPM_BUILD_ROOT%{bash_compdir}/docker

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
%doc README.md CHANGELOG.md CONTRIBUTING.md FIXME LICENSE AUTHORS NOTICE MAINTAINERS
%attr(754,root,root) /etc/rc.d/init.d/lxc-docker
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
