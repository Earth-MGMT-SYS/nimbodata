
function ResultViewer (root, spec) {
    this.init(root,spec)
}

ResultViewer.prototype = Object.create(Widget.prototype)

ResultViewer.prototype.clear = function () {
    this._node.selectAll("table").remove()
}

extend(ResultViewer, function () {

var header_decoder = {}
var dataset;
var header;
var rows;
var self;
var objid;

return {
        
    init: function(root, spec) {
        self = this
        this._classes = "ResultViewer Container"
        Widget.prototype.init.call(this, root, spec)
    },
            
    get_label: function(d) {
        return d.alias ? d.alias : d.name;
    },
    
    get_dtype: function(d) {
        return d.datatype;
    },
    
    event_filter: function(source,event,details) {
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
            return ['select',{'viewid':objid}]
        } else if (event == 'select') {
            return ['select',{'viewid':objid}]
        }
        return false
    },
    
    refresh: function () {
        Widget.prototype.update.call(self)
    },
    
    clear: function () {
        self._node.selectAll("table").remove()
    },
    
    update: function(e,dataset) {
        
        if (dataset) {}
        else if (e) { alert(e.responseText) }
        else {
            Widget.prototype.update.call(this)
            return
        }
        
        var header = dataset.header
        
        if (header.slice(-1)[0].name == 'geom') {
            header = header.slice(0,-1)
            var rows = []
            dataset.rows.forEach(function(d) {
                rows.push(d.slice(0,-1))
            })
        } else {
            var rows = dataset.rows
        }        
        
        this._node.selectAll("table").remove()
        
        var dtable = this._node.append("table")
            .attr("id",this.relid("datatable"))
            .attr("state","shown")
            .classed("pure-table pure-table-bordered pure-table-striped",true)
        
        var tiddlywinks = this;
        
        dtable.append('thead').append("tr")
            .selectAll("th")
            .data(header)
            .enter().append("th")
                .text(self.get_label)
                .attr('class',function (d,i) {
                    return 'n_hcol_'+i
                })
                .on('click',function (d) {
                    tiddlywinks.col_selected(this,tiddlywinks,d)
                })
        
        dtable.append('tbody')
            .selectAll("tr")
            .data(rows)
            .enter().append("tr")
                .selectAll("td")
                .data(function (d) { return d })
                .enter().append("td")
                    .text(function (d) { return d })
                    .attr('class',function (d,i) {
                        return 'n_col_'+i
                    })
        
        Widget.prototype.update.call(this)
        Layout.refresh()
    },
    
    insert_single: function () {
        var editRow = d3.selectAll("input.edit_box")[0]
        var insRow = []
        for (var i=0; i < editRow.length; i++) {
            insRow.push(editRow[i].value)
        }
        insert(this.insert_done,insRow)
    },
    
    insert_done: function(e,d) {
        if (e) {
            alert(e.responseText)
        }
        dataviews.show_dataview(d,true)
    },
    
    keypress: function (e) {
        // ENTER
        if (d3.event.keyCode == 13) {
            datatables.insert_single()
        }
        // TAB
        else if (d3.event.keyCode == 9) {
            if (e.pos == header.length - 1) {
                datatables.insert_single()
            }
        }
        // ESCAPE
        else if (d3.event.keyCode == 27) {
            datatables.stop_edit()
        }
        else {
            return false;
        }
    },
    
    stop_edit: function(){
        var id = navtree.get_selected_tree_id()
        var tblid = d3.select("#"+id).selectAll('a').attr("tblid")
        
        d3.select("#toolbar").insert("span", "#stop_edit")
                .attr("class","toolButton")
                .attr("id","edit_dataset")
                .text("Edit Dataset")
                .on("click",function(){toolButton_clicked({'id':'edit_dataset'})})
        
        d3.select("#stop_edit").remove()
        dataviews.show_dataview(tblid)
    },
    
    stop_edit_cell: function(d) {
        var val = d3.select("#"+d.id)[0][0].value
        var cellID = "#datacell_"+d.rowIndex+"x"+d.colIndex
        d3.selectAll(".selected_edit_cell")
            .attr("class","row_cell")
            .select("input").remove()
        d3.select(cellID).text(val)
    },
    
    edit_cell: function(d) {
        d3.event.stopPropagation()

        var e_cell = d3.select("#datacell_"+d.rowIndex + "x" + d.colIndex)
        var orig_text = e_cell.attr("class","selected_edit_cell").text()
        e_cell.attr("class","selected_edit_cell")
              .text("")
        e_cell.append("input")
            .attr("type","text")
            .attr("class","selected_edit_box")
            .attr("id",function(d){
                    d.id = "editcell_"+d.rowIndex+"x"+d.colIndex
                    return d.id
                })
            .attr("value",orig_text)
            .on("blur",function(d){datatables.stop_edit_cell(d)})
        d3.select('input.selected_edit_box')[0][0].focus()
    },
    
    edit_datatable: function () {
        d3.select("#edit_dataset").remove()
        var id = navtree.get_selected_tree_id()
        var tblid = d3.select("#"+id).selectAll('a').attr("tblid")
        if (d3.select("#stop_edit").empty()) {
            d3.select("#toolbar").insert("span", "#add_column")
                .attr("class","toolButton")
                .attr("id","stop_edit")
                .text("Stop Editing")
                .on("click",this.stop_edit)
        }
        var dtable = d3.select("#datatable")
        d3.selectAll(".row_cell")
            .on("click",this.edit_cell)
            
        var tr = dtable.append("tr")
                   .attr("class","editrow")
                   .selectAll("td.edit_cell")
                   .data(header)
                   .enter().append("td")
                        .attr("class","edit_cell")
                    .selectAll("input")
                        .data(function(d){return [d]})
                        .enter().append("input")
                        .attr("type","text")
                        .attr("class","edit_box")
                        .attr("id",function(d) {return "editrow_"+d.pos+"_"+d.label})
                        .on("keypress",this.keypress)
        d3.select('input.edit_box')[0][0].focus()
    },
    
    col_deselect: function () {
        this._node.selectAll("th")
            .classed('header_selected',false)
    },
    
    edit_column: function (d) {
        var nacho;
    },
    
    col_selected: function (node,self,d) {
                
        d3.select('#'+self._spec.id).selectAll("th.header_selected")
            .classed('header_selected',false)
        
        d3.selectAll('td.n_col_selected')
            .classed('n_col_selected',false)
        
        Model.respond(self,'select',d)
        
        var colid = d.objid
        var dtype = d.datatype
        
        d3.selectAll('.n_col_'+node.cellIndex)
            .classed('n_col_selected',true)
                
        d3.select(node)
            .classed('header_selected',true)
        
        d3.select("th.n_results")
            .on('click',self.col_deselect)
        d3.select("th.n_results")
            .on('click',self.col_deselect)
        
        var settings = d3.select("#datatable_container")
            .insert("div","#datatable")
                .attr("class","col_settings_container")
                .attr("id","col_settings_container")
        
        var dtype_options = [
            ['String','String'],
            ['Integer','Integer']
        ]
        
        controls.multi("col_settings_container",{
            "id":"col_widget_box"
        })
        
        controls.input_button("col_widget_box",{
            "label":"Column Name",
            "id":"colname",
            "button_label":"Update Column Name",
            "display":"block",
            "default":d.label,
            "on":{
                "click":function(){
                    return rename_column(colid,widgets.button_get_value(this))
                }
            }
        })
        
        controls.dropdown_button("col_widget_box",{
            "label":"Column Datatype",
            "id":"dtype",
            "button_label":"Update Column Datatype",
            "display":"block",
            "default":d.dtype,
            "options":dtype_options,
            "on":{
                "click":function(){
                    return modify_column(colid,widgets.button_get_value(this))
                }
            }
        })
        
        d3.select("#col_widget_box").append("div")
            .attr("id","cancel_col_settings")
        
        controls.button("cancel_col_settings",{
            "label":"Cancel",
            "on":{
                "click":function() {
                    d3.select("#col_widget_box").remove()
                }
            }
        })
    }    
  }
} (/*Look at me being executed, like a lamb... at... well... nevermind.*/) )

Layout.widgets.ResultViewer = ResultViewer
