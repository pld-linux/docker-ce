Summary:	Docker CE: the open-source application container engine
Name:		docker-ce
Version:	27.3.1
Release:	1
License:	Apache v2.0
Group:		Applications/System
# https://github.com/moby/moby/releases
Source0:	https://github.com/moby/moby/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	cb21a843d1fc89c5707a3d4790d1a27e
Source1:	dockerd.sh
Source2:	docker.init
Source3:	docker.sysconfig
Patch0:		systemd.patch
URL:		https://www.docker.com/
BuildRequires:	golang >= 1.21
BuildRequires:	linux-libc-headers >= 7:4.12
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 2.009
BuildRequires:	systemd-devel
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires:	ca-certificates
Requires:	containerd >= 1.6.22
Requires:	iproute2 >= 3.5
Requires:	iptables >= 1.4
Requires:	procps
Requires:	rc-scripts >= 0.4.0.10
Requires:	systemd-units >= 38
Requires:	tini
Requires:	uname(release) >= 3.8
Suggests:	docker-ce-cli
Suggests:	pigz
Suggests:	xfsprogs
Suggests:	xz >= 1:4.9
Suggests:	zfs
Provides:	docker = %{version}
Provides:	docker(engine) = %{version}
Provides:	group(docker)
Obsoletes:	docker < 18.0
Obsoletes:	lxc-docker < 1.1.1
ExclusiveArch:	%go_arches
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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

%prep
%setup -q -n moby-%{version}
%patch -P0 -p1

%build
export VERSION=%{version}
export DOCKER_GITCOMMIT="PLD-Linux/%{version}"
export GO111MODULE=off

AUTO_GOPATH=1 \
bash -x hack/make.sh dynbinary
./bundles/dynbinary-daemon/dockerd -v

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_sbindir},%{_mandir}/man1,/etc/{rc.d/init.d,sysconfig},%{systemdunitdir}} \
	$RPM_BUILD_ROOT%{_sysconfdir}/docker \
	$RPM_BUILD_ROOT%{_libexecdir} \
	$RPM_BUILD_ROOT/var/lib/docker/{containers,execdriver,graph,image,init,network,swarm,tmp,trust,vfs,volumes}

install -p bundles/dynbinary-daemon/docker-proxy $RPM_BUILD_ROOT%{_sbindir}/docker-proxy
install -p bundles/dynbinary-daemon/dockerd $RPM_BUILD_ROOT%{_sbindir}/dockerd
%{__ln_s} /sbin/tini $RPM_BUILD_ROOT%{_sbindir}/docker-init
cp -p contrib/init/systemd/docker.service $RPM_BUILD_ROOT%{systemdunitdir}
cp -p contrib/init/systemd/docker.socket $RPM_BUILD_ROOT%{systemdunitdir}
install -p %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/docker
install -p %{SOURCE1} $RPM_BUILD_ROOT%{_libexecdir}/dockerd
cp -p %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/docker

# install udev rules
install -d $RPM_BUILD_ROOT/lib/udev/rules.d
cp -p contrib/udev/80-docker.rules $RPM_BUILD_ROOT/lib/udev/rules.d

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
%doc README.md CONTRIBUTING.md LICENSE AUTHORS NOTICE MAINTAINERS
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/docker
%attr(754,root,root) /etc/rc.d/init.d/docker
%dir %{_sysconfdir}/docker
%attr(755,root,root) %{_sbindir}/docker-init
%attr(755,root,root) %{_sbindir}/docker-proxy
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
