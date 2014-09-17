.. introduction:

**************
Introduction
**************

The initial goals of Nimbodata are to provide relational capabilities in a terse
and Pythonic syntax, allowing rich support for the analytical power of a relational
database as if it were a native capability of Python.

Since Nimbodata is still in the early phases of development, this section is
basically as important as the rest.  Nimbodata aims to support a modern
approach to the development, deployment and use of management information
systems.  The tremendous power inherent in collecting, organizing, and analyzing
information in a continuous improvement approach is hampered by our 20th
century tools.  In the hubub over "big data", people seem to have forgotten
that for many organizations regular data is enouch of a challenge - and if
our tools aren't up to snuff for regular data, big data is still in many ways
an illusion.

Nimbodata will support a platform inspired by Python, Zope, ArcGIS and infuriated
by SharePoint; aimed at producing a cross-platform, standards-based approach 
to developing and deploying applications that exist beyond a particular device
or machine.

We will:

-  Enable truly distributed, data-driven applications with an approach influenced
   by github.  By encapsulating the data and code into a single, self-hosting
   data platform that provides revision control and cloning capabilities.
-  Provide quick and easy access to the world's free data, enabling users to
   develop and share applications to evaluate and act upon the mountains of data
   that are available.
-  Enable developers to create domain-specific management systems that are
   easy to deploy, maintain and customize.
-  Provide a cloud platform to store and share data and applications, which
   is masterless and decentralized.

Functional Description
========================

Nimbodata is a platform for the full life cycle of collection, management 
and analysis of structured data.  Nimbodata makes a relational data store 
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
    file and a JSON structure, however, the architecture allows for simple
    extensibility in Javascript.
-   Update tool which can ingest web services, csv, geodatabases and shapefiles.
-   Owner-based permissions model.
-   Data input forms automatically generated from a database table, leveraging
    database constraints and a JSON schema for validation.

Rudiments in place, More Dev Planned:

-   Temporal database capability.  All non-schema changes are currently captured
    as append-only and presented via a current-view.  Query engine support for
    querying the state as of a particular date needs integration.  Waiting on
    integration with ZFS for cloning and schema-change checkpointing.
-   Nimbodata analysis engine.  A set of tools and datatypes which enable the
    same capabilities across the datastore and analysis layer.  Mostly in place,
    just needs to be exposed properly.
    
Longer term goals:

-   Workflows and global event manager.
-   Conflict manager for managing merges.


Vision
========

We reject the notion of domain-specific platforms, the challenges of the 21st
century are not just operations or resource planning (for instance), but rather
require cooperation amongst a variety of fields to acheive successful outcomes.

The Python ecosystem provides the ability to effectively interact with nearly 
any form of digital information with an idiom that encourages easy-to-read
code.  Platforms such as a GIS or CMS provide domain-specific implementations
on top of basically the same core functionality - a relational data store.

While there have been many platforms with similar core concepts since the days
of the earliest mainframes, technology has developed to enable a few key
features previously infeasible:

*   Provide reasonable performance and a high-level interface.
*   Take advantage of the maturation of web standards to the point where client
    platform independence is feasible using simple techniques.
*   A distributed cloud architecture will allow users to take advantage of
    public data sources as well as private-cloud and private-local data in
    a seamless manner.
    
Other aspects of the vision which aren't really enabled by technology, but
don't seem to have been picked up by others:

*   Enable cooperation amongst groups with different interests and policies for
    sharing data while providing a decentralized platform to manage the flow of
    data.
*   Provide a rich data library which allows users full query access to as much
    data as possible in a consistent format (i.e. follow naming standards
    and establish extensive foreign key relationships).
*   Python is great for programmers, but the spirit is wholly applicable to
    data analysis tools.  By providing a powerful platform for users to levarage
    Python, we hope to expand the power and reach of the Python ecosystem.


What's Unique
===============

While superficially similar concepts exist (such as SQLAlchemy and 
Flask-Restless), Nimbodata strives to develop a full-stack platform inspired by
Zope and infuriated by SharePoint and ArcGIS.

Currently the key unique concepts implemented in Nimbodata are:

    *   Append-only modification mode for data and metadata (not including 
        structure currently)
    *   Metadata-mediated queries which reduce the risk of allowing ad hoc
        queries to untrusted users
    *   Full functionality via REST/JSON
    *   Tiling GeoJSON query functionality
    *   All relationships are by ID not name, allowing side-effect-free renames

Ongoing development is aimed at the following unique capabilities:

    *   Micro-versioning (temporal database) for all non-structural changes
        (inserts/updates/deletes/renames/create_*)
    *   Macro-versioning to reproduce state for each database structurural
        change not encapsulated by microversioning
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
