
function ContentPane (root,spec) {
    this.init(root,spec)
}

ContentPane.prototype = Object.create(Widget.prototype)

extend(ContentPane, function () {

return {

    init: function(root, spec) {
        this._classes = " Container n_contentpane"
        Widget.prototype.init.call(this, root, spec)
        var thiswidget = this
        var editmode = this._node.append('div')
            .attr('id',this.relid('edit'))
            .classed('n_maximize',true)
            .classed('fa',true)
            .classed('fa-pencil',true)
            .on('click',function () { thiswidget.enter_editmode() })
    },
    
    enter_editmode: function() {
        var thiswidget = this
        d3.select('#'+this.relid('edit'))
            .classed('fa-pencil',false)
            .classed('fa-save',true)
            .on('click',function () { thiswidget.exit_editmode() })
        this._node.classed('n_editmode_active',true)
        this._node.select('#'+this.relid('content'))
            .attr('contenteditable',true)
    },
    
    exit_editmode: function() {
        var thiswidget = this
        d3.select('#'+this.relid('edit'))
            .classed('fa-pencil',true)
            .classed('fa-save',false)
            .on('click',function () { thiswidget.enter_editmode() })
        this._node.classed('n_editmode_active',false)
        this._node.select('#'+this.relid('content'))
            .attr('contenteditable',false)
    },
        
    update: function(e, dataset) {
        
        if (dataset) {}
        else if (e) { alert(e) }
        else {
            Widget.prototype.update.call(this)
            return
        }
        
        this._node.select('#'+this.relid('content')).remove()
        this._node.append('div')
            .attr('id',this.relid('content'))
            .html(dataset)
        
        Widget.prototype.update.call(this)
        
    }
    
}} () );

Layout.widgets.ContentPane = ContentPane
