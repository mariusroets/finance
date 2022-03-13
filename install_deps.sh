#!/bin/bash

groupadd -g 1000 roetsm
useradd -d /home/roetsm -g 1000 -u 1000 roetsm
mkdir /home/roetsm
chown roetsm:roetsm /home/roetsm

#apt-get update && apt-get -y install sudo curl
#curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
#apt-get install -y nodejs
#cd /app
#sudo -u roetsm npm init -y
#sudo -u roetsm npm install webpack webpack-cli react react-dom create-react-app
