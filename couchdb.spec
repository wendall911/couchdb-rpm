%define couchdb_user couchdb
%define couchdb_group couchdb
%define couchdb_home %{_localstatedir}/lib/couchdb

Name:       couchdb
Version:    1.6.1
Release:    1%{?dist}
Summary:    A document database server, accessible via a RESTful JSON API

Group:      Applications/Databases
License:    ASL 2.0
URL:        http://couchdb.apache.org/
Source0:    http://www.apache.org/dist/%{name}/source/%{version}/apache-%{name}-%{version}.tar.gz
Source1:    http://www.apache.org/dist/%{name}/source/%{version}/apache-%{name}-%{version}.tar.gz.asc
Source2:    %{name}.init
Source3:    %{name}.service
Source4:    %{name}.tmpfiles.conf
Patch1:     couchdb-0001-Do-not-gzip-doc-files-and-do-not-install-installatio.patch
Patch2:     couchdb-0002-Install-docs-into-versioned-directory.patch
Patch3:     couchdb-0003-More-directories-to-search-for-place-for-init-script.patch
Patch4:     couchdb-0004-Install-into-erllibdir-by-default.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  autoconf
BuildRequires:  autoconf-archive
BuildRequires:  automake
BuildRequires:  curl-devel >= 7.18.0
BuildRequires:  erlang-asn1
BuildRequires:  erlang-erts >= R13B
# For building mochiweb
BuildRequires:  erlang-eunit
BuildRequires:  erlang-os_mon
BuildRequires:  erlang-xmerl
BuildRequires:  help2man
BuildRequires:  js-devel >= 1.8.5
BuildRequires:  libicu-devel
BuildRequires:  libtool
# For /usr/bin/prove
BuildRequires:  perl(Test::Harness)

Requires:    erlang-asn1%{?_isa}
Requires:    erlang-erts%{?_isa} >= R13B
Requires:    erlang-os_mon%{?_isa}
Requires:    erlang-xmerl%{?_isa}

#Initscripts
%if 0%{?fedora} > 16
Requires(post): systemd info
Requires(preun): systemd info
Requires(postun): systemd
%else
Requires(post): chkconfig info
Requires(preun): chkconfig initscripts info
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
%patch4 -p1 -b .install_into_erllibdir

# More verbose tests
sed -i -e "s,prove,prove -v,g" test/etap/run.tpl


%build
autoreconf -ivf
%configure --with-erlang=%{_libdir}/erlang/usr/include
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

# Install our custom couchdb initscript
%if 0%{?fedora} > 16
# Install /etc/tmpfiles.d entry
install -D -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/tmpfiles.d/%{name}.conf
# Install systemd entry
install -D -m 755 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service
rm -rf %{buildroot}/%{_sysconfdir}/rc.d/
rm -rf %{buildroot}%{_sysconfdir}/default/
%else
# Use /etc/sysconfig instead of /etc/default
mv %{buildroot}%{_sysconfdir}/{default,sysconfig}
install -D -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/%{name}
%endif

# Remove *.la files
find %{buildroot} -type f -name "*.la" -delete

# Remove generated info files
rm -f %{buildroot}%{_infodir}/dir


%check
make check


%clean
rm -rf %{buildroot}


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
    /usr/bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
%else
/sbin/chkconfig --add couchdb
%endif
/sbin/install-info %{_infodir}/CouchDB.gz %{_infodir}/dir || :


%preun
%if 0%{?fedora} > 16
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /usr/bin/systemctl --no-reload disable %{name}.service > /dev/null 2>&1 || :
    /usr/bin/systemctl stop %{name}.service > /dev/null 2>&1 || :
fi
%else
if [ $1 = 0 ] ; then
    /sbin/service couchdb stop >/dev/null 2>&1
    /sbin/chkconfig --del couchdb
fi
%endif
/sbin/install-info --delete %{_infodir}/CouchDB.gz %{_infodir}/dir || :


