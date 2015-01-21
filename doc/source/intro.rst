.. introduction:

**************
Introduction
**************

Nimbodata aims to enable distributed management systems.  The core capabilities
of any management system include the collection, validation, management,
analysis, and communication of structured information in the furtherance of an
objective.  Nimbodata expands upon the now age-old concepts of a relational
database and GIS, but makes them Python, REST and Javascript native, with
a sprinking of modern goodness like an object store thrown in.

Nimbodata is a platform inspired by Python, Zope, ArcGIS and infuriated
by SharePoint; aimed at producing a cross-platform, standards-based approach 
to developing and deploying applications that exist beyond a particular device
or machine.


Functional Description
========================

Nimbodata makes a relational, spatially and temporally aware data store 
available via a REST interface, which enables a rich, Pythonic client as 
well as a Python/JavaScript MVC framework for developing data-driven 
applications.

Currently implemented in Nimbodata:

-   Relational datastore powered by PostgreSQL 9.4 offering jsonb, PostGIS and
    range queries (and Python types to support them).
-   Metadata manager which provides UUID-style naming for entities, which 
    enables both distributed operation as well as renaming without side-
    effects.
-   REST interface which provides 100% access to the capabilities of the
    datastore.
-   Python client which includes queries driven by JSON or pythonic overloaded
    operators a-la SQLAlchemy but without chaining.
-   Javascript MVC client including 10+ widgets, a layout manager and data 
    model for navigating and viewing data. Apps are composed primarily of a css
    file and a JSON file, however, the architecture allows for simple
    extensibility in Javascript.
-   ETL framework which can ingest web services, csv, geodatabases and
    shapefiles.
-   Owner-based permissions model.

Rudiments in place, More Dev Planned:

-   Temporal database capability.  All non-schema changes are currently captured
    as append-only and presented via a current-view.  Query engine support for
    querying the state as of a particular date needs integration.  Waiting on
    integration with ZFS for cloning and schema-change checkpointing.


Vision
========
    
*   Enable cooperation amongst groups with different interests and policies for
    sharing data while providing a decentralized platform to manage the flow of
    data.
*   Provide a rich data library which allows users full query access to as much
    data as possible in a consistent format (i.e. follow naming standards
    and establish extensive foreign key relationships).
*   Python is great for programmers, but the spirit is wholly applicable to
    data analysis tools.  By providing a powerful platform for users to leverage
    Python, we hope to expand the power and reach of the Python ecosystem.
*   Enable meta-programming approaches for relational data stores - such as
    tools for applying a specific aggretation pattern to different sets of
    views.


What's Unique
===============

While superficially similar concepts exist (such as SQLAlchemy and 
Flask-Restless), Nimbodata strives to develop a full-stack platform inspired by
Zope and infuriated by SharePoint and ArcGIS.

Currently the key unique concepts fully implemented in Nimbodata are:

    *   Append-only modification mode for data and metadata (not including 
        structure currently)
    *   Metadata-mediated queries which reduce the risk of allowing ad hoc
        queries to untrusted users (all database input is either parameterized,
        or for identifiers, fulfilled via catalog not user input).
    *   Full functionality via REST/JSON.
    *   Tiling, simplifying GeoJSON query functionality integrated with
        full relational query capabilities.
    *   All relationships are by ID not name, allowing side-effect-free
        renames.
    *   Widget-based Javascript MVC which directly integrates with the core 
        data model.

Ongoing development is aimed at the following unique capabilities:

    *   Micro-versioning (temporal database) for all non-structural changes
        (inserts/updates/deletes/renames/create_*)
    *   Macro-versioning to reproduce state for each database structurural
        change not encapsulated by microversioning
    *   Push/Pull ala git
    *   Ability to control versioning behavior on a default and per-table basis
    *   Platform applications self-hosted from database - versioning covers apps
    *   Inherent streaming replication to support read-isolation for queries
    

What's The Same
================

Nimbodata is inspired by the power of the relational database.  While Nimbodata
is currently implemented on a SQL database and is closely based on the
functionality of PostgreSQL, we do not strive to be SQL-compliant or to limit
Nimbodata to the implementation decisions of SQL.  Most PostgreSQL types are 
reused with the same names.  Most PostGIS types have been simplified and
condensed (i.e. LineString and MultiLineString are now just Line).
