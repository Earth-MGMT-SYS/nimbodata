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
var joininfo;

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
        var cols = controls.checkboxes_get_selected(self.relid("column_checks"))
        var join = [joininfo.jtbl,[joininfo.jto,'=',joininfo.jcol]]
        var params = {
            'viewid':objid,
            'where':{"all":all_parts,"any":any_parts},
            'order_by':order_parts,
            'limit':200
        }
        if (cols.length > 0) params.cols = cols
        if (join[0]) params.join = join
        Model.respond(self,'select',params)
    },
    
    get_view_name: function () {
        self._node.select('#'+self.relid("gobox"))
            .selectAll('*').remove()
            
        controls.input(self.relid('gobox'),{
            'label':'View Name: ',
            'id':self.relid('viewname')
        })
        
        controls.button(self.relid('gobox'),{
            'label':'Create',
            'icon':'search-plus',
            'on':{"click":function () { self.create_view() }}
        })
    },
    
    create_view: function () {
        var cols = controls.checkboxes_get_selected(self.relid("column_checks"))
        if (cols.length == 0) {
            var params = {
                'viewid':objid,
                'where':{"all":all_parts,"any":any_parts},
                'order_by':order_parts,
            }
        } else {
            var params = {
                'cols':cols,
                'viewid':objid,
                'where':{"all":all_parts,"any":any_parts},
                'order_by':order_parts,
            }
        }
        var join = [joininfo.jtbl,[joininfo.jto,'=',joininfo.jcol]]
        if (join[0]) params.join = join
        var viewname = self._node.select('#'+self.relid('viewname')).node().value
        Model.respond(self,'create_view',{
            name: viewname,
            parent_objid: parent_objid,
            params:params
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
        
        if (!e && !d) {
            return
        }
        
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
                
        var qbox = this._node
        
        qbox.selectAll("*").remove()
        
        qbox
            .classed("shown",true)
            .classed("hidden",false)
            .attr("state","shown")
        
        var cols = dataset.header
        var optmap = d3.map()
        var revmap = d3.map()
        var colopts = []
        for (var i = 0; i < cols.length; i++) {
            var colname = cols[i].name
            colopts.push([colname,colname])
        }
        
        var cbox = controls.expando(self._spec.id,{
            id:self.relid('colbox'),
            label:'Column Control'
        })
        
        controls.checkboxes(self.relid("colbox"),{
            "id":self.relid("column_checks"),
            "options":colopts
        })
        
        cbox.append('br')
        cbox.append('br')
        
        var wbox = controls.expando(self._spec.id,{
            id:self.relid('wherebox'),
            label:'Filter Control'
        })
                    
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
            "id":this.relid("filter_stmt")
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
                
        var obox = controls.expando(self._spec.id,{
            id:self.relid('orderbox'),
            label:'Sort Control'
        })
        
        controls.feedback(this.relid("orderbox"),{
            "label":"Order by : ",
            "id":this.relid("order_stmt"),
        })
        
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
        
        var jbox = controls.expando(self._spec.id,{
            id:self.relid('join_box'),
            label:'Join Control'
        })
        
        var jtbl_outer = jbox.append('span')
            .attr('id',self.relid('jtbl_outer'))
        
        
        
        joininfo = {
            jtbl: jtbl_choice,
            jcol: jcol_choice,
            jto: join_to
        }
        
        var jtbl_choice
        var jcol_choice;
        var join_to = colopts[0][0]
        var jtbl_name;
        
        function jtbl_chosen () {
            jtbl_choice = this.value
            d3.select(this).selectAll('option').each(function () {
                if (this.value == jtbl_choice) {
                    jtbl_name = d3.select(this).text()
                }
            })
            cloud.Database(parent_objid).Table(jtbl_choice).columns(got_jcols)
        }
        
        function got_jcols (e,d) {
            jtbl_outer.selectAll('*').remove()
            var opts = []
            var colchecks = d3.select('#'+self.relid("column_checks"))
            d.forEach(function(d) {
                opts.push([d.objid,d._info.name])
                colchecks.append('label')
                    .classed('argo',true)
                    .text(jtbl_name +"."+d._info.name)
                    .append('input')
                        .attr('type','checkbox')
                        .attr('class','argo')
                        .attr('value',d.objid)
            })
            controls.listbox(self.relid('jtbl_outer'),{
                "id":self.relid('join_table'),
                "default":2,
                "options":opts,
                "on":{
                    "change":function(){
                        jcol_choice = this.value
                        joininfo = {
                            jtbl: jtbl_choice,
                            jcol: jcol_choice,
                            jto: join_to
                        }
                    }
                }
            })      
        }
        
        controls.dropdown_button(self.relid("jtbl_outer"),{
            "label":"Join to : ",
            "icon":"play",
            "id":self.relid("join_to_col"),
            "default":join_to,
            "options":colopts,
            "on":{
                "change":function () { join_to = this.value },
                "click":get_tables
            }
        })
        
        function get_tables() {
            jtbl_outer.selectAll('*').remove()
            cloud.Database(parent_objid).tables(function(e,d) {
                var options = []
                d.forEach(function(d) {
                    options.push([d.objid,d.name])
                })
                
                controls.listbox(self.relid('jtbl_outer'),{
                    "id":self.relid('join_table'),
                    "default":2,
                    "options":options,
                    "on":{
                        "change":jtbl_chosen
                    }
                })
            })
        }
        
        jbox.append('br')
        
        var abox = controls.expando(self._spec.id,{
            id:self.relid('aggbox'),
            label:'Aggregation Control'
        })
        
        controls.feedback(this.relid("aggbox"),{
            "label":"Aggregate : ",
            "id":this.relid("group_display"),
        })
        
        controls.feedback(this.relid("aggbox"),{
            "label":"Group by : ",
            "id":this.relid("group_display"),
        })
        
        controls.input_button(this.relid("aggbox"),{
            "label":"Aggregate : ",
            "id":this.relid("group_stmt"),
            "button_label":"Add",
            "icon":"plus",
            "on":{"click":function () { self.add_to_all() }}
        })
        
        abox.append('br')
        
        var gobox = self._node.append('div')
            .attr('id',self.relid('gobox'))
            .classed('n_gobox',true)
                
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
