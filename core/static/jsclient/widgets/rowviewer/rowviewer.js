
function RowViewer (root,spec) {
    this.init(root,spec)
}

RowViewer.prototype = Object.create(Widget.prototype)

extend(RowViewer, function () {
    
var objid;

return {

    init: function(root, spec) {
        this._classes = " Container "
        Widget.prototype.init.call(this, root, spec)
    },
    
    objid: null,
    
    event_filter: function(source,event,details) {
        if (details.rowid) {
            if (this._spec.subview) {
                return [this.objid,details.rowid]
            } else {
                return true
            }
        } else if (event == 'selectrow') {
            return true
        } else {
            var info = details.info ? details.info : details
            this.objid = info.objid
            var closeself = this
            if (this._spec.subview) {
                Nimbodata.View(info.objid).View(this._spec.subview)
                    .info(function(e,d) {
                        closeself.objid = d.objid
                    })
            }
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
                
        if (dataset[0][0]) {
            var data = d3.map()
            dataset.forEach(function(d) {
                data.set(d[0],d[1])
            })
        } else {
            var data = d3.map(dataset[0])
        }
        
        data.remove('geom')
        
        this._node.selectAll("ul").remove()
        
        this._node.append("ul")
            .classed('n_rowview',true)
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
