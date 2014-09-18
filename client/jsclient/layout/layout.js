
Layout = function () {

return {
    
    registry: {},
    containers: {},
    widgets: {},
    model: null,
            
    init: function (model) {
        this.model = model
        
        var body = d3.select('body')
        var main = body.append('div')
            .attr('id','main')
            
        this.set_outer()
        
        // Recursively walk the doc_structure and create the nodes
        model.forEach(function(node) {
            // Closure required for the main parameter
            node.created = this._add_node(main,node);
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
    
    set_size: function(selector, w, h) {
        var parent = selector.node().parentNode
        var dim = this.dimensions(parent)
        
        if (typeof w == 'string' && w.slice(-1) == '%') {        
            w = String((Number(w.slice(0,w.length - 1)) / 100 * dim[0])) + 'px'
            h = String((Number(h.slice(0,h.length - 1)) / 100 * dim[1])) + 'px'
        }
        
        selector
            .style("width",w)
            .style("height",h)
    },
        
    refresh: function (model) {
        
        if (arguments.length == 0) {
            this.model.forEach(function(item) {
                item.created.refresh()
                if (item.children) this.refresh(item.children)
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


