// C3 Viewer for Nimbodata
// Copyright (C) 2014  Bradley Alan Smith
// All praise be to C3 and D3

function C3Viewer (root,spec) {
    this.init(root,spec)
}

C3Viewer.prototype = Object.create(Widget.prototype)

extend(C3Viewer, function () {

return {

    init: function(root, spec) {
        this._classes = " Container "
        Widget.prototype.init.call(this, root, spec)
    },
    
    objid: null,
    last_height: null,
    chart: null,
    
    event_filter: function(source,event,details) {
        
        if (this._spec.respondTo == 'select' && event == 'select') {
            var info = details.info ? details.info : details
            if (info.objid) {
                if (info.entitytype == 'Table' || info.entitytype == 'View') {
                    return true
                }
            }
        } else if (details.rowid) {
            if (this._spec.subview) {
                return [this.objid,details.rowid]
            } else if (this._spec.subselect) {
                return {
                    'objid':Nimbodata.View(details.objid).View(this._spec.subselect),
                    'where':['_adm-rowid','=',details.rowid],
                    'limit':500
                }
            } else {
                return true
            }
        } else if (event == 'selectrow') {
            return true
        } else {
            var info = details.info ? details.info : details
            this.objid = info.objid
            var closeself = this
            if (this._spec.subview) {
                Nimbodata.View(info.objid).View(this._spec.subview)
                    .info(function(e,d) {
                        closeself.objid = d.objid
                    })
            } else if (this._spec.subselect) {
                Nimbodata.View(info.objid).View(this._spec.subselect)
                    .info(function(e,d) {
                        closeself.objid = d.objid
                    })
            }
            return false
        }
        
        if (details.entitytype) {
            if (details.entitytype == 'View' || details.entitytype == 'Table') {
                return true
            }
        } else if (details._info) {
            if (details._info.entitytype == 'View' || details._info.entitytype == 'Table') {
                return true
            }
        } else if (details.viewid) {
            return true
        } else if (event == 'refresh') {
            return ['select',{'viewid':this.objid}]
        } else if (event == 'select') {
            return ['select',{'viewid':this.objid}]
        }
        return false
    },
    
    update_timeseries_line: function(drows) {
        
        if (!drows) return
        
        for (var i = 0; i < drows.length; i++) {
            if (drows[i][1] === null) {
                drows[i][1] = 0
            }
        }
        
        var hnode = this._node.node()
        if (Model.viewmode == 'mobile') {
            var cont_height = $(window).innerHeight() * 0.8
            var cont_width = $(window).innerWidth() * 0.95
        } else {
            var cont_height = null,
                cont_width = null
        }
        
        var colors = {}
        colors[drows[0][1]] = 'blue'
        colors[drows[0][2]] = 'red'
        colors[drows[0][3]] = 'orange'
        colors[drows[0][4]] = 'green'
        
        try {
            this.chart = c3.generate({
                size: {
                    height: cont_height,
                    width: cont_width
                },
                bindto: '#'+this._spec.id,
                data: {
                    x: 'x',
                    rows: drows,
                    type: 'area-step',
                    colors: colors
                },
                padding: {
                    top: 20,
                    bottom: 30,
                    right: 40,
                    left: 60
                },
                axis: {
                    x: {
                        type: 'timeseries',
                        tick: {
                            format: '%Y-%m-%d',
                            count: 6
                        }
                    }
                }
            })
        } catch (e) {
            /* Ohs noes */
        }
    },
    
    update_line: function(drows) {
        
        if (!drows) return
        
        var hnode = this._node.node()
        var cont_height = $(hnode).outerHeight()
        var cont_width = $(hnode).outerWidth()
        
        var chart = c3.generate({
            bindto: '#'+this._spec.id,
            data: {
                x: 'x',
                rows: drows
            },
            padding: {
                top: 20,
                bottom: 20,
                right: 20,
                left: 40
            }
        })
    },
    
    update_bar: function(drows) {
        
        if (!drows) return
        
        var hnode = this._node.node()
        var cont_height = $(hnode).outerHeight()
        var cont_width = $(hnode).outerWidth()
        
        var chart = c3.generate({
            bindto: '#'+this._spec.id,
            data: {
                x: 'x',
                rows: drows,
                type: 'bar'
            },
            bar: {
                width: {
                    ratio: 0.8
                }
            },
            padding: {
                top: 20,
                bottom: 20,
                right: 20,
                left: 40
            }
        })
    },
    
    update_gauge: function(drows) {
        
        if (!drows) return
        
        var hnode = this._node.node()
        var cont_height = $(hnode).outerHeight()
        var cont_width = $(hnode).outerWidth()
        
        if (drows[0][1] === null) {
            this._node.append('div')
                .classed('n_chart_nodata',true)
                .text('No data')
            return
        }
        
        try {
            var pct = (drows[0][1] / drows[1][1]) * 100
        } catch (e) {
            this._node.append('div')
                .classed('n_chart_nodata',true)
                .text('No data')
            return
        }
        
        var height = $(window).innerHeight() / 3
        
        this._node.append('div')
            .attr('id',this.relid('chartbox'))
        
        var chart = c3.generate({
            bindto: '#'+this.relid('chartbox'),
            data: {
                columns: [
                    ['Value', drows[0][1]]
                ],
                type: 'gauge'
                /*
                onclick: function (d, i) { console.log("onclick", d, i); },
                onmouseover: function (d, i) { console.log("onmouseover", d, i); },
                onmouseout: function (d, i) { console.log("onmouseout", d, i); }
                */
            },
            gauge: {
                width: 50,
                max: drows[1][1]
            },
            size: {
                height: 250
            }
        })
        //this.refresh()
    },
    
    refresh: function () {
        if (this.objid === null) {
            this._node.style('height','0px')
            this._node.style('width','0px')
        } else if (this.objid) {
            this._node.style('height',this.last_height+'px')
            this._node.style('width',this.last_width+'px')
        }
    },
    
    maximize: function () {
        if (Model.viewmode == 'browser') {
            var width = $(window).innerWidth() - 100,
                height = $(window).innerHeight() - 100
        } else {
            var width = $(window).innerWidth(),
                height = $(window).innerHeight()
        }
        if (this.chart) {
            this.chart.resize({width: width, height: height})
        }
    },
    
    unmaximize: function () {
        this.refresh()
        if (this.chart) this.chart.resize()
    },

    update: function(e, dataset) {
        
        if (dataset) {}
        else if (e) { alert(e.responseText) }
        else {
            Widget.prototype.update.call(this)
            return
        }
        
        if (this._root.viewspec.page && this._root.viewspec.page == 'eventrespond') {
            this._root.active = true
            this._root.maximize()
        }
        
        var chartheight = $(window).innerHeight() / 4
        this._node.style('height',chartheight+'px')
        Widget.prototype.update.call(this)
        
        if (this._spec.xindex) {
            var xindex = this._spec.xindex
        } else {
            var xindex;
            if (dataset.header) {
                dataset.header.forEach(function(d) {
                    if (xindex) return
                    else {
                        if (d.datatype == 'Date') {
                            xindex = d.weight
                        }
                    }
                })
            } else {
                var xindex = 0;
            }
        }
        
        if (this._spec.yindex) {
            var yindex = this._spec.yindex
        } else {
            var yindex = [];
            if (dataset.header) {
                dataset.header.forEach(function(d) {
                    if (d.datatype == 'Integer' || d.datatype == 'Float') {
                        yindex.push(d.weight)
                    }
                })
            } else {
                var yindex = [1];
            }
        }
        
        try {
            var headrow = ['x']
            yindex.forEach(function(i) {
                headrow.push(dataset.header[i].name)
            })
            var drows = [headrow]
            dataset.rows.forEach(function(d) {
                var newrow = [d[xindex]]
                yindex.forEach(function(i) {
                    newrow.push(d[i])
                })
                drows.push(newrow)
            })
        } catch (e) {
            /* eeeee */
        }
        
        this._node.selectAll('*').remove()
        
        if (this._spec.chart_title) {
            this._node.append('div')
                .attr('id',this.relid('chart_title'))
                .classed('n_chart_title',true)
                .text(this._spec.chart_title)
        }
        
        if (!this._spec.chart_type || this._spec.chart_type == 'line') {
            this.update_line(drows)
        } else if (this._spec.chart_type == 'bar') {
            this.update_bar(drows)
        } else if (this._spec.chart_type == 'gauge') {
            this.update_gauge(dataset)
        } else if (this._spec.chart_type == 'timeseries-line') {
            this.update_timeseries_line(drows)
        }
        
        this.last_height = $(this._node.node()).innerHeight()
        this.last_width = $(this._node.node()).innerWidth()
        
    }
    
}} () );

Layout.widgets.C3Viewer = C3Viewer
