// Copyright (C) 2014  Bradley Alan Smith

function Select (root, spec) {
    this.init(root, spec)
}

Select.prototype = Object.create(Widget.prototype)

extend(Select, function () {

var header;
var all_parts;
var any_parts;
var none_parts;
var order_parts;
var limit = 200;
var objid, parent_objid;
var self; // Capture the this of the now for the later when this this is that
var dataset;

return {
    add_to_order: function(value) {
        order_parts.push(value)
        d3.select("#"+self.relid("order_stmt"))
            .text(JSON.stringify(order_parts))
    },
    
    add_to_all: function() {
        var whereStmt = d3.select('#'+self.relid("filter_stmt"))[0][0].value
        all_parts.push(whereStmt)
        d3.select('#'+self.relid("all_stmt"))
            .text(JSON.stringify(all_parts))
    },
    
    add_to_any: function () {
        var whereStmt = d3.select('#'+self.relid("filter_stmt"))[0][0].value
        any_parts.push(whereStmt)
        d3.select('#'+self.relid("any_stmt"))
            .text(JSON.stringify(any_parts))
    },
    
    add_to_none: function () {
        var whereStmt = d3.select('#'+self.relid("filter_stmt"))[0][0].value
        none_parts.push(whereStmt)
        d3.select('#'+self.relid("none_stmt"))
            .text(JSON.stringify(none_parts))
    },
        
    submit_select: function() {
        Model.respond(self,'select',{
            'viewid':objid,
            'where':{"all":all_parts,"any":any_parts},
            'order_by':order_parts,
            'limit':200
        })
    },
    
    get_view_name: function () {
        self._node.select('#'+self.relid("gobox"))
            .selectAll('*').remove()
        controls.input_button(self.relid("limitbox"),{
            "label":"View Name: ",
            'icon':'search-plus',
            'button_label':'Create View',
            "id":self.relid("viewname"),
            "on":{"click":function () { self.create_view() }}
        })
    },
    
    create_view: function () {
        var viewname = self._node.select('#'+self.relid('viewname')).node().value
        var l = d3.select("#"+self.relid("limit")).attr("value")
        Model.respond(self,'create_view',{
            name: viewname,
            parent_objid: parent_objid,
            params:{
                'viewid':objid,
                'where':{"all":all_parts,"any":any_parts},
                'order_by':order_parts,
            }
        })
    },
    
    init: function(root, spec) {
        this._classes = 'argo Container'
        Widget.prototype.init.call(this, root, spec)
        self = this // This is where where capturing the essence of the this
    },
    
    event_filter: function(source,event,details) {
        var match = false
        if (details.entitytype) {
            if (details.entitytype == 'View' || details.entitytype == 'Table') {
                match = true
            }
        } else if (details.viewid) {
            match = true
        } else if (details._info) {
            match = true
        }
        return match
    },
    
    update: function(e, d) {
        all_parts = []
        any_parts = []
        order_parts = []
        
        if (d) dataset = d;
        
        if (dataset && dataset.header[0]) {}
        else {
            Widget.prototype.update.call(this)
            return
        }
        
        if (dataset.info) {
            parent_objid = dataset.info.parent_objid
            objid = dataset.info.objid
            
        } else {
            objid = dataset.header[0].parent_objid
        }
                
        controls.multi(this._spec.id,{
            "id":this.relid("outer_container")
        })
        
        var qbox = this._node
                
        qbox.selectAll("*").remove()
        
        qbox
            .classed("shown",true)
            .classed("hidden",false)
            .attr("state","shown")
        
        var wbox = qbox.append("div")
            .attr("id",this.relid("wherebox"))
            .classed("n_select_inner_container",true)
            .style("float","left")
                    
        controls.feedback(this.relid("wherebox"),{
            "label":"All : ",
            "id":this.relid("all_stmt"),
        })
        
        controls.feedback(this.relid("wherebox"),{
            "label":"Any : ",
            "id":this.relid("any_stmt"),
        })
                
        
        d3.select('#'+this.relid('wherebox'))
            .append('span')
            .attr('id',this.relid('col_filter'))
        
        controls.input(this.relid("col_filter"),{
            "label":"Column Filter",
            "id":this.relid("filter_stmt"),
            
        })        
        
        controls.button(this.relid("col_filter"),{
            "label":"All",
            'icon':'plus',
            "on":{"click":function () { self.add_to_all() }}
        })
        
        controls.button(this.relid("col_filter"),{
            "label":"Any",
            'icon':'plus',
            "on":{"click":function () { self.add_to_any() }}
        })
        
        var obox = qbox.append("div")
            .attr("id",this.relid("orderbox"))
            .classed("n_select_inner_container",true)
            .style("float","left")
            
        controls.feedback(this.relid("orderbox"),{
            "label":"Order by : ",
            "id":this.relid("order_stmt"),
        })
        
        var cols = dataset.header
        var optmap = d3.map()
        var revmap = d3.map()
        var colopts = []
        for (var i = 0; i < cols.length; i++) {
            var colname = cols[i].name
            colopts.push([colname,colname])
        }
        
        var current_option = colopts[0][0]
        var current_opt_node = obox.select('option')
        
        controls.dropdown_button(this.relid("orderbox"),{
            "label":"Order by column: ",
            "id":this.relid("orderby"),
            "button_label":"Add",
            'icon':'plus',
            "default":current_option,
                "options":colopts,
                "on":{
                    "click":function(){
                        self.add_to_order(current_option)
                        var end;
                        obox.selectAll('option').each(function () {
                            if (end) return
                            if (this.value == current_option) {
                                d3.select(this).remove()
                                current_opt_node = obox.select('option').node()
                                current_option = current_opt_node.value
                                end = true
                                return
                            }
                        })
                    },
                    "change":function(){
                        current_option = this.value
                        current_opt_node = this
                    }
                }
        })
        
        obox.append('br')
        var gobox = obox.append('div').attr('id',self.relid('gobox'))
                
        controls.button(self.relid('gobox'),{
            "label":"Select",
            'icon':'search',
            "on":{"click":function () { self.submit_select() }}
        })
        
        controls.button(self.relid('gobox'),{
            "label":"Create View",
            'icon':'search-plus',
            "on":{"click":function () { self.get_view_name() }}
        })
        
        Widget.prototype.update.call(this)
    }
}
} ())

Layout.widgets.Select = Select
