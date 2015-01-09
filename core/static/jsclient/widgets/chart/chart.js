
function Chart (root,spec) {
    this.init(root,spec)
}

Chart.prototype = Object.create(Widget.prototype)

extend(Chart, function () {

var parseDate = d3.time.format("%Y-%m-%d").parse;

var self;

var margins, 
    height, 
    width;

var rows= null, 
    header = null;

var xScale = null,
    yScale = null;

var xCol, yCol, y2Col;
var xType, yType, y2Type;
var xData = [];
var yData = [];

var data;

//function line_height (d) { return yScale(d[yCol]) }
//function bar_height (d) { return height - yScale(d[yCol]) }

function draw_ui_control (datasource) {
    var box = self._node.insert('div', '#chart');
    box.attr('class', 'pure-form');

    var opts = [];
    
    datasource.header.forEach(function(d){
        opts.push(
            {
                text: d.alias ? d.alias : d.name,
                index: d.weight,
                type: d.datatype
            }
        )
    })

    box.append('label')
            .text('X Source:')
    
    var xSelect = box.append('select') 

    xSelect.on('change', function(d) {
        xCol = this.value;
        xType= getDataType(datasource.header, xCol);
        console.log('Xcol= '+xCol + ' xType= ' + xType);
        self._spec.xindex = xCol;  
        self.redraw()
    })

    xSelect.selectAll('option')
        .data(opts)
        .enter()
        .append('option')
            .text(function(d) {return d.text;})
            .attr('value',function(d) {return d.index;})
            .attr('datatype', function(d) {return d.type;})
   
    box.append('label')
            .text('Y Source:')
    

    var ySelect = box.append('select') 


    ySelect.on('change', function(d) {
        yCol = this.value;
        yType = getDataType(datasource.header, yCol);
        console.log('Ycol= '+yCol + 'yType= ' + yType);
        self._spec.xindex = xCol;  
        self.redraw()
    })

    ySelect.selectAll('option')
        .classed('bleh', true)
        .data(opts)
        .enter()
        .append('option')
            .text(function(d) {return d.text;})
            .attr('value',function(d) {return d.index;})
        .attr('datatype', function(d) {return d.type;})

    if( self._spec.draw_y2_axis) {   
    box.append('label')
            .text('Y2 Source:')

    var y2Select = box.append('select') 

    y2Select.on('change', function(d) {
        y2Col = this.value;
        y2Type = this.datatype;
        console.log('yCol ' + y2Col)
        self.redraw()

    })

    y2Select.selectAll('option')
        .data(opts)
        .enter()
        .append('option')
            .text(function(d) {return d.text;})
            .attr('value',function(d) {return d.index;})
            .attr('datatype', function(d) {return d.type;})
      y2Select[0][0].value = y2Col
    }

     if (self._spec.type_control) {
            draw_type_control()
     }

    xSelect.property( "value", xCol );
    ySelect.property( "value", yCol );
}



function draw_type_control () {
    var box = self._node.insert('div', 'g')
    
    var opts = ['line','bar']
    
    var select = box.append('select')
    
    select.on('change',function(d) {
        self._spec.chart_type = this.value
        self.redraw()
    })
    
    select.selectAll('option')
        .data(opts)
        .enter()
        .append('option')
            .text(function(d) {return d})
            
    select[0][0].value = self._spec.chart_type
}

function draw_resize_control () {
    var box = self._node.append('div')
    
    box.append('label')
            .text('X Size:')
    
    box.append('input')
        .attr('class','chartx')
    
    box.append('label')
            .text('Y Size:')
    
    box.append('input')
        .attr('class','charty')
    
    box.append('button')
        .text('Resize!')
        .attr('data-owner',self._node.attr('id'))
        .on('click',function (d) {
            var w = Number(self._node.select(".chartx")[0][0].value)
            var h = Number(self._node.select(".charty")[0][0].value)
            Layout.registry[this.dataset.owner].size(w,h)
        })
        
    box.append('button')
        .text('Maximize!')
        .attr('data-owner',self._node.attr('id'))
        .on('click',function (d) {
            var w = window.innerWidth - 200;
            var h = window.innerHeight - 200;
            Layout.registry[this.dataset.owner].size(w,h)
        })
        
    box.append('button')
        .text('Reset!')
        .attr('data-owner',self._node.attr('id'))
        .on('click',function (d) {
            Layout.registry[this.dataset.owner].reset()
        })
}

function point_on_click (d) {
    var date = d3.time.format("%Y-%m-%d")(d[0])
    var text = "Observation Date: " + date + "\nValue: " + d[1] + " CFS"
    alert(text)
}

function getDataType(header, index) {
    var type;   
    header.forEach(function(obj) {
        if(obj.weight === parseInt(index)){
            type = obj.datatype;
        }
    });
    return type;
}

function normalizeType(type, data){
    console.log(data);  

    if(type === 'Integer' || type === 'real') {
        return parseInt(data);
    }
    else if (type === 'Float') {
        return parseFloat(data);
    }
    else if (type === 'Date' || type === 'date') {
        data = data.toString(); 
        if(data.length === 4){
            var d = new Date()
            d.setYear(data + '');
            return d;
        }   
        return Date(data);
    }
    else if (type === 'Timestamp') {
        return Date(data);
    }
    else if (type === 'Text') {
        return data;
    }
    else {
        return new Date(data);  

    }
}

function update_line (svg) {        
        
    var line = d3.svg.line()
        .x(function(d) {
            var x = xScale(d[xCol])
            return x; 
        })
        .y(line_height);    
    
    var svg = self._node.select('svg')
    
    svg.append("path")
        .datum(rows)
        .attr("class", "line")
        .attr("transform", "translate(" + margins.left + "," + margins.top + ")")
        .attr("d",line)
        
    svg.selectAll("circle")
        .data(rows)
        .enter()
        .append("svg:circle")
            .attr("cx", function(d) { return xScale(d[xCol]) })
            .attr("cy", line_height)
            .attr("r", 5)
            .attr("transform", "translate(" + margins.left + "," + margins.top + ")")
            .on("click",point_on_click)
}

function update_bar (svg) {
    
    svg.selectAll("rect").data(rows)
        .enter()
        .append("rect")
        .classed("chart_bar",true)
        .attr("x", function (d) {
            //return (w / rows.length) * i;
            return xScale(d[xCol])
        })
        .attr("y", line_height)
        .attr("width", width / rows.length)
        .attr("height", bar_height)
        .attr("fill", function (d) {
            return "rgb(0, 0, 256)";
        })
        .on('click',point_on_click)
    .sort()
        
}

function getData(rows, colIndex) {
    var data = [];
    for(var i = 0; i < rows.length; i++){
        data[i] = rows[i][colIndex];
    }
    console.log('data = ' + data);
    return data;
}



return {
    
    init: function(root, spec) {
        self = this
        this._classes = " Container "
        Widget.prototype.init.call(this, root, spec)
        
        margins = {top: 10, right: 10, bottom: 100, left: 60};
        width = spec.width - margins.left - margins.right;
        height = spec.height - margins.top - margins.bottom;
        
    },
    
    size: function (w, h, m) {
        if ((!w && !h && !m)) {
            return [width,height,margins]
        }
        
        if (m) {
            margins = m;
        }
        
        if (w) {
            width = w - margins.left - margins.right;
        }
        
        if (h) {
            height = h - margins.top - margins.bottom;
        }
        
        self.update(null, data)
    },
    
    reset: function () {
        self.size(
            self._spec.width,
            self._spec.height,
            self._spec.margins ? spec.margins : margins
        )
    },
    
    redraw: function () {
        return self.update(null,data)
    },
    
    title: function(title) {
        if (title) {
            spec.title = title
        }
        else {
            return spec.title
        }
    },
    
    event_filter: function(source,event,details) {
        
        if (self._spec.respondTo == 'select' && event == 'select') {
            var info = details.info ? details.info : details
            if (info.objid) {
                if (info.entitytype == 'Table' || info.entitytype == 'View') {
                    return true
                }
            }
        } else if (details.rowid) {
            if (self._spec.subview) {
                return [self.objid,details.rowid]
            } else if (self._spec.subselect) {
                return {
                    'objid':this.objid,
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
            if (self._spec.subview) {
                Nimbodata.View(info.objid).View(self._spec.subview)
                    .info(function(e,d) {
                        closeself.objid = d.objid
                    })
            } else if (self._spec.subselect) {
                Nimbodata.View(info.objid).View(self._spec.subselect)
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
        var cont_height = $(hnode).outerHeight()
        var cont_width = $(hnode).outerWidth()
        
        var colors = {}
        
        colors[drows[0][1]] = '#ff0000'
        
        var chart = c3.generate({
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
                bottom: 5,
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
            
    update: function (e, dataset) {
        xData = [];
        yData= [];    
        
        if (dataset) {
            data = dataset
        }
        else if (data) {
            dataset = data;
        }
        else if (e) { alert(e.responseText) }
        else {
            Widget.prototype.update.call(self)
            return
        }
    
        if (self._spec.xindex) {
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
        
        if (self._spec.yindex) {
            var yindex = self._spec.yindex
        } else {
            var yindex;
            if (dataset.header) {
                dataset.header.forEach(function(d) {
                    if (yindex) return
                    else {
                        if (d.datatype == 'Integer' || d.datatype == 'Float') {
                            yindex = d.weight
                        }
                    }
                })
            } else {
                var yindex = 1;
            }
        }
        
        try {
            var a = dataset.header[xindex].name, b = dataset.header[yindex].name
            var drows = [['x',b]]
            dataset.rows.forEach(function(d) {
                drows.push([d[xindex],d[yindex]])
            })
        } catch (e) {
            /* eeeee */
        }
        
        self._node.selectAll('*').remove()
        
        
        if (!self._spec.chart_type || self._spec.chart_type == 'line') {
            self.update_line(drows)
        } else if (self._spec.chart_type == 'bar') {
            self.update_bar(drows)
        } else if (self._spec.chart_type == 'gauge') {
            self.update_gauge(dataset)
        } else if (self._spec.chart_type == 'timeseries-line') {
            self.update_timeseries_line(drows)
        }

        if (self._spec.chart_title) {
            self._node.append('div')
                .attr('id',this.relid('chart_title'))
                .classed('n_chart_title',true)
                .text(this._spec.chart_title)
        }


        if (self._spec.ui_control) {
            draw_ui_control(dataset)
        } 
                        
        if (self._spec.resize_control) { 
            draw_resize_control()
            self._node.select(".chartx")[0][0].value = width;
            self._node.select(".charty")[0][0].value = height;
        }
        

    }
    
}} () );

Layout.widgets.Chart = Chart
