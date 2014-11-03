
function makeid() {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

    for( var i=0; i < 5; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}

function nada () {}


function Model () {
    this.init()
}

Model.prototype = function () {
    
    var responders,loadevents;
    var self;
    var override_datasource;
    
    return {
        
        init: function() {
            self = this
        },
        
        register: function(widget) {
            responders[widget._spec.id] = widget
            if (widget._spec.datasource) {
                if (override_datasource) {
                    widget._spec.datasource = override_datasource
                }
                loadevents.push(widget)
            }
        },
        
        respond: function (source,event,details) {
            if (event == 'select') {
                
                var basicresponders = []
                var inforesponders = []
                var subresponders = []
                var info = details._info ? details._info : details
                
                d3.values(responders).forEach(function(sink) {
                    // If the widget does not define event_filter, it gets
                    // only layout events.
                    var fresult = false
                    if (sink.event_filter) {
                        fresult = sink.event_filter(source,event,details)
                    }
                    
                    if (!fresult) {
                        fresult = false
                    }
                    
                    if (fresult && sink._spec.subview) {
                        subresponders.push(sink)
                        if (sink.clear) sink.clear()
                    } else if (fresult === true) {
                        basicresponders.push(sink)
                        if (sink.clear) sink.clear()
                    } else if (fresult == 'refresh') {
                        sink.reload()
                    } else if (fresult == 'info') {
                        inforesponders.push(sink)
                        if (sink.clear) sink.clear()
                    } else if (fresult && fresult[0] == 'select') {
                        if (sink.clear) sink.clear()
                        cloud.select(fresult[1],function (e,d) {
                            sink.update(e,d)
                            Layout.refresh()
                        })
                    } else {
                        // Otherwise it has a special request
                        if (fresult[1]) {
                            if (fresult[1].entitytype) {
                                var ent = cloud[fresult[1].entitytype](fresult[1].objid)
                                ent[fresult[0]](function (e,d) {
                                    sink.update(e,d)
                                    Layout.refresh()
                                })
                            } else {
                                var ent = new Entity(fresult[1])
                                ent.info(function (e,d) {
                                    sink.update(e,d)
                                    Layout.refresh()
                                })
                            }
                        }
                    }
                    
                })
                
                if (details.rowid) {
                    cloud.get_byrowid(details.objid,details.rowid, function (e,d) {
                        basicresponders.forEach(function(rsp) {
                            rsp.update(e,d)
                        })
                    })
                    subresponders.forEach(function(rsp) {
                        var sink = rsp[0]
                        var view = rsp[1]
                        var row = rsp[2]
                        cloud.get_byrowid(view,row,function (e,d) {
                            sink.update(e,d)
                        })
                    })
                    Layout.refresh()
                    return
                }
                
                if (basicresponders.length > 0) {
                    if (info.objid) {
                        var params = {
                            'objid':info.objid,
                            'limit':200
                        }
                    } else {
                        var params = info
                    }
                    cloud.select(params,function (e,d) {
                        basicresponders.forEach(function(rsp) {
                            rsp.update(e,d)
                        })
                        inforesponders.forEach(function(rsp) {
                            rsp.update(e,d)
                        })
                        Layout.refresh()
                    })
                } else if (inforesponders.length > 0) {
                    cloud.Entity(info.objid).info(function (e,d) {
                        inforesponders.forEach(function(rsp) {
                            var inf = {'info':d}
                            rsp.update(e,inf)
                        })
                        Layout.refresh()
                    })
                }
                
            } else if (event == 'rename') {
                cloud[details.entitytype](details.objid)
                    .rename(details.newname, function (e,d) {
                        if (details.entitytype == 'Column') {
                            var selobjid = details.parent_objid
                        } else {
                            var selobjid = details.objid
                        }
                        Model.respond(source,'select',{
                            'objid':selobjid
                        })
                    })
            } else if (event == 'modify') {
                var mod_params = {}
                var id_params = ['entitytype','objid','parent_objid']
                for (var x in details) {
                    if (id_params.indexOf(x) < 0) {
                        mod_params[x] = details[x]
                    }
                }
                cloud[details.entitytype](details.objid)
                    .modify(mod_params, function (e,d) {
                        if (details.entitytype == 'Column') {
                            var selobjid = details.parent_objid
                        } else {
                            var selobjid = details.objid
                        }
                        Model.respond(source,'select',{
                            'objid':selobjid
                        })
                    })
            } else if (event == 'clear') {
                d3.values(responders).forEach(function(sink) {
                    if (sink.clear) {
                        sink.clear()
                    }
                })
            } else if (event == 'refresh') {
                d3.values(responders).forEach(function(sink) {
                    if (sink.refresh) {
                        sink.refresh()
                    }
                })
            } else if (event == 'legend') {
                d3.values(responders).forEach(function(sink) {
                    if (sink.legend) {
                        sink.update(null,details)
                    }
                })
            } else if (event == 'selectrow') {
                d3.values(responders).forEach(function(sink) {
                    if (sink._spec.subselect) {
                        if (sink.event_filter) {
                            var fresult = sink.event_filter(source,event,details)
                            cloud.select(fresult, function (e,d) {
                                sink.update(e,d)
                            })
                        }
                    } else if (sink._spec.subview) {
                        if (sink.event_filter) {
                            var fresult = sink.event_filter(source,event,details)
                            var viewid = fresult[0], rowid = fresult[1]
                            cloud.get_byrowid(viewid,rowid, function (e,d) {
                                sink.update(e,d)
                            })
                        }
                    } else if (sink.event_filter && sink.event_filter(source,event,details)) {
                        cloud.get_byrowid(details.objid,details.rowid, function (e,d) {
                            sink.update(e,d)
                        })
                    }
                })
            } else if (event == 'create_view') {
                cloud.Database(details.parent_objid)
                    .create_view(details.name,details.params,function (e,d) {
                        Model.respond(source,'select',d)
                    })
            } else if (event == 'style') {
                d3.values(responders).forEach(function(sink) {
                    if (sink.event_filter && sink.event_filter(source,event,details)) {
                        if (sink.style) sink.style(details)
                    }
                })
            }
        },
        
        getmodel: function (url,datasource) {
            if (environment == 'mobile') return
            if (datasource) override_datasource = datasource
            if (!url) url = './app.json'
            else url += 'app.json'
            d3.json(url,self.loadmodel)
        },
        
        loadmodel: function (e, doc) {
            responders = {}
            loadevents = []
            
            var app, css;
            
            doc.rows.forEach(function(d) {
                
                if (d[0] == 'app.json') {
                    app = JSON.parse(d[1])
                } else if (d[0] == 'app.css') {
                    css = d[1]
                }
            })
            
            d3.select('style#appcss').remove()
            
            var style = document.createElement("style")
            style.id = "appcss"
            style.appendChild(document.createTextNode(css))
            document.head.appendChild(style)
            
            Layout.init(app) // Populates loadevents
            loadevents.forEach(function (sink) {
                var src = sink._spec.datasource
                if (src instanceof Array) {
                    n_get(src,function (e,d) {
                        sink.update(e,d)
                    })
                } else if (src.slice(0,4) == 'http' || src.slice(0,1) == '.') {
                    var texty = ['html','txt','mst']
                    var ext = src.split('.').pop()
                    if (texty.indexOf(ext) != -1){
                        d3.text(src,function (e,d) {
                            sink.update(e,d)
                        })
                    } else {
                        d3.json(src,function (e,d) {
                            sink.update(e,d)
                        })
                    }
                } else {
                    cloud[src](function (e,d) {
                        sink.update(e,d)
                    })
                }
            })
            Layout.refresh()
        },
                
        on_load: function () {
            self.getmodel()
        },
    }
}()

Model = new Model()

if (!server) {
    server = ""
}

var cloud = connect(
    server,
    'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7',
    Model.on_load
)

///////////////////////////////////////////////////////////////////////////////
////// Over the line, Smokey //////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////


function set_env ( env ) {
    environment = env
}

module.exports = {
    Model: Model,
    environment: set_env
}
