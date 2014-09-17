function Container (root, spec) {
    this.init(root, spec)
}

Container.prototype = Object.create(Widget.prototype)

extend(Container, function () {
    
    var active = 0;
    var self;
    
    return {
        init: function (root, spec) {
            this._classes = 'Container'
            self = this
            Widget.prototype.init.call(this, root, spec)
        },
        
        update: function (e,d) {
            self = this
            if (this._spec.browserview) {
              if (this._spec.browserview.containermode == 'tabs') {
                  this.tab_update(e,d)
              } else if (this._spec.browserview.containermode == 'h-accordion') {
                  this.accordion_update(e,d)
              }
            }
                
            Widget.prototype.update.call(this)
        }, 
        
        accordion_update: function () {
            var containers = self._node.selectAll('.Container')
                .classed('n_accordion_content',true)
        },
        
        hideall: function () {
            self._node.selectAll('div.Container')
                .classed('hidden',true)
                .classed('shown',false)
        },
                    
        tab_update: function (e,d) {
            var container = d3.select('#'+this._spec.id)
                .classed('TabOuter',true)
            
            var ids = [];
            
            var inner = container.selectAll('.Container')
            inner.each(function(d) {
                ids.push(d3.select(this).attr("id"))
            })
            
            function show (d) {

                var width = $(container.node()).innerWidth()
                var height = $(container.node()).innerHeight()
                var tabheight = $(tabcont.node()).outerHeight()                
                
                container.selectAll('#'+d)
                    .classed('hidden',false)
                    .classed('shown',true)
                    .style('width',width+'px')
                    .style('height',(height-tabheight)+'px')
                    
                Model.respond(self,'refresh',{})
            
            }
            
            container.selectAll('div.n_tabs').remove()
            
            var tabcont = container.insert('div',':first-child')
                .classed('n_tabs',true)
            var tabs = tabcont.append('ul')
                .classed('n_tabs',true)
            var tablist = tabs.selectAll('li').data(ids)
            
            tablist.exit().remove()
            tablist.enter().append('li')
                .classed('n_tabs',true)
                .text(function(d) { return d })
                .on('click',function (d) {
                    self.hideall()
                    show(d)
                })
                
            self.hideall()
            show(container.select('div.Container')[0][0].id)
        }
    }   
}())

Layout.widgets.Container = Container
