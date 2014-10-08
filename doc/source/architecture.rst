.. _architecture:

*****************
Architecture
*****************

The core of the platform is the data persistence engine.  It is written in
Python and exposes a REST interface.  This Python application interacts with
PostgreSQL via unix sockets on the localhost.  The application mediates all
access to the database via a metacatalog which spans PostgreSQL clusters.


Nimbodata Core Server
=======================

Currently targeting Python 2.7.  Numerous dependencies, see the install
documentation for more detail.

The Nimbodata server uses psycopg2, a syntax engine, a metadata catalog
and some hidden columns to provide extra capabilities beyond a traditional SQL
database.  Current functionality is aimed to provide a feature complete
relational (i.e. not SQL) database, with geospatial and object store support.

The server logic and the client access patterns are both oriented around the 
API structure, which in turn, is structured on the relational model.


Nimbodata Application Server
==============================

Currently half-exists.  The existing Python client will provide the core API
to all manner of apps, ranging from analysis engines to front-end apps.  Uses
the Nimbodata API generation capabilities to generate a REST API from user code
which follows a reasonable convention and serves front-end assets such as the
`app.json` and `app.css`.  The Nimbodata API generation needs to step up its
parameter handling game (query string support), but this is not too far off.


Nimbodata Clients
==================

The Nimbodata platform targets Python 2.7, NodeJS and modern HTML5/Javascript.
Clients are provided for Python and Javascript (same client runs in browser and
Node).

The clients each serve different purposes.  The Python client is intended 
to be the primary application development environment, and provides a rich 
set of features for querying the database using Python operators in a style 
similar to SQLAlchemy.  The NodeJS client is primarily for testing 
purposes, and to enable client-side apps to be developed in NodeJS for 
those who prefer Javascript (Python is strongly encouraged, however).  Finally,
the browser client provides the MVC environment for application development, 
and the same core driver functionality as the NodeJS client.


Nimbodata Apps
===============

At the core, a Nimbodata app is just data in the database.  The app platform
is built on the rudiments provided only by the relational datastore and entity-
model, with more creature comforts planned.  Nimbodata apps can be developed to
run in either a pure Python environment, as an api-only toolkit or as a full
platform app, with an adaptive UI and advanced cloud-driven capabilities.



