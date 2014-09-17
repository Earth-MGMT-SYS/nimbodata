

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
        else return lab = d.name
    };

    function get_id(d) {
        return d.parent_objid + d.name + d.entitytype + d.key;
    };

    var on_click_methods = {
        'add_layer':function(d) {Map.add_tiled_geojson(d.objid)},
        'shout_out':function (d) {alert(d.key)}
    }

    var width = 200,
        height = 200;
        
    var svg, self;
    
    var data = []
    
    var priorities = d3.map();

    priorities.set('Database',1)
    priorities.set('Table',2)
    priorities.set('View',2)
    priorities.set('Column',3)
    priorities.set('Constraint',3)

    var levels = d3.set()

    tree_layout = d3.layout.indent()
      .children(function(d) { return d.values; })
      .nodeSize([10, 25])

    return {
    
        init: function (root, spec) {
            this._classes = 'Overbox'
            Widget.prototype.init.call(this, root, spec)
            
            self = this;
                        
            svg = this._node.append("svg")
                .attr({
                    id:spec.id+'_svg',
                    width: width,
                    height: height
                })
                
            svg.append("g")
                .attr("transform", "translate(10,10)");
        },
        
        event_filter: function (source, event, details) {
            if (details.key) {
                return true
            } else if (event == 'rename' || event == 'drop' || event == 'select') {
                return 'refresh'
            } else {
                return false
            }
        },
        
        update: function (e, d) {
            
            if (d) {
                data = d
            }
            
            if (data && data[0]) {}
            else return
            
            if (e) {
                alert(e.responseText)
            }
                                    
            var nestDatabase = d3.nest()
            var top_type = data[0].entitytype;
                
            for (var i = data.length -1; i >=0; i--)  {
                if (data[i].entitytype == top_type) {
                    objid_to_name.set(data[i].objid,data[i].name)
                    levels.add(data.entitytype)
                    data.splice(i,1)
                }
            }
            
            // Group-by nesting... not quite... but close enough
            [
                function(d) { return d.parent_objid; },
                function(d) { return d.parent_objid + " " + d.entitytype + 's'}
            ].forEach(function(d) { nestDatabase.key(d) })
            
            var data = {
                key: "Nimbodata",
                values: nestDatabase.entries(data)
            };
            
            var nodes = tree_layout(data);
            
            var dwg = this._node.select('g')
            
            dwg.selectAll('*').remove()
            
            labels = dwg.selectAll(".label")
                .data(nodes, get_id);

            labels.enter()
                .append("text")
                .attr({
                  "class": function(d) {
                      return d.Label ? "menu_item" : "menu_category"
                    },
                  dy: ".35em",
                  transform: function(d) { return "translate(" + (d.x - width) + "," + d.y + ")"; }
                })
                .style("font-weight", function(d) { return d.Label ? null : "bold" })
                .text(function(d) { return get_label(d); })
                .attr({
                    'data-owner':this._spec.id,
                    'data-name':get_key,
                    'data-parent_objid': function (d) {return d.parent_objid},
                    'data-objid': function (d) {return d.objid},
                    'data-action': function (d) {return d.action},
                })
                .on('click',function (d) {
                    self.on_click(d)
                })
            
            labels
              .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

            labels.exit()
              .attr("transform", function(d) { return "translate(" + (d.x - 200) + "," + d.y + ")"; })
              .remove()
            
            svg.attr({
                "width":dwg[0][0].getBoundingClientRect().width + 5,
                "height":dwg[0][0].getBoundingClientRect().height + 5
            })
            
        },
            
        on_click: function (d, i) {
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
