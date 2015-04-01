# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "chef/centos-6.5"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  config.vm.provision "shell", inline: <<-SHELL
    sudo rpm -i http://linux.mirrors.es.net/fedora-epel/6/x86_64/epel-release-6-8.noarch.rpm
    sudo yum update -y
    sudo yum install -y rpm-build redhat-rpm-config spectool git autoconf gcc-c++ js js-devel
    mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
    echo '%_topdir %(echo $HOME)/rpmbuild' > ~/.rpmmacros
    cp /vagrant/{*.cfg,*.patch,*.spec,*.init,*.service,*.conf} ~/rpmbuild/SOURCES
    sudo yum install -y yum-utils --enablerepo=extras
    git clone https://github.com/meltwater/autoconf-archive-rpm.git
    cd autoconf-archive-rpm
    spectool -g -R -C SOURCES autoconf-archive.spec
    rpmbuild --define "_topdir `pwd`" -bs autoconf-archive.spec
    sudo yum-builddep SRPMS/autoconf-archive-*.src.rpm
    rpmbuild --define "_topdir `pwd`" --rebuild SRPMS/autoconf-archive-*.src.rpm
    sudo rpm -i RPMS/noarch/*.rpm
    cd .. && rm -rf autoconf-archive-rpm
    cd ~/rpmbuild && spectool -g -R SOURCES/couchdb.spec
    rpmbuild -bs SOURCES/couchdb.spec
    sudo yum-builddep -y SRPMS/couchdb-*.src.rpm
    rpmbuild --rebuild SRPMS/couchdb-*.src.rpm
    cp ~/rpmbuild/RPMS/x86_64/*.rpm /vagrant
  SHELL
end
