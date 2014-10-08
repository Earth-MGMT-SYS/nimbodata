// Copyright (C) 2014  Bradley Alan Smith

function Map (root, spec) {
    this.init(root,spec)
}

Map.prototype = Object.create(Widget.prototype)

extend(Map, function () {

var base_layers = [],
    feature_layers = [];
    
var _map, self;
var _geocol;
var fill = "#29CAE1", stroke = "#F40C0E";
var strokewidth = 2, strokewidthhover = 3;
var _style = {
    "clickable": true,
    "color": stroke,
    "fillColor": fill,
    "weight": strokewidth,
    "opacity": 0.5,
    "fillOpacity": 0.5
};

var _hover_style = {
    "clickable": true,
    "color": stroke,
    "fillColor": fill,
    "weight": strokewidthhover,
    "opacity": 0.9,
    "fillOpacity": 0.3
};

var maximized = false;

// Private function used in init, also with public method interface.
function _add_base_layer (urltempl) {
    
    var mq_tiles = L.tileLayer(urltempl,{
        maxZoom: 18,
        attribution: '<a href="http://www.mapquest.com">MapQuest</a>'
    })
    
    base_layers.push(mq_tiles)
    mq_tiles.addTo(_map);

}

function draw_resize_control () {
    
    var box = self._node.append('div')
        .classed('n_map_overlay',true)
    
    box.append('label')
            .text('X Size:')
    
    box.append('input')
        .attr('class','mapx')
    
    box.append('label')
            .text('Y Size:')
    
    box.append('input')
        .attr('class','mapy')
    
    box.append('button')
        .text('Resize!')
        .attr('data-owner',self._spec.id)
        .on('click',function (d) {
            var w = Number(cont.select(".mapx")[0][0].value)
            var h = Number(cont.select(".mapy")[0][0].value)
            Layout.registry[this.dataset.owner].size(w,h)
        })
        
    box.append('button')
        .text('Maximize!')
        .attr('data-owner',self._spec.id)
        .on('click',function (d) {
            Layout.registry[this.dataset.owner].maximize()
        })
        
    box.append('button')
        .text('Reset!')
        .attr('data-owner',self._spec.id)
        .on('click',function (d) {
            Layout.registry[this.dataset.owner].reset()
        })

}

function _clear () {

    feature_layers.forEach(function (x) {
        _map.removeLayer(x)
    })

}

function got_geojson (e, d) {
    if (e) {
        alert(e.responseText)
    }
    
    var gj_layer = L.geoJson(d, {
        'style': {'weight': 3}
    })
    feature_layers.push(gj_layer)
    gj_layer.addTo(_map)
}


var _layerchoice;

// Public methods on object
return {
    
    init: function(root, spec) {
        
        self = this
        this._classes = "n_map Container"
        Widget.prototype.init.call(this, root, spec)
        
        _map = null
        
        var cont = this._node.append('div')
            .attr('id',this.relid("container"))
            .attr('class','resizable_map')
            .style('width','100%')
            .style('height','100%')
                
        var layer_control = this._node.append('div')
            .attr('class','map_control')
        
        if (this._spec.maxbutton) {
        
            var size_control = this._node.append('span')
                .attr('class','n_map_size')
            
            var max_button = size_control.append('a')
            
            max_button.classed('pure-button',true)
                .append('i')
                .attr('class','fa fa-arrows-alt')
            
            max_button.on('click',function(d) { self.maximize() })
        }
            
        _map = L.map(this.relid('container'), {
            center: [37.35, -105.23],
            zoom: 6,
            zoomControl: false
        })
        
        L.control.zoom({position: 'topright'}).addTo(_map,true)
            
        _add_base_layer('http://otile2.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.png')
                    
        if (spec.resize_control) { 
            draw_resize_control()
        }
        
        this.update()
        
    },

    clear: function () {
        _clear()
    },
    
    refresh: function () {
        self.update()
    },
    
    reset: function () {
        map._invalidateSize()
    },
    
    event_filter: function(source,event,details) {
        var info = details._info ? details._info : details
        if (event == 'style') {
            return true;
        }
        if (info.objid && info.entitytype) {
            var ent = cloud[info.entitytype](info.objid)
            if (ent.geo_columns) {
                ent.geo_columns(function(e,d) {
                    if (d.length == 0) {
                        return false
                    } else {
                        _layerchoice = info
                        self.add_tiled_geojson(info,d[0])
                    }
                })
            }
        }
        return false
    },
    
    update: function(e,d) {
        
        var mapsize = self._node.select('span.n_map_size')
        var offset = $(mapsize.node()).outerWidth() + 10
        
        var width = $(self._node.node()).innerWidth()
        mapsize
            .style('left',(width-offset)+'px')
            
        _map.invalidateSize()
    },
        
    maximize: function () {
                                
        var width = $(window).innerWidth()
        var height = $(window).innerHeight()
        
        this._node.style('width',width+'px')
        this._node.style('height',height+'px')
        
        this._node.select('div.leaflet-container').style('width',width+'px')
        this._node.select('div.leaflet-container').style('height',height+'px')
        
        //this._node
            //.style('width',width+'px')
            //.style('height',height+'px')
        
        this._node.classed({
            'resizable_map':false,         
            'fullscreen_map':true
        })
        
        this._node.style('position','absolute')
        
        _map.invalidateSize()
        
        var size_control = this._node.select('span.n_map_size')
        size_control.selectAll('*').remove()
        
        var norm_button = size_control.append('a')
        
        norm_button.classed('pure-button',true)
            .append('i')
            .attr('class','fa fa-compress')
        
        norm_button.on('click',function(d) { self.normalize() })
        
        maximized = true        
        this.update()
    },
    
    normalize: function () {
        maximized = false
        
        var size_control = this._node.select('span.n_map_size')
        size_control.selectAll('*').remove()
        
        var cont = self._node.select('#'+self.relid("container"))
            .style('width','100%')
            .style('height','100%')
        
        var max_button = size_control.append('a')
        
        max_button.classed('pure-button',true)
            .append('i')
            .attr('class','fa fa-arrows-alt')
        
        max_button.on('click',function(d) { self.maximize() })
        
        self.update()
    },
    
    size: function (w,h) {
        
        if (width === null && height === null && !w && !h) {
            return 'fullscreen';
        }
        
        if (!w && !h) {
            return {'width':width,'height':height}
        }
        
        var box = d3.select('#'+spec.id)
        
        if (box.classed('fullscreen_map')) {
            this.reset()
        }
        
        box.classed({
            'fullscreen_map':false,
            'resizable_map':true
        })
        
        width = w
        height = h
                
        box.style('width',w+'px')
        box.style('height',h+'px')
        
        this.update()
        
    },
    
    on_click: function (e,viewid,feature) {
        
        getby_id(function (e,d) {
                chart.update(d[0][1],d[1][1])
                rowviewer.update(d)
            },{
                'ids': feature.properties.rowid,
                'viewid':viewid,
                'alias':true
        })
    
    },
        
    add_base_layer: function (urltempl) {
        _add_base_layer(urltempl)
    },
    
    add_geojson: function (url) {
        d3.json(url,got_geojson)
    },
    
    style: function (details) {
        if (arguments.length > 0) {
            stroke = details.stroke
            fill = details.fill
            _style = {
                "clickable": true,
                "color": details.stroke,
                "fillColor": details.fill,
                "weight": 2,
                "opacity": 0.5,
                "fillOpacity": 0.5
            };

            _hover_style = {
                "clickable": true,
                "color": details.stroke,
                "fillColor": details.fill,
                "weight": 3,
                "opacity": 0.9,
                "fillOpacity": 0.3
            };
            self.add_tiled_geojson(_layerchoice)
        } else {
            _style = {
                "clickable": true,
                "color": stroke,
                "fillColor": fill,
                "weight": strokewidth,
                "opacity": 0.5,
                "fillOpacity": 0.5
            };

            _hover_style = {
                "clickable": true,
                "color": stroke,
                "fillColor": fill,
                "weight": strokewidthhover,
                "opacity": 0.9,
                "fillOpacity": 0.3
            };
        }
        
    },
    
    add_tiled_geojson: function (info,geocol) {
        
        var objid = info.objid
        var etype = info.entitytype
        
        this.clear()
        
        if (geocol) {
            _geocol = geocol
        } else {
            geocol = _geocol
        }
        
        if (geocol._info.datatype == 'MultiLine'){
            strokewidth = 4
            strokewidthhover = 8
            self.style()
        } else {
            strokewidth = 2
            strokewidthhover = 3
            self.style()
        }
                
        var hoverStyle = {
            "fillOpacity": 0.5
        };
        
        var geojsonURL = 'http://ubupgbeta:5000/'+ etype + '/' + objid + '/tile/{x}/{y}/{z}/'
        
        var geojsonMarkerOptions = {
            radius: 4,
            fillColor: "#1B1BC7",
            color: "#000",
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        };
        
        var laststyle;
            
        var gj_layer = new L.TileLayer.GeoJSON(geojsonURL, {
                clipTiles: false,
                unique: function (feature) {
                    return feature.properties.rowid;
                },
            },{
                pointToLayer:function (feature, latlng) {
                    var marker = L.circleMarker(latlng, geojsonMarkerOptions);
                    marker.on('click',function(e){
                        Model.respond(self,'selectrow',{
                            'rowid':feature.properties.rowid,
                            'objid':objid
                        })
                    })
                    return marker
                },
            
                onEachFeature: function (feature, layer) {
                    layer.on('click', function (e) {
                        Model.respond(self,'selectrow',{
                            'rowid':feature.properties.rowid,
                            'objid':objid
                        })
                    })
                    layer.on('mouseover', function (e) {
                        layer.setStyle(_hover_style)
                    })
                    layer.on('mouseout', function (e) {
                        layer.setStyle(_style)
                    })
                },
                style: function (feature) {
                    if (!feature) {
                    } else if (_style) {
                        laststyle = _style
                    } else if (feature.geometry.geometries[0].type == 'Point') {
                        // Points - doesn't actually do anything now
                        // but I would forget how if I don't leave this in.
                        laststyle = {
                            "clickable": true,
                            "color": "#F40C0E",
                            "fillColor": "#8BDCEB",
                            "weight": 1,
                            "opacity": 0.9,
                            "fillOpacity": 0.7
                        };
                    } else {
                        // Polygons and lines - doesn't actually do anything now
                        // but I would forget how if I don't leave this in.
                        laststyle = {
                            "clickable": true,
                            "color": "#D88717",
                            "fillColor": "#DFE129",
                            "weight": 1,
                            "opacity": 0.5,
                            "fillOpacity": 0.3
                        };
                    }
                    return laststyle
                }
            }
        )
            
        feature_layers.push(gj_layer)
        gj_layer.addTo(_map)
        
        this.update()
        
    }
    
}}());

Layout.widgets.Map = Map
