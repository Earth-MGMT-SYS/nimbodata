
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
        
        if (spec.collapsible === true) {
            this._node = controls.expando(root,{
                id: spec.id,
                label: spec.label ? spec.label : spec.id,
                overbox: spec.overbox
            })
        } else {
            this._node = root.append('div')
                .attr('id',spec.id)
            if (spec.overbox) this._node.classed('Overbox',true)
        }
        
        if (spec.reloadable) {
            var thiswidget = this
            var reload = this._node.append('div')
                .attr('id',this.relid('reload'))
                .classed('n_maximize',true)
                .classed('fa',true)
                .classed('fa-refresh',true)
                .on('click',function () { thiswidget.reload() })
        }
        
        if (Model.viewmode == 'browser') {
            var viewspec = this._spec.browserview
        } else if (Model.viewmode == 'mobile') {
            if (this._spec.mobileview) {
                var viewspec = this._spec.mobileview
            } else {
                var viewspec = this._spec.browserview
            }
        }
        
        if (viewspec && viewspec.page && viewspec.page != 'root') {
            this.active = false
            this._node.style('display','none')
        }
        
        if (!viewspec) viewspec = null
        this.viewspec = viewspec
        
        this._node.classed(this._classes, true)
    },
    
    active: true,
    viewspec: null,
    
    node: function () {
        return this._node
    },
    
    relid: function (relid) {
        return this._spec.id + "_" + relid
    },
    
    refresh: function() {
        this.update()
    },
    
    reload: function () {
        var src = this._spec.datasource
        var thiswidget = this
        if (src.slice(0,4) == 'http' || src.slice(0,1) == '.') {
            d3.json(src,function (e,d) {
                thiswidget.update(e,d)
            })
        } else {
            if (src instanceof Array) {
                n_get(src,thiswidget.update)
            } else {
                cloud[src](function (e,d) {
                    thiswidget.update(e,d)
                })
            }
        }
    },
    
    update: function() {
        
        var viewspec = this.viewspec
        
        if (!this.active) {
            this._node.style('display','none')
            return
        }
        
        if (viewspec && viewspec.height == 'natural') {
            this._node.style('width','initial').style('height','initial')
            return
        }
        
        if (viewspec && viewspec.height) {
            Layout.set_height_pct(
                this._node,
                viewspec.height
            )
            Layout.set_width_pct(
                this._node,
                viewspec.width
            )
        } else if (viewspec && viewspec.containermode) {
            var width = $(this._node.node()).innerWidth()
            var height = $(this._node.node()).innerHeight()
            Layout.set_height_pct(
                this._node,
                viewspec.height
            )
            Layout.set_width_pct(
                this._node,
                viewspec.width
            )
            var tabheight = $(this._node.select('div.n_tabs').node()).outerHeight()
            var shownheight = height - tabheight
            this._node.selectAll('.Container')
                .style('height',shownheight+'px')
                .style('width',width+'px')
        }
        
        if (this._spec.children) {
            if (this._spec.children[0].browserview) {}
            else if (viewspec && viewspec.containermode) {}
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
