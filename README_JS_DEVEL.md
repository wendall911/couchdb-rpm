1. yum install autoconf213 gcc gcc-c++ make nspr-devel python zip readline-devel ncurses-devel rpmlib pkgconfig

2. Download lastest SRPM from Fedora project [Fedora 16 Source RPMS](http://infrastructure.fedoraproject.org/repo/pub/fedora/linux/releases/16/Fedora/source/SRPMS/) [SRPM](http://infrastructure.fedoraproject.org/repo/pub/fedora/linux/releases/16/Fedora/source/SRPMS/js-1.8.5-7.fc16.src.rpm)

3. If not already installed, install and configure system for building rpms. [Instructions](http://wiki.centos.org/HowTos/SetupRpmBuildEnvironment)

4. Unpack source rpm: rpm2cpio js-1.8.5-7.fc16.src.rpm | cpio -idmv

5. Move .spec file to ~/rpmbuild/SPECS

6. Move all other files to ~/rpmbuild/SOURCES

7. cd ~/rpmbuild/SPECS

8. rpmbuild -ba js.spec

9. sudo rpm {-ihv | -U} ~/rpmbuild/RPMS/i386/js-devel-1.8.5-7.el6.i386.rpm
