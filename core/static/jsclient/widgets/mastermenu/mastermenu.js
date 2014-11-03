function MasterMenu (root, spec) {
    this.init(root, spec)
}

MasterMenu.prototype = Object.create(Widget.prototype)

extend(MasterMenu, function () {
    
    var active = 0;
    var self;
    var menu, feedback;
    var objid;
        
    return {
        init: function (root, spec) {
            self = this
            this._classes = 'n_master_control_container Container'
            Widget.prototype.init.call(this, root, spec)
            
            var container = this._node
                            
            container.append('span')
                .attr('id',this.relid('label'))
                .classed('n_mastermenu_company',true)
                .append('a')
                .text('Earth Management Systems')
                .attr('href','http://www.mgmt-sys.com')
                
            var rmenu = container.append('span')
                .attr('id',this.relid('right'))
                .classed('n_mastermenu_right',true)
                
            rmenu.append('a')
                .classed('n_rmenu_item',true)
                .attr('href','http://www.nimbodata.com/doc')
                .text('Docs')
            
            rmenu.append('a')
                .classed('n_rmenu_item',true)
                .attr('href','http://www.github.com/Earth-MGMT-SYS/nimbodata/')
                .text('Github!')
                
            
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
                        cloud.Entity(objid).drop(function(e,d) {
                            var parent = cloud.Entity(info.parent_objid)
                                .info(function(e,d) {
                                    Model.respond(self,'select',d)
                                })
                        })
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
                    } else if (action == 'modify') {
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
                                                    
                        controls.dropdown(self.relid("modify_controls"),{
                            "label":"loopins",
                            "id":"loopins",
                            "default":current_choice,
                            "options":opts,
                            "on":{
                                "change":function(){
                                    current_choice = this.value
                                }
                            }
                        })
                        
                        controls.button(self.relid("modify_controls"),{
                            "label":"Submit",
                            "icon":"play",
                            "id":self.relid('submit_button'),
                            "on":{ click:function () {
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
                                        newtype: newtype,
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
                        'label':'Rename',
                        'action':'rename',
                        'on':on
                    },
                    {
                        'label':'Modify Type',
                        'action':'modify',
                        'on':on
                    }
                ]
            }
                        
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
            
            d3.select('#'+self.relid('label'))
                .text(entitytype + ": " + name)
                .style('display','inline')
        }
    }   
}())

Layout.widgets.MasterMenu = MasterMenu
