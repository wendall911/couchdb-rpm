%define couchdb_user couchdb
%define couchdb_group couchdb
%define couchdb_home %{_localstatedir}/lib/couchdb

Name:       couchdb
Version:    1.2.1
Release:    1%{?dist}
Summary:    A document database server, accessible via a RESTful JSON API

Group:      Applications/Databases
License:    ASL 2.0
URL:        http://couchdb.apache.org/
Source0:    http://www.apache.org/dist/%{name}/%{version}/apache-%{name}-%{version}.tar.gz
Source1:    %{name}.init
Source2:    %{name}.service
Source3:	%{name}.tmpfiles.conf
Patch1:		couchdb-0001-Do-not-gzip-doc-files-and-do-not-install-installatio.patch
Patch2:		couchdb-0002-Install-docs-into-versioned-directory.patch
Patch3:		couchdb-0003-More-directories-to-search-for-place-for-init-script.patch
Patch4:		couchdb-0004-Install-into-erllibdir-by-default.patch
Patch5:		couchdb-0005-Don-t-use-bundled-etap-erlang-oauth-ibrowse-and-moch.patch
Patch6:		couchdb-0006-Fixes-for-system-wide-ibrowse.patch
Patch7:		couchdb-0007-wait-for-couch-stop.patch

BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:	curl-devel
BuildRequires:	erlang-erts
BuildRequires:	erlang-etap
BuildRequires:	erlang-ibrowse >= 2.2.0
BuildRequires:	erlang-mochiweb
BuildRequires:	erlang-oauth
BuildRequires:	erlang-os_mon
BuildRequires:	help2man
BuildRequires:	js-devel >= 1.8.5
BuildRequires:	libicu-devel
# For /usr/bin/prove
BuildRequires:	perl(Test::Harness)

Requires:	erlang-crypto
Requires:	erlang-erts
Requires:	erlang-ibrowse >= 2.2.0
Requires:	erlang-inets
Requires:	erlang-kernel
Requires:	erlang-mochiweb
Requires:	erlang-oauth
Requires:	erlang-sasl
Requires:	erlang-stdlib
Requires:	erlang-tools
Requires:   erlang-os_mon

#Initscripts
%if 0%{?fc17}%{?fc18}
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%else
Requires(post): chkconfig
Requires(preun): chkconfig initscripts
%endif

# Users and groups
Requires(pre): shadow-utils


%description
Apache CouchDB is a distributed, fault-tolerant and schema-free
document-oriented database accessible via a RESTful HTTP/JSON API.
Among other features, it provides robust, incremental replication
with bi-directional conflict detection and resolution, and is
queryable and indexable using a table-oriented view engine with
JavaScript acting as the default view definition language.


%prep
%setup -q -n apache-%{name}-%{version}
%patch1 -p1 -b .dont_gzip
%patch2 -p1 -b .use_versioned_docdir
%patch3 -p1 -b .more_init_dirs
%patch4 -p1 -b .install_into_erldir
%patch5 -p1 -b .remove_bundled_libs
%patch6 -p1 -b .workaround_for_system_wide_ibrowse
%patch7 -p1 -b .remove_pid_file

# Remove bundled libraries
rm -rf src/erlang-oauth
rm -rf src/etap
rm -rf src/ibrowse
rm -rf src/mochiweb

%build
#./bootstrap
autoreconf -ivf


%configure \
    --with-erlang=%{_libdir}/erlang/usr/include/ \
    --libdir=%{_libdir} \

make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# Install our custom couchdb initscript
%if 0%{?fedora} > 16
install -D -m 755 %{SOURCE2} $RPM_BUILD_ROOT%{_unitdir}/%{name}.service
rm -rf $RPM_BUILD_ROOT/%{_sysconfdir}/rc.d/
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/default/
%else
# Use /etc/sysconfig instead of /etc/default
mv $RPM_BUILD_ROOT%{_sysconfdir}/{default,sysconfig}
install -D -m 755 %{SOURCE1} $RPM_BUILD_ROOT%{_initrddir}/%{name}
%endif

