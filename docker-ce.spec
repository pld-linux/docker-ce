#
# Conditional build:
%bcond_with	tests		# build without tests
%bcond_with	vim			# build vim syntax package (bundled in vim 7.4.979-2)
%bcond_with	doc			# build manual pages

# TODO: drop P docker when docker-compose updated to use docker(engine) dep

# NOTES
# - https://github.com/docker/docker-ce/releases
# - https://github.com/moby/moby/blob/master/project/PACKAGERS.md#build-dependencies

# v1.0.0-rc10
%define	runc_commit dc9208a
# v1.2.13
%define	containerd_commit 7ad1843
# v0.8.0-dev.2-1075-g1b91bc94
%define	libnetwork_commit 153d076
#define	subver -rc2
Summary:	Docker CE: the open-source application container engine
Name:		docker-ce
# Using Docker-CE, Stay on Stable channel
# https://docs.docker.com/engine/installation/
Version:	19.03.11
Release:	1
License:	Apache v2.0
Group:		Applications/System
# https://github.com/docker/docker-ce/releases
#Source0:	https://github.com/docker/docker-ce/archive/v%{version}-ce%{subver}/%{name}-%{version}-ce%{subver}.tar.gz
Source0:	https://github.com/docker/docker-ce/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	4af9c11658e8a9f11dd10d3a83c5c3fb
Source1:	https://github.com/opencontainers/runc/archive/%{runc_commit}/runc-%{runc_commit}.tar.gz
# Source1-md5:	b593d63c7df5a27fba615afcf411762f
Source2:	https://github.com/containerd/containerd/archive/%{containerd_commit}/containerd-%{containerd_commit}.tar.gz
# Source2-md5:	82af4401bdae0f3f39f8a4307e70f9f4
Source3:	https://github.com/docker/libnetwork/archive/%{libnetwork_commit}/libnetwork-%{libnetwork_commit}.tar.gz
# Source3-md5:	4489650d655a82d623a4be5e079fc04e
Source4:	https://github.com/krallin/tini/archive/v0.18.0/tini-0.18.0.tar.gz
# Source4-md5:	cc3b205a1b83b8e6ed6892fc5e8ef2c3
Source5:	dockerd.sh
Source7:	docker.init
Source8:	docker.sysconfig
Patch0:		systemd.patch
URL:		https://www.docker.com/community-edition/
BuildRequires:	btrfs-progs-devel >= 3.16.1
BuildRequires:	cmake
BuildRequires:	device-mapper-devel >= 2.02.89
BuildRequires:	golang >= 1.12
BuildRequires:	libseccomp-devel >= 2.3
BuildRequires:	rpmbuild(macros) >= 1.644
BuildRequires:	sqlite3-devel >= 3.7.9
BuildRequires:	xxd
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
Provides:	docker = %{version}
Provides:	docker(engine) = %{version}
Provides:	group(docker)
Requires:	libseccomp >= 2.3
Obsoletes:	docker < 18.0
Obsoletes:	lxc-docker < 1.1.1
# only runs on x64 hosts for now:
# https://github.com/docker/docker/issues/136
# https://github.com/docker/docker/issues/611
ExclusiveArch:	%{x8664} aarch64
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
%setup -q -n %{name}-%{version}%{?subver} -a1 -a2 -a3 -a4

mv runc-%{runc_commit}* runc
mv runc/vendor runc/src
ln -s ../../.. runc/src/github.com/opencontainers/runc

mv containerd-%{containerd_commit}* containerd
mv containerd/vendor containerd/src
ln -s ../../.. containerd/src/github.com/containerd/containerd

mv libnetwork-%{libnetwork_commit}* libnetwork
install -d libnetwork/gopath
mv libnetwork/vendor libnetwork/gopath/src
ln -s ../../../.. libnetwork/gopath/src/github.com/docker/libnetwork

mv tini-* tini

install -d components/cli/.gopath/src/github.com/docker
ln -s ../../../.. components/cli/.gopath/src/github.com/docker/cli

%patch0 -p1 -d components/engine

%build
grep -rhE "=%{runc_commit}|=%{containerd_commit}|=%{libnetwork_commit}" $(pwd)/components/engine/hack/dockerfile/install/

export VERSION=%{version}-ce # for `docker version`
export GITCOMMIT="PLD-Linux/%{version}" # for cli
export DOCKER_GITCOMMIT="PLD-Linux/%{version}" # for engine

# build runc
sed -i -e 's,shell git,shell false,' runc/Makefile
GOPATH=$(pwd)/runc \
%{__make} -C runc \
	COMMIT=$RUNC_COMMIT
./runc/runc -v

# build containerd
GOPATH=$(pwd)/containerd \
%{__make} -C containerd \
	GIT_COMMIT=$CONTAINERD_COMMIT

