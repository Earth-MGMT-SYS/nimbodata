
function Title (root,spec) {
    this.init(root,spec)
}

Title.prototype = Object.create(Widget.prototype)

extend(Title, function () {

return {

    init: function(root, spec) {
        this._classes = " Container "
        Widget.prototype.init.call(this, root, spec)
        this._node.style('display','none')
    },
    
    objid: null,
    info: null,
    
    event_filter: function(source,event,details) {
        var info = details.info ? details.info : details
        this.objid = info.objid
        this.info = info
        if (details.rowid) {
            return false
        } else if (event == 'selectrow') {
            this.update(null,details)
            return false
        } else if (event == 'select') {
            this.update(null,details)
            return false
        } else {
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
    
    unmaximize: function(e, d) {
        Model.closemodal()
    },

    update: function(e, d) {
        
        if (d) {}
        else if (e) { alert(e.responseText) }
        else {
            Widget.prototype.update.call(this)
            return
        }
        
        this._node.style('display','block')
        this._node.selectAll('div').remove()
        
        var closeself = this
        this._node.append('div')
            .text(d.alias ? d.alias : d.name)
            .classed('n_maptitle',true)
            .on('click',function () {
                
                history.pushState({'maximize':closeself._spec.id}, 'also', '')
                history.pushState({'maximize':closeself._spec.id}, '', './?fullscreen')
                
                var modalnode = controls.modal()
                if (d.dobj && d.dobj.info) var content = d.dobj.info
                else var content = "<h2>Nothing to see here</h2>"
                
                modalnode.append('div')
                    .html(content)
                    .selectAll('a')
                    .attr('target','_blank')
            })
    }
    
}} () );

Layout.widgets.Title = Title
