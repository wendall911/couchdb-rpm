# Build current js-devel for CentOS

## Building on Host OS
* If not already installed, install and configure system for building rpms. [Instructions](http://wiki.centos.org/HowTos/SetupRpmBuildEnvironment)
* Download a recent SRPM from Fedora project
  * [Fedora 20 Source RPMS](http://infrastructure.fedoraproject.org/repo/pub/fedora/linux/releases/20/Fedora/source/SRPMS/) [SRPM](http://infrastructure.fedoraproject.org/repo/pub/fedora/linux/releases/20/Fedora/source/SRPMS/j/js-1.8.5-14.fc20.src.rpm)
* Install dependencies
  * sudo yum-builddep js-1.8.5-14.fc20.src.rpm
* Rebuild rpm
  * rpmbuild --rebuild js-1.8.5-14.fc20.src.rpm
* Install rpm
  * sudo rpm {-ihv | -U} ~/rpmbuild/RPMS/i386/js-devel-1.8.5-14.el6.i386.rpm

## Building Using Mock
* Install mock
  * [Notes on mock usage](https://fedoraproject.org/wiki/Using_Mock_to_test_package_builds)
* Checkout js sources from Fedora Project
  * git clone git://pkgs.fedoraproject.org/js.git
* Fetch sources
  * spectool -g -R -C ./ js.spec
* Build SRPM
  * sudo mock -r epel-6-x86_64 --buildsrpm --sources ./ --spec ./js.spec
* Copy generated SRPM to working directory
  * cp /var/lib/mock/epel-6-x86_64/result/js-1.8.5-14.el6.src.rpm ./
* Install dependencies
  * sudo mock -r epel-6-x86_64 --installdeps js-1.8.5-14.el6.src.rpm
* Build RPM
  * sudo mock -r epel-6-x86_64 rebuild js-1.8.5-14.el6.src.rpm
* Copy built RPMS to working directory
  * cp /var/lib/mock/epel-6-x86_64/result/js-devel-1.8.5-14.el6.x86_64.rpm ./
  * cp /var/lib/mock/epel-6-x86_64/result/js-debuginfo-1.8.5-14.el6.x86_64.rpm ./
  * cp /var/lib/mock/epel-6-x86_64/result/js-1.8.5-14.el6.x86_64.rpm ./
* Install js RPMS into chroot environment
  * sudo mock -r epel-6-x86_64 --install js-1.8.5-14.el6.x86_64.rpm
  * sudo mock -r epel-6-x86_64 --install js-devel-1.8.5-14.el6.x86_64.rpm

## Target Server Installation
* Install js RPM
  * rpm -ihv js-1.8.5-14.el6.x86_64.rpm
