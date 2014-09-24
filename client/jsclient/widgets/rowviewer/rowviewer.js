
function RowViewer (root,spec) {
    this.init(root,spec)
}

RowViewer.prototype = Object.create(Widget.prototype)

extend(RowViewer, function () {
    
var self;
var objid;
    
return {

    init: function(root, spec) {
        self = this
        this._classes = " Container "
        Widget.prototype.init.call(this, root, spec)
        self._node.style('display','none')
    },
    
    event_filter: function(source,event,details) {
        if (details.rowid) {
            return true
        } else if (event == 'selectrow') {
            return true
        } else {
            var info = details.info ? details.info : details
            objid = info.objid
            return false
        }
    },

    update: function(e, dataset) {
        
        if (dataset) {}
        else if (e) { alert(e.responseText) }
        else {
            Widget.prototype.update.call(this)
            return
        }
        
        self._node.style('display','block')
        
        if (dataset[0][0]) {
            var data = d3.map()
            dataset.forEach(function(d) {
                data.set(d[0],d[1])
            })
        } else {
            var data = d3.map(dataset[0])
        }
        
        data.remove('geom')
        
        self._node.selectAll("ul").remove()
        
        self._node.append("ul")
            .selectAll("li")
            .data(data.entries())
            .enter().append("li")
                .text(function(data){
                    if (data.key) {
                        return data.key + ": " + data.value
                    }
                })
                .attr('class','row_entry')
    }
    
}} () );

Layout.widgets.RowViewer = RowViewer
