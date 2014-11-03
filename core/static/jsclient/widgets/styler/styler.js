// Copyright (C) 2014  Bradley Alan Smith

function Styler (root, spec) {
    this.init(root, spec)
}

Styler.prototype = Object.create(Widget.prototype)

extend(Styler, function () {

return {
        
    init: function(root, spec) {
        self = this
        this._classes = ' Container '
        if (!spec.overbox) {
            this._classes = this._classes + ' argo '
        }
        Widget.prototype.init.call(this, root, spec)
                
        var color_expando = controls.expando(self._spec.id,{
            "id":self.relid("styleexpando"),
            "label":"Styler"
        })
        
        var fill = controls.color(self.relid("styleexpando"),{
            "id":self.relid("fillcolor"),
            "label":"Fill Color: " + String.fromCharCode(160) + String.fromCharCode(160)
        })
        
        var stroke = controls.color(self.relid("styleexpando"),{
            "id":self.relid("strokecolor"),
            "label":"Stroke Color: "
        })
        
        var go = controls.button(self.relid("styleexpando"),{
            "id":self.relid("go"),
            "label":"Set Style",
            "on":{
                click: function () {
                    Model.respond(self,'style',{
                        'fill':fill.node().value,
                        'stroke':stroke.node().value
                    })
                }
            }
        })
        
    },
    
    event_filter: function(source,event,details) {
        return false;
    },
    
    update: function(e, d) {
        
        if (!e && !d) {
            return
        }
        
        all_parts = []
        any_parts = []
        order_parts = []
        group_parts = []
        
        if (d) dataset = d;
        
        if (dataset && dataset.header[0]) {}
        else {
            Widget.prototype.update.call(this)
            return
        }
        
        self._node.style('display','block')
        
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
        
        if (self._spec.column_control !== false) {
            var cbox = controls.expando(self._spec.id,{
                id:self.relid('colbox'),
                label:'Column Control'
            })
            controls.checkboxes(self.relid("colbox"),{
                "id":self.relid("column_checks"),
                "options":colopts
            })
            cbox.append('br')
        }
        
        if (self._spec.filter_control !== false) {
            var wbox = controls.expando(self._spec.id,{
                id:self.relid('wherebox'),
                label:'Filter Control'
            })
                        
            controls.feedback(self.relid("wherebox"),{
                "label":"All : ",
                "id":this.relid("all_stmt"),
            })
            
            controls.feedback(self.relid("wherebox"),{
                "label":"Any : ",
                "id":this.relid("any_stmt"),
            })
            
            d3.select('#'+self.relid('wherebox'))
                .append('span')
                .attr('id',self.relid('col_filter'))
            
            controls.input(self.relid("col_filter"),{
                "label":"Column Filter",
                "id":self.relid("filter_stmt")
            })        
            
            controls.button(self.relid("col_filter"),{
                "label":"All",
                'icon':'plus',
                "on":{"click":function () { self.add_to_all() }}
            })
            
            controls.button(this.relid("col_filter"),{
                "label":"Any",
                'icon':'plus',
                "on":{"click":function () { self.add_to_any() }}
            })
        }
        
        if (self._spec.order_control !== false) {
            var obox = controls.expando(self._spec.id,{
                id:self.relid('orderbox'),
                label:'Sort Control'
            })
            
            controls.feedback(self.relid("orderbox"),{
                "label":"Order by : ",
                "id":self.relid("order_stmt"),
            })
            
            var current_option = colopts[0][0]
            var current_opt_node = obox.select('option')
            
            controls.dropdown_button(self.relid("orderbox"),{
                "label":"Order by column: ",
                "id":self.relid("orderby"),
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
        }
        
        if (self._spec.join_control !== false) {        
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
            
            
        }
        
        if (self._spec.aggregate_control !== false) {
            var abox = controls.expando(self._spec.id,{
                id:self.relid('aggbox'),
                label:'Aggregation Control'
            })
            
            controls.feedback(this.relid("aggbox"),{
                "label":"Group by : ",
                "id":self.relid("group_stmt"),
            })
            
            var group_by_choice = colopts[0][0];
            var group_by_node;
            controls.dropdown_button(self.relid("aggbox"),{
                "label":"Group by column: ",
                "id":self.relid("group"),
                "button_label":"",
                'icon':'plus',
                "default":group_by_choice,
                "options":colopts,
                "on":{
                    "click":function(){
                        self.add_to_group(group_by_choice)
                        var end;
                        abox.selectAll('option').each(function () {
                            if (this.value == group_by_choice) {
                                group_by_node = this
                                group_by_choice = group_by_node.value
                                d3.select(this).remove()                            
                                return
                            }
                        })
                    },
                    "change":function(){
                        group_by_choice = this.value
                        group_by_node = this
                    }
                }
            })
            
            var aggcol = colopts[0][0];
            controls.dropdown(self.relid("aggbox"),{
                "label":"Aggregate column : ",
                "id":self.relid("group"),
                "button_label":"",
                'icon':'plus',
                "default":group_by_choice,
                "options":colopts,
                "on":{
                    "change":function(){
                        aggcol = this.value
                        aggcol_node = this
                        agg_data = [aggfunc,aggcol]
                    }
                }
            })
            
            var aggfunc = 'avg';
            agg_data = [aggfunc,aggcol]
            controls.dropdown(self.relid("aggbox"),{
                "label":"Aggregate function : ",
                "id":self.relid("group"),
                "button_label":"",
                'icon':'plus',
                "default":'avg',
                "options":[
                    ['avg','Average'],
                    ['max','Maximum'],
                    ['min','Minimum']
                ],
                "on":{
                    "change":function(){
                        aggfunc = this.value
                        agg_data = [aggfunc,aggcol]
                    }
                }
            })
        }
        
        var gobox = self._node.append('div')
            .attr('id',self.relid('gobox'))
            .classed('n_gobox',true)
        
        controls.button(self.relid('gobox'),{
            "label":"Select",
            'icon':'search',
            "on":{"click":function () { self.submit_select_view() }}
        })
        
        if (self._spec.create !== false) {
            controls.button(self.relid('gobox'),{
                "label":"Create View",
                'icon':'search-plus',
                "on":{"click":function () { self.get_view_name() }}
            })
        }
        
        Widget.prototype.update.call(this)
    }
}
} ())

Layout.widgets.Styler = Styler
