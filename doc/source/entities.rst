.. _entities:

***********
Entities
***********

Entities are API objects which relate to each other to form a database.
Entities are those items which are complex collections of other data or other
entities.  Currently, the Entities closely model a traditional SQL database,
but as additional features are developed, additional entities will be needed.


Database
==========

A :py:class:`Database` is a logical collection of tables, views, datatypes, 
functions and applications related to the same set of data or purpose.
Databases are the equivalent of (and implemented as) a PostgreSQL schema.  
In Nimbodata, all :py:class:`Database` objects exist in the same "cloud"
(although not all might be visible or accessible to any particular user), 
although Universe would be a clearer term considering that some items may
not be accessible to one-another.

Here's an example of creating a database::

    >>> db = cloud.create_database('organization')

You can access and manage your database later really easily too::

    >>> db = cloud.Database('organization')
    >>> db.rename('nuthouse')
    >>> db = cloud.Database('nuthouse')
    >>> cloud.Database('nuthouse').drop() # same as db.drop()
    >>> db = cloud.Database('organization') # no more horsing around


Table
=======

A :py:class:`Table` stores rows of data with one or more columns.
Each :py:class:`Column` has a datatype, and the Column's datatype is also the
constructor for values of that type.  All data exists first in a table, because
you may only insert into a table.  Constraints and columns also maintain a
certain core affinity to the table that they are associated with, even when
being presented in a derived view.  Here's an example of creating a table with
no columns::

    >>> table = db.create_table('people')

As you might expect, management is easy here too::

    >>> table = cloud.Database('organization').Table('people')
    >>> table.rename('employees')
    >>> info = table.info # original table object still a-ok after rename
    >>> cloud.Database('organization').Table('employees').drop()
    >>> table.drop() # would have done the same thing... but will error here
    >>> table = cloud.Database('organization').Table('people') # goofin again.


Column
========

A column is a named, typed data descriptor.  In a relational database, any
data value in a row is described by its column. Server-side slice is 
forthcoming, but in the interim, limit + client slice is still pretty useful.
For a table to be really useful, you need columns... so, here's a more useful
example::

    >>> cols = [
    ...     {'name':'fullname','datatype':'Text'},
    ...     {'name':'age','datatype':'Integer'}
    ... ]
    >>> db = cloud.create_database('organization')
    >>> table = db.create_table('people',cols)
    >>> table
    >>> fullname, age = table.columns() # Useful for queries.
    >>> table.insert(['Jane',38])
    >>> table.insert({'age':83,'fullname':'John'}) # Also works
    >>> table.insert({'fullname':'Zorro'}) # He's sensitive about his age
    >>> table.select()
    

View
======

A :py:class:`View` is a reference to a query.  It provides a mechanism to 
access a consistent selection of data based on a pre-defined query.  From 
the user's perspective, the only difference between a :py:class:`Table` and 
:py:class:`View` is that you may only add data to a :py:class:`Table`.  
In fact, whenever selecting data, a user is only ever interacting with a 
view, even if they are selecting from a table.

    >>> fullname, age = table.columns()
    >>> view = db.create_view('oldtimers',{'objid':table,'where':age > 50 })
    >>> view.select([fullname]).rows
    [['John']]


Constraint
============

A :py:class:'Constraint' is a limitation on the data that can be inserted into
a particular table.  These are currently just a wrapper around SQL constraints,
but longer term we will implement functional-constraints built in the
analytical environment.
   
