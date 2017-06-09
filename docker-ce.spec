#
# Conditional build:
%bcond_with	tests		# build without tests
%bcond_with	vim			# build vim syntax package (bundled in vim 7.4.979-2)
%bcond_with	doc			# build manual pages

# NOTES
# https://github.com/docker/docker/blob/master/project/PACKAGERS.md#build-dependencies

# v1.0.0-rc2-136-g54296cf4
%define	runc_commit 54296cf
# v0.2.6
%define	containerd_commit 4ab9917
# v0.8.0-dev.2-464-g0f53435
%define	libnetwork_commit 0f53435
%define	subver -rc1
Summary:	Docker CE: the open-source application container engine
Name:		docker-ce
# Using Docker-CE, Stay on Stable channel
# https://docs.docker.com/engine/installation/
Version:	17.03.2
Release:	0.1
License:	Apache v2.0
Group:		Applications/System
# https://github.com/docker/docker/releases
Source0:	https://github.com/docker/docker/archive/v%{version}-ce%{subver}/%{name}-%{version}-ce%{subver}.tar.gz
# Source0-md5:	4434d6891814a02f1e7f3879fa85cc65
Source1:	https://github.com/docker/runc/archive/%{runc_commit}/runc-%{runc_commit}.tar.gz
# Source1-md5:	c4eff71ea7da80d25f7cece171683a03
Source2:	https://github.com/docker/containerd/archive/%{containerd_commit}/containerd-%{containerd_commit}.tar.gz
# Source2-md5:	37dae1d17f530c2c7f7a35d3bf0977a4
Source3:	https://github.com/docker/libnetwork/archive/%{libnetwork_commit}/libnetwork-%{libnetwork_commit}.tar.gz
# Source3-md5:	7cfbfe76355aae3577c77a6a4b2c92db
Source4:	https://github.com/krallin/tini/archive/v0.13.0/tini-0.13.0.tar.gz
# Source4-md5:	c29541112a242c53c82bb6b1213f288f
Source5:	dockerd.sh
Source7:	docker.init
Source8:	docker.sysconfig
Patch0:		systemd.patch
URL:		https://www.docker.com/community-edition/
BuildRequires:	btrfs-progs-devel >= 3.16.1
BuildRequires:	cmake
BuildRequires:	device-mapper-devel >= 2.02.89
BuildRequires:	golang >= 1.6
BuildRequires:	libseccomp-devel >= 2.2.1
BuildRequires:	rpmbuild(macros) >= 1.644
BuildRequires:	sqlite3-devel >= 3.7.9
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires:	ca-certificates
Requires:	iproute2 >= 3.5
Requires:	iptables
Requires:	rc-scripts >= 0.4.0.10
Requires:	systemd-units >= 38
Requires:	tar >= 1:1.26
Requires:	uname(release) >= 3.8
Requires:	xz
Suggests:	docker-credential-helpers
Suggests:	git-core >= 1.7
Suggests:	libcgroup
Suggests:	xz >= 1:4.9
Provides:	group(docker)
Obsoletes:	docker < 17.0
Obsoletes:	lxc-docker < 1.1.1
# only runs on x64 hosts for now:
# https://github.com/docker/docker/issues/136
# https://github.com/docker/docker/issues/611
ExclusiveArch:	%{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		bash_compdir	%{_datadir}/bash-completion/completions
%define		zsh_compdir	%{_datadir}/zsh/site-functions
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

%package -n zsh-completion-%{name}
Summary:	zsh completion for Docker
Summary(pl.UTF-8):	Uzupełnianie parametrów w zsh dla poleceń Dockera
Group:		Applications/Shells
Requires:	%{name}
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n zsh-completion-%{name}
This package provides zsh completion for Docker.

%description -n zsh-completion-%{name} -l pl.UTF-8
Pakiet ten dostarcza uzupełnianie w zsh dla poleceń Dockera.

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
%setup -q -n moby-%{version}-ce%{?subver} -a1 -a2 -a3 -a4
mv runc-%{runc_commit}* runc
mv containerd-%{containerd_commit}* containerd
mv libnetwork-%{libnetwork_commit}* libnetwork
mv tini-* tini
%patch0 -p1

install -d vendor/src/github.com/docker
ln -s $(pwd) vendor/src/github.com/docker/docker
ln -s $(pwd)/containerd containerd/vendor/src/github.com/docker/containerd
ln -s $(pwd)/libnetwork vendor/src/github.com/docker/libnetwork

%build
v=$(awk -F= '/^RUNC_COMMIT/ {print $2}' hack/dockerfile/binaries-commits)
echo "$v" | grep "^%{runc_commit}"
v=$(awk -F= '/^CONTAINERD_COMMIT/ {print $2}' hack/dockerfile/binaries-commits)
echo "$v" | grep "^%{containerd_commit}"
v=$(awk -F= '/^LIBNETWORK_COMMIT/ {print $2}' hack/dockerfile/binaries-commits)
echo "$v" | grep "^%{libnetwork_commit}"

export GOPATH=$(pwd)/vendor:$(pwd)/containerd/vendor
export DOCKER_GITCOMMIT="pld/%{version}"
# build docker-runc
%{__make} -C runc

# build docker-containerd
%{__make} -C containerd

# build docker-proxy
go build -ldflags="-linkmode=external" \
	-o docker-proxy \
	github.com/docker/libnetwork/cmd/proxy

# build docker-init
cd tini
cmake .
%{__make}
cd ..

bash -x hack/make.sh dynbinary
%if %{with doc}
man/md2man-all.sh
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_sbindir},%{_mandir}/man1,/etc/{rc.d/init.d,sysconfig},%{systemdunitdir}} \
	$RPM_BUILD_ROOT%{_libexecdir} \
	$RPM_BUILD_ROOT/var/lib/docker/{containers,execdriver,graph,image,init,network,swarm,tmp,trust,vfs,volumes}

