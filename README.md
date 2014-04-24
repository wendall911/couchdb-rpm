# Creating RPM Packages for Fedora 16+ / Centos 6+
You might be able to get these specs working on ancient versions of <= Centos 5 / <= RHEL 5/ <= Fedora 15, but it is a royal pain, and requires some crazy patching to do so. It is practical to use a more current distribution release. Please don't send me patches or requests for those older OS. They won't get accepted.

These are written and tested against couchdb-1.2.0+

## Building with rpmbuild on host OS

### Fedora Step 1
* Setup rpmbuild
  * [Instructions](https://fedoraproject.org/wiki/How_to_create_an_RPM_package)

### Centos Step 1
* Configure [EPEL](http://fedoraproject.org/wiki/EPEL)
  * Download latest version of epel-release [epel-release](http://linux.mirrors.es.net/fedora-epel/6/i386/repoview/epel-release.html)
  * rpm -ihv epel-release-{version}.noarch.rpm
* Setup rpmbuild
  * [Instructions](http://wiki.centos.org/HowTos/SetupRpmBuildEnvironment)
* If you want a ~4X faster couchdb replace js-devel-1.7, build and install working js-devel-1.8.5
  * [js185](https://github.com/wendall911/js185)
* Install js and js-devel rpms from step above or continue

### Fedora/Centos Step 2
* Copy contents of repo to ~/rpmbuild/SOURCES
* Fetch sources
  * spectool -g -R couchdb.spec
* Build SRPM
  * rpmbuild -bs couchdb.spec
* Install dependencies
  * sudo yum-builddep ~/rpmbuild/SRPMS/couchdb-{version}.{release}.src.rpm
* rpmbuild --rebuild ~/rpmbuild/SRPMS/couchdb-{version}.{release}.src.rpm

## Building rpm using mock
* Install mock
  * [Notes on mock usage](https://fedoraproject.org/wiki/Using_Mock_to_test_package_builds)
* Checkout this repo. All commands from within this repo.
* CentOS build
  * copy centos-6-i386.cfg and centos-6-x86_64.cfg to /etc/mock/
* Fetch sources
  * spectool -g -R -C ./ couchdb.spec
* Build SRPM
  * sudo mock -r centos-6-x86_64 --buildsrpm --sources ./ --spec ./couchdb.spec
* Copy generated SRPM to working directory
  * cp /var/lib/mock/centos-6-x86_64/result/couchdb-1.3.0-3.el6.src.rpm ./
* Install dependencies
  * sudo mock -r centos-6-x86_64 --installdeps couchdb-1.3.0-3.el6.src.rpm
* Build RPM
  * sudo mock -r centos-6-x86_64 rebuild couchdb-1.3.0-3.el6.src.rpm
* Copy built RPMS to working directory
  * cp /var/lib/mock/centos-6-x86_64/result/\*.rpm ./

## Prerelease Notes
* Checkout couchdb from https://git-wip-us.apache.org/repos/asf/couchdb.git
* Create an archive from a release tag or repo revision: git archive --format=tar --prefix=apache-couchdb-1.2.0/ fb72251bc | gzip >apache-couchdb-1.2.0.tar.gz
* Comment out "autoreconf -ivf" and uncomment './bootstrap' as configure doesn't exist in git repo and needs bootstrapped

## Other
* Please take a look at https://github.com/iriscouch/build-couchdb for ability to build against specific erlang and spidermonkey versions.
* Drop by irc.freenode.net #couchdb if you have any questions.
