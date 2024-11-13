# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure("2") do |config|

    $password_script = <<-EOF
    apt -q -y update
    apt -q -y install -y openssh-server
    useradd -m -s /bin/bash mla
    echo -e "password_mla\npassword_mla" | passwd mla
    usermod -aG sudo mla
    EOF
  
    $ssh_script = <<-EOF
    mkdir -p /home/mla/.ssh
    mv /tmp/mla_key.pub /home/mla/.ssh/mla_key.pub
    cat /home/mla/.ssh/mla_key.pub >> /home/mla/.ssh/authorized_keys
    chown -R mla:mla /home/mla/.ssh
    sed -i '58s/no/yes/' /etc/ssh/sshd_config
    systemctl restart sshd
    EOF
  
    $python_script = <<-EOF
    apt -q -y update
    apt -q -y install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
    cd /tmp
    wget -q https://www.python.org/ftp/python/3.11.7/Python-3.11.7.tgz
    tar -xzf Python-3.11.7.tgz
    cd Python-3.11.7/
    ./configure --enable-optimizations --quiet
    make -j `nproc` --quiet
    make altinstall --quiet
    # Ensure the new Python version is the default
    update-alternatives --install /usr/bin/python python /usr/local/bin/python3.11 1
    update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.11 1
    # Install pip and virtualenv
    pip install --upgrade pip
    pip install virtualenv
    EOF
  
    config.vm.box = "debian/bullseye64"
    config.vm.box_check_update = false
  
    config.vm.provision "shell", inline: $password_script
    config.vm.provision "file", source: "./mla_key.pub", destination: "/tmp/mla_key.pub"
    config.vm.provision "shell", inline: $ssh_script
  
    config.vm.define "runner" do |runner|
  
      runner.vm.network "private_network", ip: "192.168.56.110"
      runner.vm.provision "shell", inline: $python_script
      runner.vm.hostname = "runner"
      runner.vm.synced_folder ".", "/home/mla"
  
      runner.vm.provider :virtualbox do |runner|
        runner.name = "runner"
        runner.memory = 2048
        runner.cpus = 4
      end
    end
  
    config.vm.define "server-1" do |server|
  
      server.vm.network "private_network", ip: "192.168.56.111"
      server.vm.hostname = "server-1"
  
      server.vm.provider :virtualbox do |machine|
        machine.name = "server-1"
        machine.memory = 1024
        machine.cpus = 1
      end
    end
  
    config.vm.define "server-2" do |server|
  
      server.vm.network "private_network", ip: "192.168.56.112"
      server.vm.hostname = "server-2"
  
      server.vm.provider :virtualbox do |machine|
        machine.name = "server-2"
        machine.memory = 1024
        machine.cpus = 1
      end
    end
  end
  