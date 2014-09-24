function EntityMenu (root, spec) {
    this.init(root, spec)
}

EntityMenu.prototype = Object.create(Widget.prototype)

extend(EntityMenu, function () {
    
    var active = 0;
    var self;
    var menu, feedback;
    var objid;
        
    return {
        init: function (root, spec) {
            self = this
            this._classes = 'Container'
            Widget.prototype.init.call(this, root, spec)
            
            var container = this._node.append('div')
                .attr('id',this.relid('container'))
                
            container.append('span')
                .attr('id',this.relid('label'))
                .classed('n_menu_label',true)
                .style('display','none')
            
        },
        
        event_filter: function(source,event,details) {
            var match = false
            if (details.entitytype) {
                if (details.entitytype == 'Table' || details.entitytype == 'View') {
                    // We will tag along with everything else, what we need is
                    // in the results.
                    return true
                } else {
                    // There's no select here, so we need to get the entity info.
                    match = ['info',details]
                }
            } else if (details.key) {
                // We need the entity info, but it was a rollup node.
                match = ['info',details.key]
            } else if (details.viewid) {
                match = ['info',details.viewid]
            }
            return match
        },
                    
        update: function (e, dataset) {
            
            if (dataset) {}
            else if (e) { alert(e.responseText) }
            else {
                Widget.prototype.update.call(this)
                return
            }
            
            var info = dataset.info ? dataset.info : dataset
            
            var cont = d3.select('#'+self.relid('container'))
                .style('display','block')
            
            self._node.selectAll('a.n_menu_button').remove()
            self._node.selectAll('div.argo').remove()
            self._node.selectAll('.n_entity_control').remove()
            self._node.selectAll('.n_entity_control_container').remove()
            
            // The various event handlers for menu buttons... like click...
            var on = {
                click: function () {
                    var action = d3.select(this).attr('action')
                    var container = d3.select('#'+self.relid('container'))
                    if (action == 'drop') {
                        var really = confirm("Really drop " + info.name + " ? ")
                        if (really) {
                            cloud.Entity(objid).drop(function(e,d) {
                                var parent = cloud.Entity(info.parent_objid)
                                    .info(function(e,d) {
                                        Model.respond(self,'select',d)
                                    })
                            })
                        } else {
                            return
                        }
                    } else if (action == 'rename') {
                        container
                            .style('display','none')
                        
                        var rename_control = self._node.append('div')
                            .attr('id',self.relid("rename_controls"))
                            .classed('n_entity_control',true)
                            
                        controls.input(self.relid("rename_controls"),{
                            'label':'Rename: ',
                            'id':self.relid('rename_input'),
                            'default':info.name
                        })
                        
                        controls.button(self.relid("rename_controls"),{
                            "label":"Submit",
                            "icon":"play",
                            "id":self.relid('submit_rename'),
                            "on":{ click:function () {
                                    var newname = d3.select('#'+self.relid('rename_input'))
                                        .node().value
                                    rename_control.remove()
                                    
                                    var cont = d3.select('#'+self.relid('container'))
                                        .style('display','block')
                                        
                                    if (info.objid.slice(0,3) == 'col') {
                                        var selobjid = info.parent_objid
                                        var seltype = 'Table'
                                    } else {
                                        var selobjid = info.objid
                                        var seltype = info.entitytype
                                    }
                                    
                                    Model.respond(self,'rename',{
                                        objid:info.objid,
                                        parent_objid: info.parent_objid,
                                        newname: newname,
                                        entitytype: info.entitytype
                                    })
                                                                                                            
                                }
                            }
                        })
                        
                        rename_control.selectAll('div')
                            .style('float','left')
                            .classed('n_entity_control',true)
                    } else if (action == 'mod_type') {
                        container
                            .style('display','none')
                        
                        var modify_control = self._node.append('div')
                            .attr('id',self.relid("modify_controls"))
                            .classed('n_entity_control_container',true)
                            
                        var optmap = d3.map()
                        var revmap = d3.map()
                        
                        var opts = Array(
                            [0,"Integer"],
                            [1,"Float"],
                            [2,"Text"]
                        )
                        
                        opts.forEach(function (d) {
                            optmap.set(d[0],d[1])
                            revmap.set(d[1],d[0])
                        })
                        
                        var current_choice = revmap.get(info.datatype)
                                                    
                        controls.dropdown_button(self.relid("modify_controls"),{
                            "label":"Datatype",
                            "button_label":"Submit",
                            "id":self.relid('datatype_dropdown'),
                            "default":current_choice,
                            "options":opts,
                            "on":{
                                "change":function(){
                                    current_choice = this.value
                                },
                                click:function () {
                                    var newtype = optmap.get(current_choice)
                                    modify_control.remove()
                                    
                                    var cont = d3.select('#'+self.relid('container'))
                                        .style('display','block')
                                        
                                    if (info.objid.slice(0,3) == 'col') {
                                        var selobjid = info.parent_objid
                                        var seltype = 'Table'
                                    } else {
                                        var selobjid = info.objid
                                        var seltype = info.entitytype
                                    }
                                    
                                    Model.respond(self,'modify',{
                                        objid:info.objid,
                                        parent_objid: info.parent_objid,
                                        datatype: newtype,
                                        entitytype: info.entitytype
                                    })
                                }
                            }
                        })
                        
                        modify_control.selectAll('div')
                            .style('float','left')
                            .classed('n_entity_control',true)
                            
                        modify_control.selectAll('form')
                            .style('float','left')
                            .classed('n_entity_control',true)
                    } else if (action == 'alias') {
                        container
                            .style('display','none')
                        
                        var alias_control = self._node.append('div')
                            .attr('id',self.relid("alias_container"))
                            .classed('n_entity_control_container',true)
                        
                        controls.input_button(self.relid("alias_container"),{
                            "label":"New Alias",
                            "id":self.relid('modify_alias'),
                            "button_label":"Change",
                            "icon":"play",
                            "on":{ click:function () {
                                    var newalias = d3.select('#'+self.relid('modify_alias'))
                                        .node().value
                                    alias_control.remove()
                                    
                                    var cont = d3.select('#'+self.relid('container'))
                                        .style('display','block')
                                    
                                    Model.respond(self,'modify',{
                                        objid:info.objid,
                                        parent_objid: info.parent_objid,
                                        alias: newalias,
                                        entitytype: info.entitytype
                                    })
                                    
                                }
                            }
                        })
                    }
                }
            }
            
            if (info.entitytype == 'Database') {
                menuitems = [
                    {
                        'label':'Create Table',
                        'action':'create_table',
                        'on':on
                    },
                    {
                        'label':'Drop',
                        'action':'drop',
                        'on':on
                    },
                    {
                        'label':'Alias',
                        'action':'alias',
                        'on':on
                    },
                    {
                        'label':'Rename',
                        'action':'rename',
                        'on':on
                    },
                ]
            } else if (info.entitytype == 'Table') {
                menuitems = [
                    {
                        'label':'Drop',
                        'action':'drop',
                        'on':on
                    },
                    {
                        'label':'Alias',
                        'action':'alias',
                        'on':on
                    },
                    {
                        'label':'Rename',
                        'action':'rename',
                        'on':on
                    },
                ]
            } else if (info.entitytype == 'View') {
                menuitems = [
                    {
                        'label':'Drop',
                        'action':'drop',
                        'on':on
                    },
                    {
                        'label':'Alias',
                        'action':'alias',
                        'on':on
                    },
                    {
                        'label':'Rename',
                        'action':'rename',
                        'on':on
                    }
                ]
            } else if (info.entitytype == 'Column') {
                menuitems = [
                    {
                        'label':'Drop',
                        'action':'drop',
                        'on':on
                    },
                    {
                        'label':'Alias',
                        'action':'alias',
                        'on':on
                    },
                    {
                        'label':'Rename',
                        'action':'rename',
                        'on':on
                    },
                    {
                        'label':'Modify Type',
                        'action':'mod_type',
                        'on':on
                    }
                ]
            }
            
            //var menuitems = []
            //info.methods.forEach(function (d) {
                //if (valid.indexOf(d) > 0) {
                    //menuitems.push({'label':d,'on':on})
                //}
            //})
            
            menu = controls.menu(self.relid('container'),{
                'id':self.relid('menu'),
                'items':menuitems
            })
            
            var name = info.name
            var entitytype = info.entitytype
            if (entitytype == 'Column') {
                entitytype = 'Column (' + info.datatype + ')'
            }
            
            objid = info.objid
            
            var labeltext = entitytype + ": " + name
            if (info.alias) labeltext = labeltext + ' (Alias: ' + info.alias + ') '
            
            d3.select('#'+self.relid('label'))
                .text(labeltext)
                .style('display','inline')
        }
    }   
}())

Layout.widgets.EntityMenu = EntityMenu
