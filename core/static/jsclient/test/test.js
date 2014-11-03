
var assert = require("better-assert")
GLOBAL.XMLHttpRequest = require('xhr2')
var d3 = require("d3")

var nimbodata = require("../nimbodata")

describe('database', function () {
    
    var cloud;
    var dbname;
    
    beforeEach('connect', function (done) {
        cloud = nimbodata.connect(
            "http://localhost:5000",
            'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7',
            done
        )
    })
    
    after('DESTROY!', function (done) {
        var dbs = cloud.Database().listing(function(e,dbs) {
            dbs.forEach(function(d) {
                cloud.Database(d).drop(function () {})
            })
            done()
        })
    })
        
    it('create database and table', function (done) {
        cloud.create_database('dbtest',function(e,db) {
            assert(db.objid.slice(0,4) == 'dbi-')
            var cols = [
                {'name':'a','datatype':'Text'},
                {'name':'b','datatype':'Integer'}
            ]
            db.create_table('testtable',cols,function(e,tbl) {
                table = tbl
                assert(tbl.objid.slice(0,4) == 'tbl-'),
                done()
            })
        })
    })
    
    it('rename database', function (done) {
        var db = cloud.Database('dbtest')
        var _dbname = dbname
        db.rename('boffo',function () {
            var newdb = cloud.Database('boffo')
            newdb.drop(done)
        })
    })
})

describe('table', function () {
    
    var cloud; var db; var table;
    
    before('connect', function (done) {
        cloud = nimbodata.connect(
            "http://localhost:5000",
            'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7',
            done
        )
    })
    
    beforeEach('instantiate db', function(done) {
        cloud.create_database('tables',function (e,d) {
            db = d
            var cols = [
                {'name':'a','datatype':'Text'},
                {'name':'b','datatype':'Integer'}
            ]
            db.create_table('testtable',cols,function(e,d){
                table = d
                done()
            })
        })
        
    })
    
    afterEach('drop table and db', function(done) {
        table.drop(function(e,d) {
            db.drop(function(e,d) {
                done()
            })
        })
    })
    
    it('rename', function (done) {
        table.rename('sclackheimer',function (e,d) {
            table.info(function(e,d) {
                d.name == 'schlackheimer'
                done()
            })
        })
    })
    
    it('insert', function (done) {
        table.insert([['g',1],['b',2]],function () {
            table.select(function (e,result) {
                assert(result.rows[0][0] == 'g' || result.rows[0][0] == 'b')
                done()
            })
        })
    })
    
    it('columns', function(done) {
        table.columns(function(e,d){
            assert(d.length == 2)
            d[0].info(function(e,d){
                assert(d.name == 'a')
                done()
            })
        })
    })
    
    it('by name', function(done) {
        var table = db.Table('testtable')
        table.info(function(e,d) {
            assert(d.name == 'testtable')
            done()
        })
    })
    
})

describe('view', function () {
    
    var db;
    var view;
    
    before('connect', function (done) {
        cloud = nimbodata.connect(
            "http://localhost:5000",
            'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7',
            done
        )
    })
    
    beforeEach('instantiate db', function(done) {
        cloud.create_database('testingtables',function (e,d) {
            db = d
            var cols = [
                {'name':'a','datatype':'Text'},
                {'name':'b','datatype':'Integer'}
            ]
            db.create_table('testtable',cols,function(e,tbl){
                table = tbl
                table.insert([['g',1],['b',2]],function () {
                    db.create_view('klepto',{'objid':table.objid},function (e,d) {
                        view = d
                        done()
                    })
                })
            })
            
        })
        
    })
    
    afterEach('drop table and db', function(done) {
        table.drop(function(e,d) {
            db.drop(function(e,d) {
                done()
            })
        })
    })
    
    it('create view', function (done) {
        view.select(function (e,result) {
            assert(result.rows[0][0] == 'g' || result.rows[0][0] == 'b')
            done()
        })
    })
    
})
