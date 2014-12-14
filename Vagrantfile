# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.provision "docker"
  config.vm.provision "shell", inline: "apt-get update && apt-get install -y python-virtualenv python-pip python-dev"
end
