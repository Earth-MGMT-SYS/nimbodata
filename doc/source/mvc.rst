.. mvc:

**************
MVC
**************

(replacing homegrown controller/router with Backbone in progress)

Nimbodata supports the MVC style of web application development, adapted to the
capabilities of modern browsers, and the use case of data-driven applications 
(as opposed to content-driven applications).

The core principle is to integrate a modern MVC as closely as possible with the
capabilities and philosophy of a relational database.  Also important is the
desire to separate the datamodel from applications as much as possible.  In the
real world of management systems, needs develop over time: the datamodel needs
to support new and different applications as time goes on.  Ultimately, the
datamodel is about expressing a coherent body of data beyond any single app.

Built upon this "coherent body of data" are the applications themselves. In 
the most basic form, an app binds views to the datamodel using JSON. The 
nimbodata server works with the controller to acquire the assets specific 
to the device and datamodel state, and a Backbone application 
router/controller manages the state of each individual widget (view) with 
respect to the datamodel and user interaction.  Each widget manages its own 
DOM in reaction to events from other widgets.  A layout manager controls the
overall state of the app, managing the layout of the widget containers as
necessary based on device characteristics at load and as things such as
orientation change.  This enables many interactive view layout widgets, such
as tabs, expando panes, slide-outs, etc... that may be used depending on a
particular device size and orientation and can maintain consistent positioning
for scrolling or non-scrolling main windows.

Currently the platform is designed and oriented towards the automated ingestion
of data, focusing on enabling interactive visualization.  However, the core
components are in place for full user interactivity with data models for data
input and validation, however this feature is still largely in development.
