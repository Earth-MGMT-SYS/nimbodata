
function Legend (root,spec) {
    this.init(root,spec)
}

Legend.prototype = Object.create(Widget.prototype)

extend(Legend, function () {

return {

    init: function(root, spec) {
        this._classes = " Container "
        Widget.prototype.init.call(this, root, spec)
        this._node.style('display','none')
    },
    
    objid: null,
    legend: true,
    
    update: function(e, d) {
        
        if (d && d.levels) {}
        else if (e) { alert(e.responseText) }
        else {
            Widget.prototype.update.call(this)
            return
        }
        
        this._node.style('display','block')
        var data = []
        for (var i in d.levels) {
            data.push(d.levels[i])
        }
        data.reverse()
        
        this._node
            .selectAll('div')
            .data(data)
            .enter().append('div')
                .style('background',function (d) { return d })
                .classed('n_legend_square',true)
                .text(function(d,i) { return 10 * (10 - i) + "%"})
                .on('mouseover',function(){
                    var thisnode = d3.select(this)
                    thisnode.text('>'+thisnode.text())
                })
                .on('mouseout',function(){
                    var thisnode = d3.select(this)
                    thisnode.text(thisnode.text().slice(1,thisnode.text().length))
                })
    }
    
}} () );

Layout.widgets.Legend = Legend
