# docker环境配置(ubuntu)

1. 安装docker

   ```bash
   $ sudo snap install docker
   ```

2. 安装docker-machine 

   ```bash
   $ base=https://github.com/docker/machine/releases/download/v0.16.0 &&
     curl -L $base/docker-machine-$(uname -s)-$(uname -m) >/tmp/docker-machine &&
     sudo install /tmp/docker-machine /usr/local/bin/docker-machine
   ```

   检查是否成功：

   ```bash
   $ docker-machine version
   docker-machine version 0.16.0, build 9371605
   ```

   

3. 安装virtual box来作为docker-machine的driver：

   编辑/etc/apt/sources.list添加这行内容：`"deb https://download.virtualbox.org/virtualbox/debian bionic contrib"` 

   ```bash
   $ wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add - 
   $ sudo apt-get update 
   $ sudo apt-get install virtualbox-5.2
   ```

   

4. 创建一个docker-machine：

   ```bash
     $ docker-machine create --driver virtualbox default
     Running pre-create checks...
     Creating machine...
     (staging) Copying /Users/ripley/.docker/machine/cache/boot2docker.iso to /Users/ripley/.docker/machine/machines/default/boot2docker.iso...
     (staging) Creating VirtualBox VM...
     (staging) Creating SSH key...
     (staging) Starting the VM...
     (staging) Waiting for an IP...
     Waiting for machine to be running, this may take a few minutes...
     Machine is running, waiting for SSH to be available...
     Detecting operating system of created instance...
     Detecting the provisioner...
     Provisioning with boot2docker...
     Copying certs to the local machine directory...
     Copying certs to the remote machine...
     Setting Docker configuration on the remote daemon...
     Checking connection to Docker...
     Docker is up and running!
     To see how to connect Docker to this machine, run: docker-machine env default
   ```

   查看创建是否成功：

   ```bash
   $ docker-machine ls
   NAME      ACTIVE   DRIVER       STATE     URL   SWARM   DOCKER    ERRORS
   default   -        virtualbox   Stopped                 Unknown   
   ```

   创建好之后最好重启一下

5. 修改docker的源：

   修改或新增/etc/docker/daemon.json

   ```json
   # vi /etc/docker/daemon.json
   
   {
   
   "registry-mirrors": ["https://registry.docker-cn.com"]
   
   }
   
   
   ```

   ```bash
   $ systemctl restart docker.service
   ```

