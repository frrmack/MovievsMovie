# -*- mode: ruby -*-
# vi: set ft=ruby :

# if there are any problems with these required gems, vagrant
# apparently has its own ruby environment (which makes sense). To
# install these gems (iniparse, for example), you need to run
# something like:
#
# [unix]$ vagrant package install iniparse
require 'iniparse'

Vagrant.configure("2") do |config|
  
  # preliminaries
  root_dir = File.dirname(__FILE__)
  ini = IniParse.parse( File.read(root_dir + '/config.ini') )
  
  ##################################################### RACKSPACE PROVIDER SETUP
  # global rackspace provider configuration for the vagrant-rackspace
  # extension
  rackspace_server_name = ini['servers']['rackspace']
  config.vm.provider :rackspace do |rs, override_config|
    rs.username        = ini['rackspace_cloud']['username']
    rs.api_key         = ini['rackspace_cloud']['api_key']
    rs.flavor          = /512MB/
    rs.image           = /Ubuntu 12.04/
    rs.server_name     = rackspace_server_name
    rs.rackspace_region = :ord 

    # setup passwordless ssh access to rackspace for anyone that has
    # checked out this project
    rs.public_key_path = root_dir + "/.ssh/id_rsa.pub"
    override_config.ssh.private_key_path = root_dir + "/.ssh/id_rsa"
    
    # set the vm box name for the rackspace boxes
    override_config.vm.box = "dummy"
    override_config.vm.box_url = "https://github.com/mitchellh/vagrant-rackspace/raw/master/dummy.box"
  end

  #################################################### VIRTUALBOX PROVIDER SETUP
  # global configuration on the virtualbox provider. for all available
  # options, see http://www.virtualbox.org/manual/ch08.html
  virtualbox_server_name = ini['servers']['virtualbox']
  config.vm.provider :virtualbox do |vb, override_config|
    vb.gui = false
    # http://stackoverflow.com/a/17126363/892506
    vb.customize ["modifyvm", :id, "--ioapic", "on"] 
    vb.customize ["modifyvm", :id, "--cpus", "2"]
    vb.customize ["modifyvm", :id, "--memory", "2048"]
    override_config.vm.box = "precise32"
    override_config.vm.box_url = "http://files.vagrantup.com/precise32.box"
    override_config.vm.network :forwarded_port, guest: 8000, host: 8000
    override_config.vm.network :forwarded_port, guest: 80, host: 8080
  end
 
  ################################################################# LOCAL SERVER
  config.vm.define virtualbox_server_name do |server_config|
    server_config.vm.hostname = virtualbox_server_name
  end

  ############################################################# RACKSPACE SERVER
  config.vm.define rackspace_server_name do |server_config|
    server_config.vm.hostname = rackspace_server_name
  end

end
