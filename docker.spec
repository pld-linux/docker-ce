#
# Conditional build:
%bcond_with	tests		# build without tests
%bcond_with	vim			# build vim syntax package

# NOTES
# https://github.com/docker/docker/blob/master/project/PACKAGERS.md#build-dependencies

Summary:	Docker: the open-source application container engine
Name:		docker
Version:	1.10.1
Release:	1
License:	Apache v2.0
Group:		Applications/System
Source0:	https://github.com/docker/docker/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	19f027d937069b104dfb0a4a01f2e30f
Source1:	%{name}.sh
Source5:	%{name}.service
Source6:	%{name}.init
Source7:	%{name}.sysconfig
URL:		https://github.com/docker/docker
BuildRequires:	btrfs-progs-devel >= 3.16.1
BuildRequires:	device-mapper-devel >= 2.02.89
BuildRequires:	golang >= 1.4
BuildRequires:	libseccomp-devel >= 2.2.1
BuildRequires:	rpmbuild(macros) >= 1.228
BuildRequires:	sqlite3-devel >= 3.7.9
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires:	iproute2 >= 3.5
Requires:	iptables
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
%define		_libexecdir		%{_prefix}/lib

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
export DOCKER_GITCOMMIT="pld/%{version}"

DEBUG=1 hack/make.sh dynbinary

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1,/etc/{rc.d/init.d,sysconfig},%{systemdunitdir}} \
	$RPM_BUILD_ROOT%{_libexecdir} \
	$RPM_BUILD_ROOT/var/lib/docker/{aufs,containers,execdriver,graph,init,tmp,trust,vfs,volumes}

install -p bundles/%{version}/dynbinary/docker-%{version} $RPM_BUILD_ROOT%{_bindir}/docker
install -p bundles/%{version}/dynbinary/dockerinit-%{version} $RPM_BUILD_ROOT%{_bindir}/dockerinit
cp -p %{SOURCE5} $RPM_BUILD_ROOT%{systemdunitdir}
install -p %{SOURCE6} $RPM_BUILD_ROOT/etc/rc.d/init.d/docker
install -p %{SOURCE1} $RPM_BUILD_ROOT%{_libexecdir}/docker
cp -p %{SOURCE7} $RPM_BUILD_ROOT/etc/sysconfig/docker
#cp -p packaging/debian/lxc-docker.1 $RPM_BUILD_ROOT%{_mandir}/man1

# install udev rules
install -d $RPM_BUILD_ROOT/lib/udev/rules.d
cp -p contrib/udev/80-docker.rules $RPM_BUILD_ROOT/lib/udev/rules.d

# bash completion
install -d $RPM_BUILD_ROOT%{bash_compdir}
cp -p contrib/completion/bash/docker $RPM_BUILD_ROOT%{bash_compdir}/docker

# vim syntax
%if %{with vim}
install -d $RPM_BUILD_ROOT%{_vimdatadir}
cp -a contrib/syntax/vim/* $RPM_BUILD_ROOT%{_vimdatadir}
%{__rm} $RPM_BUILD_ROOT%{_vimdatadir}/{LICENSE,README.md}
%endif

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
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/docker
%attr(754,root,root) /etc/rc.d/init.d/docker
%attr(755,root,root) %{_bindir}/docker
%attr(755,root,root) %{_bindir}/dockerinit
%attr(755,root,root) %{_libexecdir}/docker
%{systemdunitdir}/docker.service
/lib/udev/rules.d/80-docker.rules
#%{_mandir}/man1/lxc-docker.1*

%dir %attr(700,root,root) /var/lib/docker
%dir %attr(700,root,root) /var/lib/docker/aufs
%dir %attr(700,root,root) /var/lib/docker/containers
%dir %attr(700,root,root) /var/lib/docker/execdriver
%dir %attr(700,root,root) /var/lib/docker/graph
%dir %attr(700,root,root) /var/lib/docker/init
%dir %attr(700,root,root) /var/lib/docker/tmp
%dir %attr(700,root,root) /var/lib/docker/trust
%dir %attr(700,root,root) /var/lib/docker/vfs
%dir %attr(700,root,root) /var/lib/docker/volumes

%files -n bash-completion-%{name}
%defattr(644,root,root,755)
%{bash_compdir}/docker

%if %{with vim}
%files -n vim-syntax-%{name}
%defattr(644,root,root,755)
%doc contrib/syntax/vim/{README.md,LICENSE}
%{_vimdatadir}/doc/dockerfile.txt
%{_vimdatadir}/ftdetect/dockerfile.vim
%{_vimdatadir}/syntax/dockerfile.vim
%endif
