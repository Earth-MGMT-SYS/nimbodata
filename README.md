nimbodata
=========

Python/Javascript Data Platform.

With the powers of PostgreSQL, Python and Javascript combined, we are captain data platform!

## Installation ##

To begin, you need a few things pip can't provide.  Arch or Ubuntu 14.04 is recommended, and since it still requires beta-software, it is not for the faint of heart.

*   git (or just download the zip)
*   PostgreSQL 9.4 (beta), you will also need plpython2u
*   gdal-bin, gdal-dev
*   Python 2.7 and python-dev
*   nodejs (also npm)

For node and the remaining Python requirements, pip install and npm install should handle it.

## Detailed Install ##

These instructions will assume Ubuntu 14.04, you Archers are an industrious bunch
and I'm sure you can manage.

First, you'll need PostgreSQL 9.4.  For now, since it is beta, you'll need to
go about it the hard way, add this you your /etc/apt/sources.list

    deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main 9.4
    
Then execute (to update the apt-key):

    $ wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | sudo apt-key add -
    
Then:
    
    $ sudo apt-get update
    
Now you'll need a few packages:

    $ sudo apt-get install postgresql-9.4 postgis gdal-bin libgdal-dev \
      python-dev python-pip
      
And a few postgres things that apt can't seem to find on its own (beta fun):

    $ wget http://apt.postgresql.org/pub/repos/apt/pool/main/p/postgis/postgresql-9.4-postgis-2.1-scripts_2.1.3%2bdfsg-4.pgdg70%2b1_all.deb
    $ sudo dpkg -i postgresql-9.4-postgis-2.1-scripts_2.1.3+dfsg-4.pgdg70+1_all.deb
    $ wget http://apt.postgresql.org/pub/repos/apt/pool/main/p/postgresql-9.4/postgresql-plpython-9.4_9.4~beta2-2~129.bzr487.pgdg14.04%2b1_amd64.deb
    $ sudo dpkg -i postgresql-plpython-9.4_9.4~beta2-2~129.bzr487.pgdg14.04+1_amd64.deb

Now you'll need some pip deliciousness:

    $ sudo pip install flask psycopg2 Shapely jsonpickle requests flask-security flask-cors
    
Now you need to configure PostgreSQL, which is always a blast:

    $ sudo nano /etc/postgresql/9.4/main/pg_hba.conf
    
And modify the line:

    local   postgres        peer
    
To (development only):

    local   all     all     trust
    
Now travel to where you want Nimbodata and instantiate the database:

    $ git clone https://github.com/Earth-MGMT-SYS/nimbodata.git
    $ cd nimbodata/install
    $ python init_db.py
    
