
Layout = function () {

return {
    
    registry: {},
    containers: {},
    widgets: {},
    model: null,
    viewmode: null,
            
    init: function (model,viewmode) {
        this.loadmodel(model)
        this.viewmode = viewmode
    },
    
    loadmodel: function(app) {
        this.model = app.elements
        
        if (app.title) {
            d3.select('title').remove()
            d3.select('head').append('title').text(app.title)
        }
        
        var body = d3.select('body')
        
        body.selectAll('div').remove()
        
        var cover = body.append('div')
            .attr('id','cover')
        
        var main = body.append('div')
            .attr('id','main')
            
        this.set_outer()
        
        // Recursively walk the doc_structure and create the nodes
        this.model.forEach(function(node) {
            // Closure required for the main parameter
            if (node.mobileview && node.mobileview.show === false && Model.viewmode == 'mobile') {
                node.created = false
            } else {
                node.created = this._add_node(main,node);
            }
        }, this)
    },
    
    dimensions: function (node) {
        if (node) {
            if (node.node) {
                node = $(node.node())
            } else {
                node = $(node)
            }
            return [node.innerWidth(),node.innerHeight()]
        } else {
            return [$(window).innerWidth(),$(window).innerHeight()]
        }
    },
    
    set_outer: function () {
        var init_dim = this.dimensions()
        
        d3.select('body')
            .style('width',init_dim[0]+'px')
            .style('height',init_dim[1]+'px')
        d3.select('#main')
            .style('width',init_dim[0]+'px')
            .style('height',init_dim[1]+'px')
    },
    
    set_width_pct: function(selector, w) {
        var parent = selector.node().parentNode
        var dim = this.dimensions(parent)
        if (typeof w == 'string' && w.slice(-1) == '%') {        
            w = String((Number(w.slice(0,w.length - 1)) / 100 * dim[0])) + 'px'
        }
        selector
            .style("width",w)
    },
    
    set_height_pct: function(selector, h) {
        var parent = selector.node().parentNode
        var dim = this.dimensions(parent)
        if (typeof h == 'string' && h.slice(-1) == '%') {        
            h = String((Number(h.slice(0,h.length - 1)) / 100 * dim[1])) + 'px'
        }
        selector
            .style("height",h)
    },
        
    refresh: function (model) {
        
        if (arguments.length == 0) {
            this.model.forEach(function(item) {
                if (item.created) {
                    item.created.refresh()
                    if (item.children) this.refresh(item.children)
                }
            }, this)
        } else {
            model.forEach(function(item) {
                item.created.refresh()
                if (item.children) this.refresh(item.children)
            }, this)
        }
    },
    
    _add_node: function (root, node) {
        var created = new this.widgets[node.widget](root,node)
        
        Model.register(created)
        
        this.registry[node.id] = created
        
        if (node.children) {
            // If we have children, recurse!
            node.children.forEach(function(d) {
                // Closure required for the created parameter
                d.created = this._add_node(created,d);
            }, this)
        }
        
        return created
    }
    
}}();


window.onresize = function () {
    Layout.set_outer()
    Layout.refresh()
}