# Install /etc/tmpfiles.d entry
%if 0%{?fedora} > 14
install -D -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d/%{name}.conf
%endif


%check
make check || exit 1


%clean
rm -rf $RPM_BUILD_ROOT


%pre
getent group %{couchdb_group} >/dev/null || groupadd -r %{couchdb_group}
getent passwd %{couchdb_user} >/dev/null || \
useradd -r -g %{couchdb_group} -d %{couchdb_home} -s /bin/bash \
-c "Couchdb Database Server" %{couchdb_user}
exit 0


%post
%if 0%{?fedora} > 16
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
%else
/sbin/chkconfig --add couchdb
%endif


%preun
%if 0%{?fedora} > 16
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable couchdb.service > /dev/null 2>&1 || :
    /bin/systemctl stop couchdb.service > /dev/null 2>&1 || :
fi
%else
if [ $1 = 0 ] ; then
    /sbin/service couchdb stop >/dev/null 2>&1
    /sbin/chkconfig --del couchdb
fi
%endif


%postun
%if 0%{?fedora} > 16
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart couchdb.service >/dev/null 2>&1 || :
fi
%endif


%if 0%{?fedora} > 16
%triggerun -- couchdb < 1.0.3-5
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply httpd
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save couchdb >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del couchdb >/dev/null 2>&1 || :
/bin/systemctl try-restart couchdb.service >/dev/null 2>&1 || :
%endif


%files
%defattr(-,root,root,-)
%doc AUTHORS BUGS CHANGES LICENSE NEWS NOTICE README THANKS
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/local.d
%dir %{_sysconfdir}/%{name}/default.d
%config(noreplace) %attr(0644, %{couchdb_user}, root) %{_sysconfdir}/%{name}/default.ini
%config(noreplace) %attr(0644, %{couchdb_user}, root) %{_sysconfdir}/%{name}/local.ini
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%if 0%{?fedora} > 14
%{_sysconfdir}/tmpfiles.d/%{name}.conf
%endif
%if 0%{?fedora} > 16
%{_unitdir}/%{name}.service
%else
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_initrddir}/%{name}
%endif
%{_bindir}/%{name}
%{_bindir}/couchjs
%{_bindir}/couch-config
%{_libdir}/erlang/lib/couch-%{version}
%{_libdir}/erlang/lib/snappy-1.0.3
%{_libdir}/erlang/lib/ejson-0.1.0
%{_datadir}/%{name}
%{_mandir}/man1/%{name}.1.*
%{_mandir}/man1/couchjs.1.*
%dir %attr(0755, %{couchdb_user}, root) %{_localstatedir}/log/%{name}
%dir %attr(0755, %{couchdb_user}, root) %{_localstatedir}/run/%{name}
%dir %attr(0755, %{couchdb_user}, root) %{_localstatedir}/lib/%{name}


%changelog
* Wed Jan 2 2013 Wendall Cada <wendallc@83864.com> - 1.2.1-1
- Updated version to 1.2.1

* Tue Aug 28 2012 Wendall Cada <wendallc@83864.com> - 1.2.0-8
- Merged Peter Lemenkov's systemd support.

* Mon Apr 2 2012 Wendall Cada <wendallc@83864.com> - 1.2.0-7
- Added erlang-os_mon as a dependency
- Added timeout to wait for stop patch.

* Mon Apr 2 2012 Wendall Cada <wendallc@83864.com> - 1.2.0-6
- Updated for release artifact e736fa9e314034e2603ac5861692ddeab92f1dad

* Tue Mar 27 2012 Wendall Cada <wendallc@83864.com> - 1.2.0-5
- Removed patch that forces removal of PID file.
- Added patch to wait until couchdb actually exits before returning success.

* Sat Mar 24 2012 Wendall Cada <wendallc@83864.com> - 1.2.0-4
- Added support for fc17/18
- Added run dir to tmpfiles.d for fc15+ so run dir persists between reboots.
- Update for 1.2.0 release, third round based on 654768

