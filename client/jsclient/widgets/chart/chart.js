
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

var data;

function line_height (d) { return yScale(d[1]) }
function bar_height (d) { return height - yScale(d[1]) }

function draw_type_control () {
    var box = self._node.append('div')
    
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

function update_line (svg) {        
        
    var line = d3.svg.line()
        .x(function(d) {
            var x = xScale(d[0])
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
            .attr("cx", function(d) { return xScale(d[0]) })
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
        .attr("x", function (d, i) {
            //return (w / rows.length) * i;
            return xScale(d[0]);
        })
        .attr("y", line_height)
        .attr("width", width / rows.length)
        .attr("height", bar_height)
        .attr("fill", function (d) {
            return "rgb(0, 0, 256)";
        })
        .on('click',point_on_click)
        
}



return {
    
    init: function(root, spec) {
        self = this
        this._classes = "Container Overbox"
        Widget.prototype.init.call(this, root, spec)
        
        margins = {top: 10, right: 10, bottom: 40, left: 40};
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
            var first_date = new Date(rows[0][0]);
            var last_date = new Date(rows[rows.length - 1][0])
        }
        catch (e) {
            node.append('h2')
                .text('SORRY, NO DATA!')
            node.append('div')
                .text('Still bushleague.')
            return;
        }
        
        self._node.append('div').text(self._spec.title)
        self._node.append('div').text(self._spec.subtitle)
        
        try {
            rows.forEach(function(d) {
                d[0] = parseDate(d[0]);
                d[1] = d[1];
            });
        }
        catch (e) {
            // This is hack - need proper input handling via query object
        }
        
        var svg = self._node.append("svg")
                .attr("class","datachart")
                .attr("width", width + margins.left + margins.right )
                .attr("height", height + margins.top + margins.bottom )
            .append('g')
                .attr("transform", "translate(" + margins.left + "," + margins.top + ")");
           
        xScale = d3.time.scale()
            .domain([first_date, last_date])
            .range([0,width])

        yScale = d3.scale.linear()
            .domain(d3.extent(rows, function(d) { return d[1]; }))
            .range([height, 0]);
        
        if (self._spec.draw_x_axis) {
        
            xAxis = d3.svg.axis()
                .scale(xScale)
                .orient("bottom")
                .ticks(d3.time.months, 2);

            svg.append('g')
                .attr('class', 'x axis')
                .attr('transform', 'translate(0, ' + height + ')')
                .call(xAxis);
        
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
        
        if (self._spec.type_control) {
            draw_type_control()
        }
    }
    
}} () );

Layout.widgets.Chart = Chart
