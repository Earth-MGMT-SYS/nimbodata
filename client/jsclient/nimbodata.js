
///////////////////////////////////////////////////////////////////////////////
////// Connection /////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

var user, server, api;
var environment = 'browser' // If nodejs it will be set by the main method

function connect (_server,_user,callback) {
    user = _user
    server = _server
    n_post(['login'],{'user':_user},callback)
    return Nimbodata
}

function set_env ( env ) {
    environment = env
}

///////////////////////////////////////////////////////////////////////////////
////// Entity Base Class //////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

function get_byinfo(objinfo) {
    if (objinfo.entitytype == 'Database') return new Database(objinfo)
    if (objinfo.entitytype == 'View') return new View(objinfo)
    if (objinfo.entitytype == 'Table') return new Table(objinfo)
    if (objinfo.entitytype == 'Column') return new Column(objinfo)
}

function Entity (objinfo) {
    this.init(objinfo)
}

Entity.prototype = {
    get objid () {
        if (this._objid) return this._objid
        else return this._info.objid
    },
    entity_type: 'Entity',
    init: function (objinfo) {
        if (typeof objinfo == 'string') {
            this._objid = objinfo
        }
        else this._info = objinfo
    },
    info: function (callback) {
        if (this._info) {
            callback(null,this._info)
            return
        }
        
        if (typeof this.parent === "undefined") {
            n_get([this.entity_type,this.objid],callback)
        }
        else {
            var entity_type = this.entity_type
            n_get(['databases',this.parent,this.entity_type,this.objid],function (e,d) {
                if (typeof d == 'object') {
                    callback(e,d)
                }
                else {
                    n_get([entity_type,d],callback)
                }
            })
        }
    },
    listing: function (/*child_type,callback*/) {
        if (arguments.length == 1) {
            var callback = arguments[0]
            n_get([this.entity_type],callback)
        }
        else if (arguments.length == 2) {
            var child_type = arguments[0]
            var callback = arguments[1]
            n_get([this.entity_type,this.objid,child_type],callback)
        }
        
    },
    tree: function(callback) {
        n_get([this.entity_type,this.objid],callback)
    },
    
    modify: function (params, callback) {
        if (this._info) this._objid = this._info.objid
        this._info = false
        n_post(
            [this.entity_type,this.objid,'modify'],
            {'params':params},
            callback
        )
    },
    
    rename: function (newname, callback) {
        if (this._info) this._objid = this._info.objid
        this._info = false
        n_post([this.entity_type,this.objid,'rename'],{'newname':newname},callback)
    },
    drop: function (callback) {
        n_delete([this.entity_type,this.objid],function (e,d) {
            if (callback) callback(null,d)
        })
    }
}

///////////////////////////////////////////////////////////////////////////////
////// Database Class /////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

function Database (objinfo) {
    this.init(objinfo)
}

Database.prototype = Object.create(Entity.prototype)

Database.prototype.entity_type = 'Database'

Database.prototype.create_table = function (name, cols, callback) {
    n_post(
        ['tables'],
        {
            'name':name,
            'cols':cols,
            'parent_objid':this.objid
        },
        function (e,d) {
            callback(e, new Table(d))
        }
    )
}

Database.prototype.create_view = function (name, select, callback) {
    params = {
        'name':name,
        'select':select,
        'parent_objid':this.objid,
    }
    if (name == 'temp') {
        params.temporary = true
    }
    n_post(
        ['views'],
        params,
        function (e,d) {
            callback(e, new View(d))
        }
    )
}

Database.prototype.tables = function (callback) {
    n_get(['databases',this.objid,'tables'],callback)
}

Database.prototype.Table = function (name) {
    var tbl = new Table(name)
    tbl.parent = this.objid
    return tbl
}

///////////////////////////////////////////////////////////////////////////////
////// View Class /////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

View = function (objinfo) {
    this.init(objinfo)
}

View.prototype = Object.create(Entity.prototype)
View.prototype.entity_type = 'View'

View.prototype.select = function (callback) {
    n_get(
        ['select',this.objid],
        callback
    )
}

View.prototype.columns = function (callback) {    
    n_get([this.entity_type, this.objid, 'columns'],function(e,d) {
        var cols = []
        for (var x in d) {
            cols.push(new Column(d[x]))
        }
        callback(e,cols)
    })
}

