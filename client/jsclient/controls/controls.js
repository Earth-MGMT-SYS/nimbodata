
controls = function () {

var val = function (d) {return d[0]}
var text = function (d) {return d[1]}
var echo = function (d) {return d}
var enclose = function (d) {return [d]}

return {

    _selector: function (parent_node) {
        return "#" + parent_node;
    },
    
    multi: function(parent_node,params) {
        if (typeof parent_node == "string") {
            var selector = controls._selector(parent_node)
        }
        else {
            var selector = parent_node
        }
                
        var node = d3.select(selector)
            .append('span')
            .classed('argo',true)
            .attr("id",params.id)
        
        if (params.label) {
            node
                .append("label")
                .classed("argo",true)
                .text(params.label)
        }
        
        return node
    },
    
    expando: function(parent_node,params) {
        var selector = controls._selector(parent_node)
        var outer = d3.select(selector)
            .append('div')
                .classed('n_expando_outer',true)
        
        var tab = outer.append('div')
            .classed('n_expando_tab',true)
            .text('Show ' + params.label)
                
        var node = outer.append('div')
            .classed('n_expando_inner',true)
            .classed('hidden',true)
            .attr('id',params.id)
            
        tab.on('click',function () {
            if (node.classed('shown')) {
                node.classed('shown',false)
                node.classed('hidden',true)
                tab.text('Show ' + params.label)
            } else if (node.classed('hidden')) {
                node.classed('shown',true)
                node.classed('hidden',false)
                tab.text('Hide ' + params.label)
            } else {
                node.classed('shown',false)
                node.classed('hidden',true)
                tab.text('Show ' + params.label)
            }
            Layout.refresh()
        })
            
        return node
    },

    input: function (parent_node,params) {
        var selector = controls._selector(parent_node)
        var tag;
                
        var node = d3.select(selector)
            .append('div')
                .classed("argo",true)   
            
        node.append('form')
            .classed('pure-form',true)
            .append("label")
                .classed('argo',true)
                .text(params.label)
                    .append("input")
                    .attr("id",params.id)
                    .attr("value",params.default)
        return node
    },
    
    feedback: function(parent_node,params) {
        var selector = controls._selector(parent_node)
        
        var node = d3.select(selector)
            .append('div')
            .classed("argo_feedback_container",true)
            .classed("argo",true)
            
        node.append("div")
            .text(params.label)
            .classed("argo_feedback_label",true)
        node.append("div")
                .append('span')
                    .attr("id",params.id)
                    .classed("argo_feedback",true)
    },
    
    dropdown: function (parent_node,params) {
        var selector = controls._selector(parent_node)

        var node = d3.select(selector)
            .append('div')
            .classed("argo",true)
                .append('form')
                .classed('pure-form',true)
        
        node.text(params.label)
            
                .append("select")
                .on("change",params.on.change)
                .data([params.options])
                .attr("id",params.id)
                .classed("argo",true)
                .selectAll("option")
                    .data(echo)
                    .enter().append("option")
                        .attr("value",val)
                        .classed("argo",true)
                        .text(text)
        
        node.select("select.argo").selectAll("option")
            .attr("selected",function(d){
                            return params.default == d[0] ? true : null
                        })
        
        return node
    },
    
    listbox: function (parent_node,params) {
        var selector = controls._selector(parent_node)

        var node = d3.select(selector)
            .append('span')
            .append('form')
            .classed('pure-form',true)
        
        node.text(params.label)
            .classed("argo",true)
                .append("select")
                .attr('size',10)
                .on("change",params.on.change)
                .data([params.options])
                .attr("id",params.id)
                .classed("argo",true)
                .selectAll("option")
                    .data(echo)
                    .enter().append("option")
                        .attr("value",val)
                        .classed("argo",true)
                        .text(text)
        
        node.select("select.argo").selectAll("option")
            .attr("selected",function(d){
                            return params.default == d[0] ? true : null
                        })
        
        return node
    },
    
    checkboxes: function(parent_node,params) {
        var selector = controls._selector(parent_node)
        
        var node = d3.select(selector)
            .append('div')
            .classed('n_check',true)
            
        node
            .data([params.options])
            .attr("id",params.id)
        node
            .selectAll("label")
                .data(echo)
                .enter().append("label")
                    .text(text)
                    .classed("argo",true)
                .selectAll("input")
                    .data(enclose)
                    .enter().append("input")
                        .attr("type","checkbox")
                        .classed("argo",true)
                        .attr("value",text)
        if (params.orientation == "vertical") {
            node.selectAll("label.argo")
                .classed("vertical",true)
        }
        return node
    },
    
    checkboxes_get_selected: function(parent_node){
        var container = d3.select(controls._selector(parent_node))
        var checked = []
        
        container.selectAll("input").each(function(d,i) {
            if(this.checked) {checked.push(d3.select(this).attr("value"))}
        })
        
        return checked
    },
    
    checkboxes_clear: function(parent_node){        
        d3.select(controls._selector(parent_node))
            .selectAll("input").each(function(d,i) {
                this.checked = false
            })
    },

    button: function (parent_node,params) {
        var selector = controls._selector(parent_node)
        
        var node = d3.select(selector)
            .append('a')
                .classed("pure-button",true)
                .classed("n_button",true)
                .attr("id",params.id)
                .on('click',params.on.click ? params.on.click : null)
        
        if (params.icon) {
            node.append('i')
                .classed('fa',true)
                .classed('fa-'+params.icon,true)
        }
        
        var label = node.append('span')
            .text(params.label)
        
        if (params.icon) {    
            label.classed('n_button_icon_label',true)
        }
        
        if (params.action) {
            node.attr('action',params.action)
        }
        
        return node
    },

    input_button: function (parent_node,params) {
        var selector = controls._selector(parent_node)
        
        var node = d3.select(selector)
            .append('div')
            .attr("id",params.id + "_container")
            .classed('argo',true)
        
        var form = node.append('form')
            .classed('pure-form',true)
            
        form
            .append("label")
                .classed("argo",true)
                .text(params.label)
                    .append("input")
                    .attr("id",params.id)
                    .attr("value",params.default)
                    .classed("argo",true)
                    
        var button = form.append('a')
            .classed('pure-button',true)
            .classed('n_input_button',true)
            .on('click',params.on.click)
            
        if (params.icon) {
            button.append('i')
                .classed('fa',true)
                .classed('fa-'+params.icon,true)
        }
        
        var label = button.append('span')
            .text(params.button_label)
        
        if (params.icon) {    
            label.classed('n_button_icon_label',true)
        }
        
    },

    dropdown_button: function (parent_node,params) {
        var selector = controls._selector(parent_node)
        
        var node = d3.select(selector)
            .append('div')
            .classed('argo',true)
            
        var form = node.append('form')
            .classed('pure-form',true)
            
        form
            .append("label")
                .classed("argo",true)
                .text(params.label)
                    .append("select")
                    .on("change",params.on.change)
                    .attr("id",params.id)
                    .classed("argo",true)
                    .selectAll('option')
                    .data(params.options)
                    .enter().append('option')
                        .attr('value',val)
                        .classed('argo',true)
                        .text(text)
                    
        var button = form.append('a')
            .classed('pure-button',true)
            .classed('n_dropdown_button',true)
            .on('click',params.on.click)
            
        if (params.icon) {
            button.append('i')
                .classed('fa',true)
                .classed('fa-'+params.icon,true)
        }
        
        var label = button.append('span')
            .text(params.button_label)
        
        if (params.icon) {    
            label.classed('n_button_icon_label',true)
        }
        
        
            
        //node.text(params.label)
            //.classed("argo",true)
                //.append("select")
                //.on("change",params.on.change)
                //.data([params.options])
                //.attr("id",params.id)
                //.classed("argo",true)
                //.selectAll("option")
                    //.data(echo)
                    //.enter().append("option")
                        //.attr("value",val)
                        //.classed("argo",true)
                        //.text(text)
        
        //node.append("span")
                //.text(params.button_label)
                //.attr("id",params.id+"_argo_button")
                //.classed("argo_button",true)
                //.on('click',params.on.click)
                
        node.select("select").selectAll("option")
            .attr("selected",function(d){
                return params.default == d[0] ? true : null
            })
    },
    
    menu: function (parent_node,params) {
        var selector = controls._selector(parent_node)
        
        var node = d3.select(selector)
            .append('span')
            .attr('id',params.id)
        
        params.items.forEach(function (buttonparams) {
            if (typeof buttonparams == 'string') {
                controls.button(params.id,{
                    'label':buttonparams,
                    'on':{'click':function (d) { alert(buttonparams) } }
                })
            } else {
                controls.button(params.id,buttonparams)
            }
        })
        
        d3.select('#'+params.id).selectAll('.n_button')
            .attr('class','pure-button n_menu_button')
            
    },

    button_get_value: function (button_node) {
        return d3.select("#"+button_node.id.replace("_argo_button",""))[0][0].value
    }

}}();
