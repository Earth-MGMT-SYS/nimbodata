function Container (root, spec) {
    this.init(root, spec)
}

Container.prototype = Object.create(Widget.prototype)

extend(Container, function () {
    
    var active = 0;
    var self;
    var shown;
    
    return {
        init: function (root, spec) {
            this._classes = 'Container'
            self = this
            Widget.prototype.init.call(this, root, spec)
            
            if (this._spec.browserview) {
              if (this._spec.browserview.containermode == 'tabs') {
                  this.tab_init()
              } else if (this._spec.browserview.containermode == 'v-accordion') {
                  this.v_accordion_update()
              } else if (this._spec.browserview.containermode == 'h-accordion') {
                  this.h_accordion_update()
              }
            }
                
            Widget.prototype.update.call(this)
            
        },
        
        update: function (e,d) {
            if (this._spec.browserview) {
              if (this._spec.browserview.containermode == 'tabs') {
                  this.tab_update(e,d)
              } else if (this._spec.browserview.containermode == 'v-accordion') {
                  this.v_accordion_update(e,d)
              } else if (this._spec.browserview.containermode == 'h-accordion') {
                  this.h_accordion_update(e,d)
              }
            }
                
            Widget.prototype.update.call(this)
        },
        
        refresh: function () {
            if (this._spec.browserview.containermode == 'tabs') {
                this.tab_update()
            }
            Widget.prototype.update.call(this)
        },
        
        h_accordion_update: function () {
            var tiddlywinks = this
            var container = d3.select('#'+this._spec.id)
                .classed('TabOuter',true)
            
            container.selectAll('div.n_h_accordion_tab').remove()
            container.selectAll('div.n_h_accordion_inactive').remove()
                        
            var left_inactive = container.insert('div',':first-child')
                .classed('n_h_accordion_inactive',true)
                .classed('n_h_left',true)
                
            var right_inactive = container.append('div')
                .classed('n_h_accordion_inactive',true)
                .classed('n_h_right',true)
            
            var ids = [];
            var shown = false;
            container.selectAll('.Container').each(function(d) {
                var node = d3.select(this)
                ids.push(node.attr("id"))
                if (node.classed('shown')) {
                    shown = this.id
                }
            })
            
            var totalwidth = $('#'+this._spec.id).innerWidth()
            
            var accordion_update = function () {
                tiddlywinks.h_accordion_update()
            }
            
            var lefttabs = 0;
            var tabwidth = 3;
            container.selectAll('div.Container').each(function () {
                var showntab;
                if (this.id == shown) {
                    shown = true
                    container.insert('div','#'+this.id)
                        .classed('n_h_accordion_tab',true)
                        .classed('n_h_accordion_active',true)
                        .style('left',lefttabs * tabwidth + 'em')
                        .append('span').classed('n_h_accordion_tab_label',true)
                            .text(this.id)
                    
                    lefttabs++;
                    d3.select(this)
                        .classed('shown',true)
                        .classed('hidden',false)
                        .style('left',lefttabs * tabwidth + 'em')
                    return
                } else if (shown === false) {
                    shown = true
                    d3.select(this).classed('shown',true)
                    container.insert('div','#'+this.id)
                        .classed('n_h_accordion_tab',true)
                        .classed('n_h_accordion_active',true)
                        .style('top',lefttabs * tabwidth + 'em')
                        .append('span').classed('n_h_accordion_tab_label',true)
                            .text(this.id)
                        
                    lefttabs++;
                    d3.select(this)
                        .classed('shown',true)
                        .classed('hidden',false)
                        .style('top',lefttabs * tabwidth + 'em')
                    return
                } else if (shown !== true) {
                    var inactive = left_inactive.append('div')
                        .style('left',lefttabs * tabwidth + 'em')
                    lefttabs++;
                } else {
                    var inactive = right_inactive.append('div')
                    lefttabs++;
                }
                
                function hideall () {
                    container.selectAll('div.Container')
                        .classed('hidden',true)
                        .classed('shown',false)
                }
                
                
                
                inactive.classed('n_h_accordion_tab',true)
                    .on('click',function (d) {
                        hideall()
                        d3.select('#'+d3.select(this).text())
                            .classed('shown',true)
                            .classed('hidden',false)
                            
                        accordion_update()
                    })
                    .append('span').classed('n_h_accordion_tab_label',true)
                    .text(this.id)
                        
                d3.select(this)
                    .classed('shown',false)
                    .classed('hidden',true)
            })
            
            var tabwidth = $('.n_h_accordion_tab').outerWidth()
            var newwidth = totalwidth - lefttabs * tabwidth
            
            right_inactive
                .style('left',newwidth + tabwidth +'px')
            
            container.select('div.shown')
                .style('width',newwidth + 'px')
        },
        
        v_accordion_update: function () {
            var tiddlywinks = this
            var container = d3.select('#'+this._spec.id)
                .classed('TabOuter',true)
            
            container.selectAll('div.n_accordion_tab').remove()
            container.selectAll('div.n_v_accordion_inactive').remove()
                        
            var top_inactive = container.insert('div',':first-child')
                .classed('n_v_accordion_inactive',true)
                .classed('n_top',true)
                
            var bottom_inactive = container.append('div')
                .classed('n_v_accordion_inactive',true)
                .classed('n_bottom',true)
            
            var ids = [];
            var shown = false;
            container.selectAll('.Container').each(function(d) {
                var node = d3.select(this)
                ids.push(node.attr("id"))
                if (node.classed('shown')) {
                    shown = this.id
                }
            })
            
            var totalheight = $('#'+this._spec.id).innerHeight()
            
            var accordion_update = function () {
                tiddlywinks.v_accordion_update()
            }
            
            var toptabs = 0;
            var tabheight = 3;
            container.selectAll('div.Container').each(function () {
                var showntab;
                if (this.id == shown) {
                    shown = true
                    container.insert('div','#'+this.id)
                        .classed('n_accordion_tab',true)
                        .classed('n_v_accordion_active',true)
                        .text(this.id)
                        .style('top',toptabs * tabheight + 'em')
                    
                    toptabs++;
                    d3.select(this)
                        .classed('shown',true)
                        .classed('hidden',false)
                        .style('top',toptabs * tabheight + 'em')
                    return
                } else if (shown === false) {
                    shown = true
                    d3.select(this).classed('shown',true)
                    container.insert('div','#'+this.id)
                        .classed('n_accordion_tab',true)
                        .classed('n_v_accordion_active',true)
                        .text(this.id)
                        .style('top',toptabs * tabheight + 'em')
                        
                    toptabs++;
                    d3.select(this)
                        .classed('shown',true)
                        .classed('hidden',false)
                        .style('top',toptabs * tabheight + 'em')
                    return
                } else if (shown !== true) {
                    var inactive = top_inactive.append('div')
                        .style('top',toptabs * tabheight + 'em')
                    toptabs++;
                } else {
                    var inactive = bottom_inactive.append('div')
                    toptabs++;
                }
                
                function hideall () {
                    container.selectAll('div.Container')
                        .classed('hidden',true)
                        .classed('shown',false)
                }
                
                
                
                inactive.classed('n_accordion_tab',true)
                    .text(this.id)
                    .on('click',function (d) {
                        hideall()
                        d3.select('#'+d3.select(this).text())
                            .classed('shown',true)
                            .classed('hidden',false)
                            
                        accordion_update()
                    })
                        
                d3.select(this)
                    .classed('shown',false)
                    .classed('hidden',true)
            })
            
            var newheight = totalheight - toptabs * $('.n_accordion_tab').outerHeight()
            
            container.select('div.shown')
                .style('height',newheight + 'px')
        },
        
        tab_init: function() {
            
            var container = d3.select('#'+this._spec.id)
                .classed('TabOuter',true)
            
            
            
            var tabcont = container.insert('div',':first-child')
                .classed('n_tabs',true)
            
            var ids = [];
            var inner = container.selectAll('.Container')
            inner.each(function(d) {
                ids.push(d3.select(this).attr("id"))
            })
        },
    
        tab_update: function () {
        
            var container = d3.select('#'+this._spec.id)
                .classed('TabOuter',true)
            
            var ids = [];
            var inner = container.selectAll('.Container')
            inner.each(function(d) {
                ids.push(d3.select(this).attr("id"))
            })
            
            container.selectAll('ul.n_tabs').remove()
            var tabs = container.select('div.n_tabs').append('ul')
                .classed('n_tabs',true)   
            
            var tabcont = container.select('ul.n_tabs')
            var tablist = tabcont.selectAll('li.n_tabs')
                .data(ids)
        
            tablist.exit().remove()
            tablist.enter().append('li')
                .classed('n_tabs',true)
                .text(function(d) { return d })
                .on('click',function (d) {
                    hideall()
                    show(d)
                })
                
            function hideall () {
                container.selectAll('div.Container')
                    .classed('hidden',true)
                    .classed('shown',false)
            }
            
            var width = $(container.node()).innerWidth()
            var height = $(container.node()).innerHeight()
            var tabheight = $(tabcont.node()).outerHeight()                
            
            container.selectAll('.Container')
                .style('width',width+'px')
                .style('height',(height-tabheight)+'px')
            
            function show (d) {
                shown = d

                var width = $(container.node()).innerWidth()
                var height = $(container.node()).innerHeight()
                var tabheight = $(tabcont.node()).outerHeight()                
                
                container.selectAll('#'+d)
                    .classed('hidden',false)
                    .classed('shown',true)
                    .style('width',width+'px')
                    .style('height',(height-tabheight)+'px')
                    
                Layout.refresh()
            }            
            
            if (shown) {
            } else {
                hideall()
                try {
                    show(container.select('div.Container')[0][0].id)
                } catch (e) {
                    
                }
            }
        }
    
    }   
}())

Layout.widgets.Container = Container