View.prototype.geo_columns = function (callback) {    
    n_get([this.entity_type, this.objid, 'geo_columns'],function(e,d) {
        var cols = []
        for (var x in d) {
            cols.push(new Column(d[x]))
        }
        callback(e,cols)
    })
}


///////////////////////////////////////////////////////////////////////////////
////// Table Class ////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

Table = function (objinfo) {
    this.init(objinfo)
}

Table.prototype = Object.create(View.prototype)
Table.prototype.entity_type = 'Table'

Table.prototype.insert = function (values, callback) {
    if (typeof this.parent === 'undefined') {
        n_post(
            [this.entity_type,this.objid],
            {'values':values},
            callback
        )
    }
    else {
        n_post(
            [this.parent,this.entity_type,this.objid],
            {'values':values},
            callback
        )
    }
}

///////////////////////////////////////////////////////////////////////////////
////// Column Class ///////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

Column = function (objinfo) {
    this.init(objinfo)
}

Column.prototype = Object.create(Entity.prototype)
Column.prototype.entity_type = 'Column'

///////////////////////////////////////////////////////////////////////////////
////// XHR Wrappers ///////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

function path(addr) {
    return '/' + addr.join('/') + '/'
}

function n_get(addr,callback) {
    var req = d3.json(server + path(addr))
    if (environment == 'node') {
        req.header('From',user)
    }
    else if (environment == 'browser') {
        req.on('beforesend', function (request) { request.withCredentials = true })
    }
    req.get(callback)
}

function n_post(addr,data,callback) {
    var req = d3.json(server + path(addr))
    if (environment == 'node') {
        req.header('From',user)
    }
    else if (environment == 'browser') {
        req.on('beforesend', function (request) { request.withCredentials = true })
    }
    req.post(JSON.stringify(data),callback)
}

function n_put(addr,data,callback) {
    var req = d3.json(server + path(addr))
    if (environment == 'node') {
        req.header('From',user)
    }
    else if (environment == 'browser') {
        req.on('beforesend', function (request) { request.withCredentials = true })
    }
    req.send('put',JSON.stringify(data),callback)
}

function n_delete(addr,callback) {
    var req = d3.xhr(server + path(addr))
    if (environment == 'node') {
        req.header('From',user)
    }
    else if (environment == 'browser') {
        req.on('beforesend', function (request) { request.withCredentials = true })
    }
    req.send('delete')
        .on('load',callback)
}

function RelationExists(message) {
    this.name = 'RelationExists'
    this.message = message || 'Relation already exists'
}

///////////////////////////////////////////////////////////////////////////////
////// Cloud Root Class ///////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

RelationExists.prototype = Object.create(Error)
RelationExists.prototype.constructor = RelationExists

Nimbodata = function () {

var self;

var public = {
    
    init: function () {
        self = this
        this.go()
    },
    create_database: function (name, callback) {
        n_post(
            ['databases'],
            {'name':name},
            function (e,d) {
                if (e) {
                    throw new RelationExists("Relation already exists")
                }
                else {
                    callback(null,new Database(d))
                }
            }
        )
    },
    Entity: function(name) {
        return new Entity(name)
    },
    Database: function(name) {
        return new Database(name)
    },
    Table: function(name) {
        return new Table(name)
    },
    View: function(name) {
        return new View(name)
    },
    Column: function(name) {
        return new Column(name)
    },
    databases: function(callback) {
        n_get(
            ['databases'],
            function(e,d) {
                var dbs = []
                for (x in d) {
                    dbs.append(new Database(d[x]))
                }
                callback(e,dbs)
            }
        )
    },
    tables: function(callback) {
        n_get(['databases'],callback)
    },
    views: function(callback) {
        n_get(['views'],callback)
    },
    columns: function(callback) {
        n_get(['columns'],callback)
    },
    tree: function(callback) {
        n_get(['tree'],callback)
    },
    select: function (kwargs,callback) {        
        try {
            if (kwargs.viewid._info) {
                kwargs.viewid = kwargs.viewid.objid
            }
        } catch (e) {
            return
        }
        
        //console.log(kwargs)
        
        n_post(['select'],kwargs,callback)
    },
    get_byrowid: function(objid,rowid,callback) {
        n_get(['select',objid,rowid],callback)
    },
    datastore: {}
}

return public;

}()

///////////////////////////////////////////////////////////////////////////////
////// Over the line, Smokey //////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

module.exports = {
    connect: connect,
    environment: set_env
}