# build docker-proxy
cd libnetwork
GOPATH=$(pwd)/gopath \
go build -ldflags="-linkmode=external" \
	-o docker-proxy \
	github.com/docker/libnetwork/cmd/proxy
cd ..

# build docker-init
cd tini
cmake .
%{__make}

# docker cli
cd ../components/cli
GOPATH=$(pwd)/.gopath \
DISABLE_WARN_OUTSIDE_CONTAINER=1 \
%{__make} dynbinary
./build/docker -v

cd ../engine
AUTO_GOPATH=1 \
bash -x hack/make.sh dynbinary
./bundles/dynbinary-daemon/dockerd -v
%if %{with doc}
man/md2man-all.sh
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_sbindir},%{_mandir}/man1,/etc/{rc.d/init.d,sysconfig},%{systemdunitdir}} \
	$RPM_BUILD_ROOT%{_libexecdir} \
	$RPM_BUILD_ROOT/var/lib/docker/{containers,execdriver,graph,image,init,network,swarm,tmp,trust,vfs,volumes}

# docker-cli
install -p components/cli/build/docker $RPM_BUILD_ROOT%{_bindir}/docker

# runc
install -p runc/runc $RPM_BUILD_ROOT%{_sbindir}/runc

# containerd
install -p containerd/bin/containerd $RPM_BUILD_ROOT%{_sbindir}/containerd
install -p containerd/bin/containerd-shim $RPM_BUILD_ROOT%{_sbindir}/containerd-shim
install -p containerd/bin/ctr $RPM_BUILD_ROOT%{_sbindir}/ctr

# docker-proxy
install -p libnetwork/docker-proxy $RPM_BUILD_ROOT%{_sbindir}/docker-proxy

# docker-init
install -p tini/tini $RPM_BUILD_ROOT%{_sbindir}/docker-init

# dockerd
cd components/engine
install -p bundles/dynbinary-daemon/dockerd $RPM_BUILD_ROOT%{_sbindir}/dockerd
cp -p contrib/init/systemd/docker.service $RPM_BUILD_ROOT%{systemdunitdir}
cp -p contrib/init/systemd/docker.socket $RPM_BUILD_ROOT%{systemdunitdir}
install -p %{SOURCE7} $RPM_BUILD_ROOT/etc/rc.d/init.d/docker
install -p %{SOURCE5} $RPM_BUILD_ROOT%{_libexecdir}/dockerd
cp -p %{SOURCE8} $RPM_BUILD_ROOT/etc/sysconfig/docker

# install udev rules
install -d $RPM_BUILD_ROOT/lib/udev/rules.d
cp -p contrib/udev/80-docker.rules $RPM_BUILD_ROOT/lib/udev/rules.d

# vim syntax
%if %{with vim}
install -d $RPM_BUILD_ROOT%{_vimdatadir}
cp -a contrib/syntax/vim/* $RPM_BUILD_ROOT%{_vimdatadir}
%{__rm} $RPM_BUILD_ROOT%{_vimdatadir}/{LICENSE,README.md}
%endif

# bash and zsh completion
cd ../cli/contrib/completion
install -d $RPM_BUILD_ROOT%{bash_compdir}
cp -p bash/docker $RPM_BUILD_ROOT%{bash_compdir}
install -d $RPM_BUILD_ROOT%{zsh_compdir}
cp -p zsh/_docker $RPM_BUILD_ROOT%{zsh_compdir}

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

%triggerun -- docker < 17.0
# Prevent preun from docker from working
chmod a-x /etc/rc.d/init.d/docker

%triggerpostun -- docker < 17.0
# Restore what triggerun removed
chmod 754 /etc/rc.d/init.d/docker
# reinstall docker init.d links, which could be different
/sbin/chkconfig --del docker
/sbin/chkconfig --add docker

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc components/engine/{README.md,CHANGELOG.md,CONTRIBUTING.md,LICENSE,AUTHORS,NOTICE,MAINTAINERS}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/docker
%attr(754,root,root) /etc/rc.d/init.d/docker
%attr(755,root,root) %{_bindir}/docker
%attr(755,root,root) %{_sbindir}/containerd
%attr(755,root,root) %{_sbindir}/ctr
%attr(755,root,root) %{_sbindir}/containerd-shim
%attr(755,root,root) %{_sbindir}/docker-init
%attr(755,root,root) %{_sbindir}/docker-proxy
%attr(755,root,root) %{_sbindir}/runc
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
%doc components/engine/contrib/syntax/vim/{README.md,LICENSE}
%{_vimdatadir}/doc/dockerfile.txt
%{_vimdatadir}/ftdetect/dockerfile.vim
%{_vimdatadir}/syntax/dockerfile.vim
%endif
