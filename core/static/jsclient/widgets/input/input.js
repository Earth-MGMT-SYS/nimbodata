
function Input (root, spec) {
    this.init(root,spec)
}

Input.prototype = Object.create(Widget.prototype)

Input.prototype.clear = function () {
    this._node.selectAll("table").remove()
}

extend(Input, function () {

var header_decoder = {}
var dataset;
var header;
var rows;
var self;
var objid;

return {
        
    init: function(root, spec) {
        JSONEditor.defaults.theme = 'pure';
        JSONEditor.defaults.iconlib = 'fontawesome4';
        
        self = this
        this._classes = "Input Container"
        Widget.prototype.init.call(this, root, spec)
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
    
    update: function(e,dataset) {
                
        if (dataset) {}
        else if (e) { alert(e.responseText) }
        else {
            Widget.prototype.update.call(this)
            return
        }
        
        self._node.selectAll('*').remove()
        
        var rows = dataset.rows
        var header = dataset.header
        
        var schema = {
            'title':dataset.info.name,
            'type':'object',
            'id':this._spec.id,
            'format':'grid',
            'properties':{}
        }
        
        var fields = schema.properties
                
        var dtconv = {
            'Text':'string',
            'Float':'number',
            'Integer':'number'
        }
        
        dataset.header.forEach(function (d) {
            var dtype = dtconv[d.datatype] ? dtconv[d.datatype] : 'object'
            fields[d.name] = {
                'type': dtype,
                'name': d.name,
                'title': d.alias ? d.alias : d.name
            }
        })
        
        function get_by_index (index) {
            var retVal = {}
            for (var i = 0; i < dataset.header.length; i++) {
                var numrows = dataset.rows.length
                if (index >= 0) {
                    retVal[dataset.header[i].name] = dataset.rows[index][i]
                }
            }
            return retVal
        }
        
        var initial = get_by_index(0)
        
        var opts = {}
        for (var k in this._spec) {
            if (k == 'id' || k == 'widget' || k == 'browserview') {
                continue
            } else {
                opts[i] = this._spec[k]
            }
        }
        
        opts.schema = schema
        opts.startval = initial
        opts.disable_edit_json = true
        opts.disable_properties = true
        
        
        
        var editor = new JSONEditor(this._node.node(),opts)
        
        var buttons = this._node.select('h3')
            .append('span')
            .classed('n_button_box',true)
        
        function load_by_index (index) {
            editor.setValue(get_by_index(index))
        }
        
        function clear () {
            var blank = {}
            for (var i in schema.properties) {
                blank[i] = ''
            }
            editor.setValue(blank)
        }
        
        var current_index = 0
        
        function first () {
            current_index = 0
            return load_by_index(0)
        }
        
        function back () {
            if (current_index > 0) {
                current_index--;
                return load_by_index(current_index)
            }
        }
        
        function next () {
            if (current_index < dataset.rows.length - 1) {
                current_index++;
                return load_by_index(current_index)
            }
        }
        
        function last () {
            current_index = rows.length - 1
            return load_by_index(current_index)
        }
        
        function reset () {
            return load_by_index(current_index)
        }
        
        var control_buttons = [
            ['Submit','play',function () { console.log( editor.getValue() )}],
            ['Reset','refresh',reset],
            ['Clear','times',clear],
            ['First','fast-backward',first],
            ['Back','backward',back],
            ['Next','forward',next],
            ['Last','fast-forward',last]
        ]
        
        control_buttons.forEach(function (d) {
            var button = buttons.append('a')
                .classed('pure-button',true)
                .classed('n_input_button',true)
                .on('click', d[2])
            
            button.append('i')
                .classed('fa',true)
                .classed('fa-'+d[1],true)
            
            button.append('span')
                .text(d[0])
        })
        
        editor.on('change',function() {
            var errors = editor.validate()
            if (errors.length) {
                alert('Validation Error')
            }
        })
        
        Widget.prototype.update.call(this)
    }
  }
} (/*Look at me being executed, like a lamb... at... well... nevermind.*/) )

Layout.widgets.Input = Input
