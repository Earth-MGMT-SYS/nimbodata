

function MenuTree (root, spec) {
    this.init(root, spec)
}

MenuTree.prototype = Object.create(Widget.prototype)


extend(MenuTree,function () {

    String.prototype.rsplit = function(sep, maxsplit) {
        var split = this.split(sep);
        return maxsplit ? [ split.slice(0, -maxsplit).join(sep) ].concat(split.slice(-maxsplit)) : split;
    }

    var objid_to_name = d3.map();

    function get_key(d) {
        return d.objid ? d.objid : d.key
    };

    function get_label(d) {
        
        
        
        if (d.key) {
            var split = d.key.rsplit(' ',1)[1]
            if (objid_to_name.has(split)) return objid_to_name.get(split)
            else return split
        }
        else return lab = d.alias ? d.alias : d.name
    };

    function get_id(d) {
        return d.parent_objid + d.name + d.entitytype + d.key;
    };

    var on_click_methods = {
        'add_layer':function(d) {Map.add_tiled_geojson(d.objid)},
        'shout_out':function (d) {alert(d.key)}
    }
    
    var margin = {top: 30, right: 20, bottom: 30, left: 20},
        width = 960 - margin.left - margin.right,
        barHeight = 20,
        barWidth = width * .8;
        
    var i = 0,
        duration = 400,
        root;

    var width = 200,
        height = 200;
        
    var svg,
        g;
    
    var self;
    
    var data,
        orig;
    
        
    var diagonal = d3.svg.diagonal()
        .projection(function(d) { return [d.y, d.x]; });
    
    var priorities = d3.map();

    priorities.set('Database',1)
    priorities.set('Table',2)
    priorities.set('View',2)
    priorities.set('Column',3)
    priorities.set('Constraint',3)

    var levels = d3.set()

    var tree = d3.layout.tree()
        .children(function(d) { return d.values; })
        .nodeSize([0, 10]);
        
    function click(d) {
                
        if (d.values) {
            d._values = d.values;
            d.values = null;
        } else {
            d.values = d._values;
            d._values = null;
        }
        
        self.draw(data);
    }
    
    function nodeclass(d) {
        return d._values ? "n_closed_branch" : d.values ? "n_open_branch" : "n_leaf";
    }
    
    function nodeicon (d) {
        return d._values ? '\uf105' : d.values ? '\uf107' : ''
    }

    return {
    
        init: function (root, spec) {
            this._classes = ' Container n_menu_container '
            Widget.prototype.init.call(this, root, spec)
            
            self = this;
            
            svg = this._node.append("svg")
                .attr({
                    id:spec.id+'_svg',
                    width: width,
                    height: height
                })
                
            g = svg.append("g")
                .attr("transform", "translate(10,10)");
        },
        
        event_filter: function (source, event, details) {
            if (source == self) {
                return false
            }
            if (details.key) {
                return true
            } else if (event == 'rename' || event == 'drop' || event == 'select') {
                if (details.entitytype == 'Column') {
                    return false
                }
                return 'refresh'
            } else {
                return false
            }
        },
        
        draw: function(source) {
          
          var nodes = tree.nodes(data);

          var height = nodes.length * barHeight

          svg.transition()
              .duration(duration)
              .attr("height", height);

          d3.select(self.frameElement).transition()
              .duration(duration)
              .style("height", height + "px");

          // Compute the "layout".
          nodes.forEach(function(n, i) {
            n.x = i * barHeight;
          });
        
          var node = g.selectAll("g.node")
              .data(nodes, function(d) { return d.id || (d.id = ++i); });

          var nodeEnter = node.enter().append("g")
              .attr("class", "node")
              .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
              .style("opacity", 1e-6);

          // Enter any new nodes at the parent's previous position.
          nodeEnter.append("rect")
              .attr("y", -barHeight / 2)
              .attr("height", barHeight)
              .attr("width", barWidth)
              .attr('class',nodeclass)
              .on("click", self.on_click);

          nodeEnter.append('text')
            .attr('font-family', 'FontAwesome')
            .attr('font-size', function(d) { return '1em'} )
            .attr("dy", 3.5)
            .attr("dx", 5.5)
            .classed('n_tree_icon',true)
            .text(nodeicon); 

          nodeEnter.append("text")
              .attr('class',nodeclass)
              .attr("dy", 3.5)
              .attr("dx", 25)
              .text(get_label)
              .classed('n_tree_label',true)
            

          // Transition nodes to their new position.
          nodeEnter.transition()
              .duration(duration)
              .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
              .style("opacity", 1);

          node.transition()
              .duration(duration)
              .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
              .style("opacity", 1)
            .select("rect")
              .attr('class',nodeclass)
              
          node.select('text.n_open_branch').attr('class',nodeclass)
          node.select('text.n_closed_branch').attr('class',nodeclass)
          node.select('text.n_leaf').attr('class',nodeclass)
          node.select('text.n_tree_icon').text(nodeicon)

          // Transition exiting nodes to the parent's new position.
          node.exit()
              .style("opacity", 1e-6)
              .remove();
          
          // Stash the old positions for transition.
          nodes.forEach(function(d) {
            d.x0 = d.x;
            d.y0 = d.y;
          });
          
          self._node.style('height',height)
          
        },
        
        update: function (e, d) {
            
            if (d && d[0]) {}
            else return
            
            if (e) {
                alert(e.responseText)
            }
     
            var nestDatabase = d3.nest()
            var top_type = d[0].entitytype;
                
            for (var i = d.length -1; i >=0; i--)  {
                if (d[i].entitytype == top_type) {
                    objid_to_name.set(d[i].objid,d[i].name)
                    levels.add(d.entitytype)
                    d.splice(i,1)
                }
            }
            
            // Group-by nesting... not quite... but close enough
            nestDatabase.key(function(d) { return d.parent_objid; })
                
            nestDatabase.key(function(d) {return d.parent_objid + " " + d.entitytype + 's'})
                .sortValues(function (a,b) {
                    var akey = a.name
                    var bkey = b.name
                    return d3.ascending(akey,bkey)
                })
            
            data = {
                key: "Nimbodata",
                values: nestDatabase.entries(d)
            };
            
            data.x0 = 0;
            data.y0 = 0;
            
            self.draw(data)
            
        },
            
        on_click: function (d, i) {
            
            if (d.values) {
                d._values = d.values;
                d.values = null;
            } else {
                d.values = d._values;
                d._values = null;
            }
            
            self.draw(data); 
            
            if (d.key) {
                if (d.key.split(' ').length > 1 || d.key == 'Nimbodata') {
                    // This is not an entity - it is a rollup group or root.
                    return
                }
                else {
                    // This is something we can work with.
                    Model.respond(self,'select',d)
                    return
                }
            }
            Model.respond(self,'select',d)
        }
    }
}())

Layout.widgets.MenuTree = MenuTree
