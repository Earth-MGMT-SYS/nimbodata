
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

function line_height (d) { return yScale(d[yCol]) }
function bar_height (d) { return height - yScale(d[yCol]) }

function draw_ui_control (datasource) {
    var box = self._node.insert('div', ':first-child');
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
    console.log( opts);
    box.append('label')
            .text('X Source:')
    
    var xSelect = box.append('select') 

    xSelect.on('change', function(d) {
		xCol = this.value;
		xType= getDataType(datasource.header, xCol);
		console.log('Xcol= '+xCol + ' xType= ' + xType);
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

    xSelect[0][0].value = xCol
    ySelect[0][0].value = yCol
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
        
        margins = {top: 10, right: 10, bottom: 50, left: 60};
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
    
    event_filter: function(title) {
        true
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
    
        rows = dataset.rows
        header = dataset.header
        
        self._node.selectAll('*').remove()
	try {
	    console.log('rows = ' + rows);
//j/           var upper_bound = normalizeType(xType, data[rows.length-1] || rows[rows.length - 1][xCol]);
        }
        catch (e) {
            self._node.append('h2')
                .text('SORRY, NO DATA!')
            self._node.append('div')
                .text('Still bushleague.')
            return;
        }
        self._node.append('div').text(self._spec.title)
        self._node.append('div').text(self._spec.subtitle)
        
	try {
            rows.forEach(function(d) {
		if(xType === 'Date' || xType === 'date') {
			var date  = normalizeType(xType, d[xCol]);
			d[xCol] = date	
			console.log(d[xCol] + '!!!!!!!!!')	
			xData.push(date)
		}
		else {
		        xData.push( normalizeType(xType, d[xCol]));
		}

                 yData.push(normalizeType(yType, d[yCol]))
            });
        }
        catch (e) {
            // This is hack - need proper input handling via query object
       		console.log(e); 
	}
 	console.log('xData= ' + xData);
	console.log('yData= ' + yData);

       
        var svg = self._node.append("svg")
                .attr("class","datachart")
                .attr("width", width + margins.left + margins.right )
                .attr("height", height + margins.top + margins.bottom )
            .append('g')
                .attr("transform", "translate(" + margins.left + "," + margins.top + ")");
           
	if(xType === 'Timestamp' || xType === 'Date') {
        	var lower_bound = d3.min(xData);
		var upper_bound = d3.max(xData);
		xScale = d3.time.scale()
            	    .domain([lower_bound, upper_bound])
            	    .range([0,width])
	}
	else if(xType === 'Text'){
		xScale = d3.scale.ordinal()
			.domain(xData)
			.rangeRoundBands([0, width], .9)
	}
	else {
		xScale = d3.scale.linear()
		    .domain(d3.extent(xData, function(d){ return d}))		    		    .range([0, width])
	}
	
	if(yType === 'Timestamp' || yType === 'Date') {
        	var lower_bound = d3.min(yData);
		var upper_bound = d3.max(yData);	
		yScale = d3.time.scale()
            	    .domain([lower_bound, upper_bound])
            	    .range([height,0])
	}
	else if(yType === 'Text'){
		yScale = d3.scale.ordinal()
			.domain(yData.sort())
			.rangeRoundBands([height, 0], .1)
	}
	else {
	var yMax= d3.max(yData, function(d) { return d});	
        yScale = d3.scale.linear()
            .domain([0,yMax])
            .range([height, 0]);
	}
       console.log('yScale' + yScale) 
        if (self._spec.draw_x_axis) {
        
            xAxis = d3.svg.axis()
                .scale(xScale)
                .orient("bottom")
	    if(xType === 'Date'){
                xAxis.ticks(d3.time.years, 5);
	    }
            svg.append('g')
                .attr('class', 'x axis')
                .attr('transform', 'translate(0, ' + height + ')')
                .call(xAxis)
		.selectAll("text")
		    .style("text-anchor", "end")
		    .attr("dx", "-.8em")
		    .attr("dy", ".15em")
		    .attr("transform", function(d) {
				return "rotate(-65)"
			});
        
        }
        
        if (self._spec.draw_y_axis) {
            
            yAxis = d3.svg.axis()
                .scale(yScale)
                .orient("left");
                            
            svg.append('g')
                .attr('class', 'y axis')
                .call(yAxis);    
        
        }
        
        if (self._spec.chart_type == 'bar') {
            update_bar(svg);
        }
        else if (self._spec.chart_type == 'line') {
            update_line(svg);
        }
                        
        if (self._spec.resize_control) { 
            draw_resize_control()
            self._node.select(".chartx")[0][0].value = width;
            self._node.select(".charty")[0][0].value = height;
        }
        
       	
	if (self._spec.ui_control) {
	    draw_ui_control(dataset)
	}
    }
    
}} () );

Layout.widgets.Chart = Chart
