
function Launcher (root, spec) {
    this.init(root,spec)
}

Launcher.prototype = Object.create(Widget.prototype)

Launcher.prototype.clear = function () {
    this._node.selectAll("table").remove()
}

extend(Launcher, function () {

var header_decoder = {}
var dataset;
var header;
var rows;
var self;
var objid;

return {
        
    init: function(root, spec) {
        self = this
        this._classes = "n_launcher_box Container"
        Widget.prototype.init.call(this, root, spec)
               
        d3.select(window).on('popstate',function (d) {
            location.reload()
        })
                    
        this._node
            .append('div')
            .selectAll('h1')
            .data(spec.options)
            .enter().append('h1')
                .text(function(d) { return d[0] })
                .classed('n_launch_item',true)
                .on('click',function(d) {
                    history.pushState({foo:"bar" }, d[0], d[1]);
                    Model.getmodel(d[1],d[2])
                })
        
    },
    
    event_filter: function(source,event,details) {
        if (details.entitytype) {
            if (details.entitytype == 'View' || details.entitytype == 'Table') {
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
    
    update: function(e,dataset) {
                
        if (dataset) {}
        else if (e) { alert(e.responseText) }
        else {
            Widget.prototype.update.call(this)
            return
        }
        
        Layout.refresh()
    }
  }
} (/*Look at me being executed, like a lamb... at... well... nevermind.*/) )

Layout.widgets.Launcher = Launcher
