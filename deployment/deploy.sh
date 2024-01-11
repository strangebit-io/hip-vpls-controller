#!/bin/bash
sudo apt-get update
sudo apt-get install python3
sudo apt-get install python3-pip
sudo apt-get install mysql-server
sudo apt-get install mysql-client

echo "Would you like to configure MySQL? (Y/N)"
read answer
if [[ "$answer" == "Y" || "$answer" == "y" ]]
then
	echo "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'NigAfDov';" > reset.sql
	sudo mysql -uroot < reset.sql
	rm reset.sql
fi

sudo apt-get install python3-mysqldb

sudo pip3 install flask
sudo pip3 install flask_wtf
sudo pip3 install flask-sqlalchemy

sudo mkdir -p /opt/hip-vpls/controller
sudo mkdir -p /opt/hip-vpls/configurator

echo "Would you like to reset the database HIP_VPLS? (Y/N)"
read answer
if [[ "$answer" == "Y" || "$answer" == "y" ]]
then
	mysql -uroot -pNigAfDov < ../configurator/database/schema.sql
fi

#sudo rsync -rv ../systemd/vpls-controller.service /etc/systemd/system/
#sudo systemctl enable vpls-controller
#sudo systemctl start vpls-controller

