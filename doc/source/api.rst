.. api:

*****************
API Reference
*****************


Major Components
==================

The API consists of two concepts - Entities and Controllers.  Entities
encapsulate much of the functionality of the objects in Nimbodata.  All actions
available via entities are also available via controllers, which are stateless,
functional API calls.  Any query beyond a Table/View scope, and any directory
query will be handled by a Controller (because of their transcendental scope).

Entities
=========

Entities make it easy to use the API in a natural way for object-orented
programming.  An entity encapsulates an identity and methods
available to act on the particular type.  The entities act as proxy objects -
they do not store any data other than the `objid` of an entity - they simply
provide a proxy for the methods provided.
    
    *   Database - contains related tables, views, datatypes and applications
    *   Application - provides a logical structure, objects and functions
    *   Table - primary container for data, all data in the database is stored in a table.
    *   View - a virtual table which can represent and transform data in tables and other views.
    *   Column - a column defines a datatype, name and description for entries in a Row
    *   Results - similar to a View except Results are actual data returned, contains header info and rows
    *   Row - an individual table record or view item whose data values are described by their respective columns


Select
============

The select engine transcends any particular entity, and allows a user to select
from and join tables and views with most of the power of SQL.  Aggregation,
column functions and inner joins are all currently supported.


REST API
==========

Example Request URLs by HTTP Verb shown in Python-nimbodata.

GET
-----

-   /entitys/<objid>/ --> Entity(objid).info
-   /databases/ --> Database().listing()
-   /databases/<dbid>/ --> Database(dbid).info
-   /databases/<dbid>/<objid>/ -->
-   /databases/<dbid>/tables/ --> Datatabase(dbid).tables()
-   /databases/<dbid>/views/ --> Database(dbid).views()
-   /tables/<tblid>/ --> Table(tblid).info
-   /views/<tblid>/ --> View(tblid).info
-   /views/<viewid>/columns/ --> View(tblid).columns()
-   /views/<viewid>/select/ --> View(tblid).select()

POST
-----

-   /databases/ --> Database().create(**json_payload)
-   /tables/ --> Table().create(**json_payload)
-   /tables/<tblid/ --> Table(tblid).insert(**json_payload)
-   /tables/<tblid>/column/ --> Table(tblid).create_column(**json_payload)
-   /tables/<tblid>/constraint/ --> Table(tblid).create_constraint(**json_payload)
-   /views/ --> View().create(**json_payload)

PUT
----

-   /databases/<dbid>/ --> Database(dbid).rename(**json_payload)
-   /tables/<tblid>/ --> Table(tblid).rename(**json_payload)
-   /columns/<colid>/ --> Columns(colid).rename(**json_payload)
-   /columns/<colid>/modify/ --> Columns(colid).modify(**json_payload)

DELETE
-------

-   /databases/<dbid>/ --> Database(dbid).drop(**json_payload)
-   /tables/<tblid>/ --> Table(tblid).drop(**json_payload)
-   /views/<viewid>/ --> View(viewid).drop(**json_payload)
-   /columns/<colid>/ --> Column(colid).drop(**json_payload)
