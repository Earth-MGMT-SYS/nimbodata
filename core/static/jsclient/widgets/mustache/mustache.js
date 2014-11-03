
function MustacheView (root,spec) {
    this.init(root,spec)
}

MustacheView.prototype = Object.create(Widget.prototype)

extend(MustacheView, function () {

return {

    init: function(root, spec) {
        this._classes = " Container "
        Widget.prototype.init.call(this, root, spec)
        d3.text(spec.template,function (e,d) {
            templ = d
        })
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
        
        if (dataset[0] && dataset[0][0]) {
            var data = {}
            dataset.forEach(function(d) {
                data[d[0]] = d[1]
            })
        } else if (dataset[0]) {
            var data = dataset[0]
        } else {
            return
        }
                
        this._node.selectAll("*").remove()
        var rendered = Mustache.render(templ, data);
        $(this._node.append('div').classed('n_mustache_frame',true).node()).html(rendered);
        
        Widget.prototype.update.call(this)
        
    }
    
}} () );

Layout.widgets.MustacheView = MustacheView