* Wed Mar 21 2012 Wendall Cada <wendallc@83864.com> - 1.2.0-3 
- New version based on cd238b42d13

* Wed Mar 15 2012 Wendall Cada <wendallc@83864.com> - 1.2.0-2 
- Removed spidermonkey configuration patch (Fixed)
- Removed etap patch (Fixed)
- Removed spidermonkey configuration flags not required with new configure

* Wed Mar 7 2012 Wendall Cada <wendallc@83864.com> - 1.2.0-1
- Removed support for EL-5/Centos-5 This will not happen without serious work, as-in not worth my time and effort.
- Removed ibrowse patch
- Updated system wide ibrowse patch
- Removed spidermonkey 1.8.5 patches
- Removed patch that sets COUCHDB_RESPAWN_TIMEOUT to 0, as it is not covered in the bugzilla report and I am removing it as a typo or mistake, or an undocumented whatever.

* Tue Jul 12 2011 Peter Lemenkov <lemenkov@gmail.com> - 1.0.2-8
- Build for EL-5 (see patch99 - quite ugly, I know)

* Sat Jun 18 2011 Peter Lemenkov <lemenkov@gmail.com> - 1.0.2-7
- Requires ibrowse >= 2.2.0 for building
- Fixes for /var/run mounted as tmpfs (see rhbz #656565, #712681)

* Mon May 30 2011 Peter Lemenkov <lemenkov@gmail.com> - 1.0.2-6
- Patched patch for new js-1.8.5

* Fri May 20 2011 Peter Lemenkov <lemenkov@gmail.com> - 1.0.2-5
- Fixed issue with ibrowse-2.2.0

* Thu May 19 2011 Peter Lemenkov <lemenkov@gmail.com> - 1.0.2-4
- Fixed issue with R14B02

* Thu May  5 2011 Jan Horak <jhorak@redhat.com> - 1.0.2-3
- Added Spidermonkey 1.8.5 patch

* Mon Mar 07 2011 Caolán McNamara <caolanm@redhat.com> 1.0.2-2
- rebuild for icu 4.6

* Thu Nov 25 2010 Peter Lemenkov <lemenkov@gmail.com> 1.0.2-1
- Ver. 1.0.2
- Patches were rebased

* Tue Oct 12 2010 Peter Lemenkov <lemenkov@gmail.com> 1.0.1-4
- Added patches for compatibility with R12B5

* Mon Oct 11 2010 Peter Lemenkov <lemenkov@gmail.com> 1.0.1-3
- Narrowed list of BuildRequires

* Thu Aug 26 2010 Peter Lemenkov <lemenkov@gmail.com> 1.0.1-2
- Cleaned up spec-file a bit

* Fri Aug  6 2010 Peter Lemenkov <lemenkov@gmail.com> 1.0.1-1
- Ver. 1.0.1

* Thu Jul 15 2010 Peter Lemenkov <lemenkov@gmail.com> 1.0.0-1
- Ver. 1.0.0

* Wed Jul 14 2010 Peter Lemenkov <lemenkov@gmail.com> 0.11.1-1
- Ver. 0.11.1
- Removed patch for compatibility with Erlang/OTP R14A (merged upstream)

* Sun Jul 11 2010 Peter Lemenkov <lemenkov@gmail.com> 0.11.0-3
- Compatibility with Erlang R14A (see patch9)

* Tue Jun 22 2010 Peter Lemenkov <lemenkov@gmail.com> 0.11.0-2
- Massive spec cleanup

* Tue Jun 18 2010 Peter Lemenkov <lemenkov@gmail.com> 0.11.0-1
- Ver. 0.11.0 (a feature-freeze release candidate)

* Fri Jun 18 2010 Peter Lemenkov <lemenkov@gmail.com> 0.10.2-13
- Remove ldconfig invocation (no system-wide shared libraries)
- Removed icu-config requires

* Tue Jun 15 2010 Peter Lemenkov <lemenkov@gmail.com> 0.10.2-12
- Narrow explicit requires

* Tue Jun  8 2010 Peter Lemenkov <lemenkov@gmail.com> 0.10.2-11
- Remove bundled ibrowse library (see rhbz #581282).

* Mon Jun  7 2010 Peter Lemenkov <lemenkov@gmail.com> 0.10.2-10
- Use system-wide erlang-mochiweb instead of bundled copy (rhbz #581284)
- Added %%check target and necessary BuildRequires - etap, oauth, mochiweb

* Wed Jun  2 2010 Peter Lemenkov <lemenkov@gmail.com> 0.10.2-9
- Remove pid-file after stopping CouchDB

* Tue Jun  1 2010 Peter Lemenkov <lemenkov@gmail.com> 0.10.2-8
- Suppress unneeded message while stopping CouchDB via init-script

* Mon May 31 2010 Peter Lemenkov <lemenkov@gmail.com> 0.10.2-7
- Do not manually remove pid-file while stopping CouchDB

* Mon May 31 2010 Peter Lemenkov <lemenkov@gmail.com> 0.10.2-6
- Fix 'stop' and 'status' targets in the init-script (see rhbz #591026)

* Thu May 27 2010 Peter Lemenkov <lemenkov@gmail.com> 0.10.2-5
- Use system-wide erlang-etap instead of bundled copy (rhbz #581281)

* Fri May 14 2010 Peter Lemenkov <lemenkov@gmail.com> 0.10.2-4
- Use system-wide erlang-oauth instead of bundled copy (rhbz #581283)

* Thu May 13 2010 Peter Lemenkov <lemenkov@gmail.com> 0.10.2-3
- Fixed init-script to use /etc/sysconfig/couchdb values (see rhbz #583004)
- Fixed installation location of beam-files (moved to erlang directory)

* Fri May  7 2010 Peter Lemenkov <lemenkov@gmail.com> 0.10.2-2
- Remove useless BuildRequires

* Fri May  7 2010 Peter Lemenkov <lemenkov@gmail.com> 0.10.2-1
- Update to 0.10.2 (resolves rhbz #578580 and #572176)
- Fixed chkconfig priority (see rhbz #579568)

* Fri Apr 02 2010 Caolán McNamara <caolanm@redhat.com> 0.10.0-3
- rebuild for icu 4.4

* Thu Oct 15 2009 Allisson Azevedo <allisson@gmail.com> 0.10.0-2
- Added patch to force init_enabled=true in configure.ac.

* Thu Oct 15 2009 Allisson Azevedo <allisson@gmail.com> 0.10.0-1
- Update to 0.10.0.

* Sun Oct 04 2009 Rahul Sundaram <sundaram@fedoraproject.org> 0.9.1-2
- Change url. Fixes rhbz#525949

* Thu Jul 30 2009 Allisson Azevedo <allisson@gmail.com> 0.9.1-1
- Update to 0.9.1.
- Drop couchdb-0.9.0-pid.patch.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Apr 21 2009 Allisson Azevedo <allisson@gmail.com> 0.9.0-2
- Fix permission for ini files.
- Fix couchdb.init start process.

* Tue Apr 21 2009 Allisson Azevedo <allisson@gmail.com> 0.9.0-1
- Update to 0.9.0.

* Tue Nov 25 2008 Allisson Azevedo <allisson@gmail.com> 0.8.1-4
- Use /etc/sysconfig for settings.

* Tue Nov 25 2008 Allisson Azevedo <allisson@gmail.com> 0.8.1-3
- Fix couchdb_home.
- Added libicu-devel for requires.

* Tue Nov 25 2008 Allisson Azevedo <allisson@gmail.com> 0.8.1-2
- Fix spec issues.

* Tue Nov 25 2008 Allisson Azevedo <allisson@gmail.com> 0.8.1-1
- Initial RPM release