%postun
%if 0%{?fedora} > 16
/usr/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /usr/bin/systemctl try-restart %{name}.service >/dev/null 2>&1 || :
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
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/local.d
%dir %{_sysconfdir}/%{name}/default.d
%config(noreplace) %attr(0644, %{couchdb_user}, %{couchdb_group}) %{_sysconfdir}/%{name}/default.ini
%config(noreplace) %attr(0644, %{couchdb_user}, %{couchdb_group}) %{_sysconfdir}/%{name}/local.ini
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%if 0%{?fedora} > 16
%{_sysconfdir}/tmpfiles.d/%{name}.conf
%{_unitdir}/%{name}.service
%else
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_initrddir}/%{name}
%endif
%{_bindir}/%{name}
%{_bindir}/couch-config
%{_bindir}/couchjs
%{_libdir}/erlang/lib/couch-%{version}/
%{_libdir}/erlang/lib/couch_index-0.1/
%{_libdir}/erlang/lib/couch_mrview-0.1/
%{_libdir}/erlang/lib/couch_replicator-0.1/
%{_libdir}/erlang/lib/couch_dbupdates-0.1/
%{_libdir}/erlang/lib/couch_plugins-0.1/
%{_libdir}/erlang/lib/ejson-0.1.0/
%{_libdir}/erlang/lib/etap/
%{_libdir}/erlang/lib/erlang-oauth/
%{_libdir}/erlang/lib/ibrowse-2.2.0/
%{_libdir}/erlang/lib/mochiweb-1.4.1/
%{_libdir}/erlang/lib/snappy-1.0.5/
%{_datadir}/%{name}
%{_mandir}/man1/%{name}.1.*
%{_mandir}/man1/couchjs.1.*
%{_infodir}/CouchDB.gz
%{_datadir}/doc/%{name}-%{version}
%dir %attr(0755, %{couchdb_user}, %{couchdb_group}) %{_localstatedir}/log/%{name}
%dir %attr(0755, %{couchdb_user}, %{couchdb_group}) %{_localstatedir}/run/%{name}
%dir %attr(0755, %{couchdb_user}, %{couchdb_group}) %{_localstatedir}/lib/%{name}


%changelog
* Mon Nov 11 2014 Robert Conrad <robert.conrad@kreuzwerker.de> - 1.6.1-1
- Bump version to upstream 1.6.1 release.

* Wed May 7 2014 Wendall Cada <wendallc@83864.com> - 1.6.0-1
- Updated to version 1.6.0 release.

* Tue Apr 29 2014 Wendall Cada <wendallc@83864.com> - 1.5.1-4
- Cleanup requirements

* Thu Apr 24 2014 Wendall Cada <wendallc@83864.com> - 1.5.1-3
- Added missing dep (erlang-asn1) to build requirements.

* Thu Apr 24 2014 Wendall Cada <wendallc@83864.com> - 1.5.1-2
- Added missing dep (erlang-xmerl) to build requirements.

* Fri Apr 4 2014 Wendall Cada <wendallc@83864.com> - 1.5.1-1
- Updated to version 1.5.1 release.

* Tue Mar 25 2014 Wendall Cada <wendallc@83864.com> - 1.5.0-2
- Spec file cleanup

* Fri Jan 17 2014 Paul Mietz Egli <paul@obscure.com> - 1.5.0-1
- Updated patches and scripts to work with the CouchDb 1.5.0 release

* Wed Apr 10 2013 Wendall Cada <wendallc@83864.com> - 1.3.0-3
- File cleanup
- Added proper support for info file

* Tue Apr 9 2013 Wendall Cada <wendallc@83864.com> - 1.3.0-2
- Updated to version 1.3.0 release.
- Removed init script patch, now a part of release.
- Added bundled etap, as tests fail without it.

* Mon Mar 11 2013 Wendall Cada <wendallc@83864.com> - 1.3.0-1
- Updated to version 1.3.0.rc1
- Merged some changes from Peter Lemenkov
- Unbundle snappy

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

* Thu Mar 15 2012 Wendall Cada <wendallc@83864.com> - 1.2.0-2
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

* Tue Jun 22 2010 Peter Lemenkov <lemenkov@gmail.com> 0.11.0-1
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
