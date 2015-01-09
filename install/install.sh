#!/bin/bash

echo deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main 9.4 >> /etc/apt/sources.list
wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | sudo apt-key add -
apt-add-repository -y ppa:ubuntugis/ubuntugis-unstable
apt-get update

if [ $1 = 'upgrade' ]; then
    apt-get upgrade -y
fi

apt-get install -y mercurial postgresql-9.4 postgresql-9.4-postgis-2.1 postgresql-9.4-postgis-2.1-scripts postgis gdal-bin python-dev python-pip python-gdal libpq-dev postgresql-plpython-9.4 nodejs npm nodejs-legacy
pip install flask Shapely jsonpickle requests flask-security flask-cors python-dateutil psycogreen gevent gunicorn psycopg2
npm install -g d3 grunt-cli
npm install

echo local  all all trust >> /etc/postgresql/9.4/main/pg_hba.conf


hg clone https://bitbucket.org/cacahootie/nimbodata
cd ./nimbodata/install

pg_dropcluster --stop 9.3 main

cp ./config/pg_hba.conf /etc/postgresql/9.4/main/pg_hba.conf
cp ./config/postgresql.conf /etc/postgresql/9.4/main/postgresql.conf

/etc/init.d/postgresql restart

sudo -u postgres createdb cloud_admin
sudo -u postgres createuser --superuser cloud_admin

python init_db.py
