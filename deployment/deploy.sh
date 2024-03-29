#!/bin/bash
sudo apt-get update
sudo apt-get install nginx
sudo apt-get install python3
sudo apt-get install python3-pip
sudo apt-get install mysql-server
sudo apt-get install mysql-client

echo "Would you like to configure MySQL? (Y/N)"
read answer
if [[ "$answer" == "Y" || "$answer" == "y" ]]
then
	echo "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'g7@#vgjaJl1';" > reset.sql
	sudo mysql -uroot < reset.sql
	rm reset.sql
fi

sudo apt-get install python3-mysqldb

sudo pip3 install flask
sudo pip3 install flask_wtf
sudo pip3 install flask-sqlalchemy
sudo pip3 install PyJWT
sudo pip3 install pycryptodome

sudo mkdir -p /opt/hip-vpls/controller
sudo mkdir -p /opt/hip-vpls/configurator

sudo rsync -rv ../controller/* /opt/hip-vpls/controller/
sudo rsync -rv ../configurator/backend/* /opt/hip-vpls/configurator/
sudo rsync -rv ../configurator/frontend/hip-vpls-controller/dist/* /var/www/hip_vpls/

sudo cp -rv ../configurator/nginx/default /etc/nginx/sites-enabled/hipls

sudo chown -R www-data:www-data /opt/hip-vpls/controller
sudo chown -R www-data:www-data /opt/hip-vpls/configurator
sudo chown -R www-data:www-data /var/www/hip_vpls/

echo "Would you like to reset the database HIP_VPLS? (Y/N)"
read answer
if [[ "$answer" == "Y" || "$answer" == "y" ]]
then
	mysql -uroot -pg7@#vgjaJl1 < ../configurator/database/schema.sql
fi

sudo rsync -rv ../systemd/vpls-controller.service /etc/systemd/system/
sudo systemctl enable vpls-controller
sudo systemctl start vpls-controller

sudo rsync -rv ../systemd/vpls-configurator.service /etc/systemd/system/
sudo systemctl enable vpls-configurator
sudo systemctl start vpls-configurator

sudo service nginx restart