install -p bundles/latest/dynbinary-client/docker $RPM_BUILD_ROOT%{_bindir}/docker
install -p bundles/latest/dynbinary-daemon/dockerd $RPM_BUILD_ROOT%{_sbindir}/dockerd

# install docker-runc
install -p runc/runc $RPM_BUILD_ROOT%{_sbindir}/docker-runc

# install docker-containerd
install -p containerd/bin/containerd $RPM_BUILD_ROOT%{_sbindir}/docker-containerd
install -p containerd/bin/containerd-shim $RPM_BUILD_ROOT%{_sbindir}/docker-containerd-shim
install -p containerd/bin/ctr $RPM_BUILD_ROOT%{_sbindir}/docker-containerd-ctr

# install docker-proxy
install -p docker-proxy $RPM_BUILD_ROOT%{_sbindir}/docker-proxy

# install docker-init
install -p tini/tini $RPM_BUILD_ROOT%{_sbindir}/docker-init

cp -p contrib/init/systemd/docker.service $RPM_BUILD_ROOT%{systemdunitdir}
cp -p contrib/init/systemd/docker.socket $RPM_BUILD_ROOT%{systemdunitdir}
install -p %{SOURCE7} $RPM_BUILD_ROOT/etc/rc.d/init.d/docker
install -p %{SOURCE5} $RPM_BUILD_ROOT%{_libexecdir}/dockerd
cp -p %{SOURCE8} $RPM_BUILD_ROOT/etc/sysconfig/docker

# install udev rules
install -d $RPM_BUILD_ROOT/lib/udev/rules.d
cp -p contrib/udev/80-docker.rules $RPM_BUILD_ROOT/lib/udev/rules.d

# bash and zsh completion
install -d $RPM_BUILD_ROOT%{bash_compdir}
cp -p contrib/completion/bash/docker $RPM_BUILD_ROOT%{bash_compdir}/docker
install -d $RPM_BUILD_ROOT%{zsh_compdir}
cp -p contrib/completion/zsh/_docker $RPM_BUILD_ROOT%{zsh_compdir}

# vim syntax
%if %{with vim}
install -d $RPM_BUILD_ROOT%{_vimdatadir}
cp -a contrib/syntax/vim/* $RPM_BUILD_ROOT%{_vimdatadir}
%{__rm} $RPM_BUILD_ROOT%{_vimdatadir}/{LICENSE,README.md}
%endif

%pre
%groupadd -g 296 docker

%post
/sbin/chkconfig --add docker
%service -n docker restart
%systemd_post docker.service

%preun
if [ "$1" = "0" ]; then
	%service -q docker stop
	/sbin/chkconfig --del docker
fi
%systemd_preun docker.service

%postun
if [ "$1" = "0" ]; then
	%groupremove docker
fi
%systemd_reload

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md CHANGELOG.md CONTRIBUTING.md LICENSE AUTHORS NOTICE MAINTAINERS
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/docker
%attr(754,root,root) /etc/rc.d/init.d/docker
%attr(755,root,root) %{_bindir}/docker
%attr(755,root,root) %{_sbindir}/docker-containerd
%attr(755,root,root) %{_sbindir}/docker-containerd-ctr
%attr(755,root,root) %{_sbindir}/docker-containerd-shim
%attr(755,root,root) %{_sbindir}/docker-init
%attr(755,root,root) %{_sbindir}/docker-proxy
%attr(755,root,root) %{_sbindir}/docker-runc
%attr(755,root,root) %{_sbindir}/dockerd
%attr(755,root,root) %{_libexecdir}/dockerd
%{systemdunitdir}/docker.service
%{systemdunitdir}/docker.socket
/lib/udev/rules.d/80-docker.rules

%dir %attr(700,root,root) /var/lib/docker
%dir %attr(700,root,root) /var/lib/docker/containers
%dir %attr(700,root,root) /var/lib/docker/execdriver
%dir %attr(700,root,root) /var/lib/docker/graph
%dir %attr(700,root,root) /var/lib/docker/image
%dir %attr(700,root,root) /var/lib/docker/init
%dir %attr(700,root,root) /var/lib/docker/network
%dir %attr(700,root,root) /var/lib/docker/swarm
%dir %attr(700,root,root) /var/lib/docker/tmp
%dir %attr(700,root,root) /var/lib/docker/trust
%dir %attr(700,root,root) /var/lib/docker/vfs
%dir %attr(700,root,root) /var/lib/docker/volumes

%files -n bash-completion-%{name}
%defattr(644,root,root,755)
%{bash_compdir}/docker

%files -n zsh-completion-%{name}
%defattr(644,root,root,755)
%{zsh_compdir}/_docker

%if %{with vim}
%files -n vim-syntax-%{name}
%defattr(644,root,root,755)
%doc contrib/syntax/vim/{README.md,LICENSE}
%{_vimdatadir}/doc/dockerfile.txt
%{_vimdatadir}/ftdetect/dockerfile.vim
%{_vimdatadir}/syntax/dockerfile.vim
%endif
