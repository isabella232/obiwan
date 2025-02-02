#/bin/bash

sudo apt-get install linux-image-extra-$(uname -r) linux-image-extra-virtual
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
# verify: 9DC8 5822 9FC7 DD38 854A E2D8 8D81 803C 0EBF CD88
# with:
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
                         $(lsb_release -cs) \
                         stable"
sudo apt-get update
sudo apt-get install docker-ce
# check it worked
sudo docker run hello-world
