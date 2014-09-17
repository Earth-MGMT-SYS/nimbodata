
function extend(base,child) {
    for (i in child) {
        base.prototype[i] = child[i]
    }
}

function Widget () {}
    
Widget.prototype = {
    
    init: function (root,spec) {
        this._root = root
        this._spec = spec
        this._node = root.append('div')
            .attr('id',spec.id)
        
        this._node.classed(this._classes, true)
    },
    
    node: function () {
        return this._node
    },
    
    relid: function (relid) {
        return this._spec.id + "_" + relid
    },
    
    update: function() {
        
        if (this._spec.browserview && this._spec.browserview.height) {
            Layout.set_size(
                this._node,
                this._spec.browserview.width,
                this._spec.browserview.height
            )
        } else if (this._spec.browserview && this._spec.browserview.containermode) {
            var width = $(this._node.node()).innerWidth()
            var height = $(this._node.node()).innerHeight()
            Layout.set_size(
                this._node,
                width,
                height
            )
            var tabheight = $(this._node.select('div.n_tabs').node()).outerHeight()
            var shownheight = height - tabheight
            this._node.select('.Container')
                .style('height',shownheight+'px')
                .style('width',width+'px')
        }
        
        if (this._spec.children) {
            if (this._spec.children[0].browserview) {}
            if (this._spec.browserview.containermode) {}
            else {
                var heights = []
                this._spec.children.forEach(function (d) {
                    heights.push($('#'+d.id).outerHeight())
                })
                try {
                    var offset = heights.slice(0,-1).reduce(function(a,b) { return a + b })
                    var inner = $(this._node.node()).innerHeight()
                    var lastchild = this._spec.children.slice(-1)[0].id
                    var lastheight = inner - offset + 'px'
                    d3.select('#'+lastchild).style('height',lastheight)
                } catch (e) {
                    /* There are no other siblings in this container */
                }
            }
        }
        
    },
    
    append: function(item) {
        return this._node.append(item)
    },
    
    spec: function () {
        return this._spec
    }
}
