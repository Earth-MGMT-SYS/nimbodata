nimbodata
=========

Python/Javascript Data Platform.

With the powers of PostgreSQL, Python and Javascript combined, we are 
captain data platform!

For complete documentation, see 
[Nimbodata at Read the Docs](http://nimbodata.readthedocs.org/en/latest/).

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

Add ppas:

    $ sudo apt-add-repository ppa:ubuntugis/ubuntugis-unstable

Then:
    
    $ sudo apt-get update
    
Now you'll need a few packages:

    $ sudo apt-get install postgresql-9.4 postgresql-9.4-postgis-2.1 postgresql-9.4-postgis-2.1-scripts postgis gdal-bin python-dev python-pip python-gdal libpq-dev postgresql-plpython-9.4 nodejs nodejs-legacy npm

Now you'll need some pip deliciousness:

    $ sudo pip install flask Shapely jsonpickle requests flask-security flask-cors psycopg2
    
Now you need to configure PostgreSQL, which is always a blast:

    $ sudo nano /etc/postgresql/9.4/main/pg_hba.conf
    
And modify the line:

    local   postgres        peer
    
To (development only):

    local   all     all     trust
    
If you are uncomfortable with the above, then you'll need to peruse `install.sql`
to establish which sql users you want to have what access (for now).

Also make sure you are on port 5432: 

    $ sudo nano /etc/postgresql/9.4/main/postgresql.conf

And finally:

    $ sudo /etc/init.d/postgresql restart
    
And then:
    
    $ sudo -u postgres createdb cloud_admin
    $ sudo -u postgres createuser --superuser cloud_admin

Now travel to where you want Nimbodata and instantiate the database:

    $ git clone https://github.com/Earth-MGMT-SYS/nimbodata.git
    $ cd nimbodata/install
    $ python init_db.py
    
