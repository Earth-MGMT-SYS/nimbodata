.. _apps:

***********
Apps
***********

Apps are built upon the Nimbodata platform.  Any functionality which is not
core functionality runs as an app.  The app platform provides two key
functionalities:

*   An in-browser MVC framework powered primarily by Python, but extensible
    in Javascript.  This provides a layout manager which can be managed 
    natively in Python with no HTML as well as widgets which are oriented 
    towards Nimbodata types and entities.  The widget framework is easily 
    extensible, from modifying the event filter to extending existing widgets.
*   Server-side functionality beyond core queries.  This can be used
    to execute a number of commands in one-round trip and to provide a domain-
    specific API.  Currently the server-side component is in-progress, current
    apps are front-end only, using core functionality to provide the data.  The
    API generation functionality will support programming a server application
    in Python an dynamically providing access via the Javascript Data Manager.
    
Apps are database entities in and of themselves, and as such, benefit from all
of the core database functionality, such as metadata management and built-in
permissions control.

In this Alpha mode, apps are files, but soon the app code, css and html will
be hosted entirely dynamically by the platform. (use python -m SimpleHTTPServer
in project root dir to serve files on :8000).


Architecture
=============

All data persistence is provided by the Nimbodata server, and all operations
conducted by an app, either server-side or client-side, are mediated through
the core API.  This means that permissions and other aspects of policy are
managed centrally, app designers need not concern themselves with security
beyond establishing sensible policies.

Currently, only the core functionality exists server-side, to support the
catalog app.  Dynamic generation of APIs and REST servers using Flask is
still nascent.

The architecture basically conforms to the MVC concept, but we use terms which
are not tainted by the confusion, and are hopefully clearer about the roles
the components play in the overall client system.

The browser environment consists of four primary components:

*   The Layout Manager, which interprets the JSON document specification, and
    manages setting the view mode of widgets and managing resizes.  Longer-term,
    the layout manager will be the first to initialize to determine environment
    and pull down only the resources specific to the environment (i.e. browser,
    mobile, etc...).
*   The Subscription Manager, which mediates the interactions between widgets.  
    Essentially, the datamodel is a local pub-sub controller.  Widgets 
    (sources) are responsible for notifying the datamodel when they emit an 
    event (distinct from DOM events), and the datamodel will examine its 
    subscription list and route the event to the appropriate consumers (sinks).
*   The Data Manager, which provides the bridge between Javascript and
    the REST API for the core (and the apps...).
*   Widgets fire events which correlate to actions against the API.  Widgets 
    have an `event_filter` method which provides the widget an opportunity to 
    receive the update data as-is, or to provide a new request based on some
    modification of the original and the widget state.  The Data Model collects
    all the requests, and executes the individual requests necessary to 
    fulfill all the requests, then provides the update results to the sinks.
*   Widgets are where the rubber meets the road.  All DOM interactions
    are controlled by widgets, which pretty well explains their purpose.  They
    fit into slots in the Layout Manager.  Widgets provide an `init` method
    as well as an `update` method.  `init` is called by the layout manager when
    the widget is created, and is provided the root node as a d3 selection, and
    the JSON specification for the widget, 'id' and 'widget' properties are
    required, a few others will be reserved, and the remainder will be free
    for widget specs.


Layout Manager
================

The overall layout of the page is controlled by the Layout Manager.  The
Layout Manager does not interact with the DOM itself, but calls widget refresh
methods in a controlled manner in response to events which cause layout 
changes.

   
