var assert = require("better-assert")
GLOBAL.XMLHttpRequest = require('xhr2')
var d3 = require("d3")

var nimbodata = require("../nimbodata")
nimbodata.environment('node')

describe('core',function () {
    
    var cloud;
    var db;
    
    before('init connection', function (done) {
        cloud = nimbodata.connect(
            "http://localhost:5000",
            'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7',
            done
        )
    })
    
    beforeEach('init db',function (done) {
        cloud.create_database('Test',function (e,d) {
            db = d
            done()
        })
    })
    
    afterEach('drop the db', function (done) {
        cloud.Database('Test').drop(done)
    })
    
    it('create db with correct name', function (done) {
        var db = cloud.Database('Test')
        db.info(function (e,d) {
            assert(d.name == 'Test')
            done()
        })
    })    
        
    it('create table, insert and select correct vals', function (done) {
        var cols = [
            {'name':'pk','datatype':'Text'},
            {'name':'a','datatype':'Integer'},
            {'name':'b','datatype':'Text'},
        ]
        
        db.create_table('testTable',cols,function (e, tbl) {
            values = [
                {'pk':'frank','a':2,'b':'apple'},
                {'pk':'jerry','a':5,'b':'orange'},
                {'pk':'ann','a':7,'b':'fig'},
                {'pk':'francine','a':9,'b':'tomato'},
            ]
            
            tbl.insert(values,function () {})
            tbl.columns(function (e,d) {
                d[0].info(function(e,dd) {
                    assert(dd.name == 'pk')
                })
            })
            
            tbl.select(function (e,result) {
                var first = []
                for (i in result) {
                    first.push(result[i][0])
                }
                var valid = ['frank','jerry','ann','francine']
                for (var i in valid) {
                    assert(first.indexOf(valid[i]))
                }
                
                var second = []
                for (i in result) {
                    second.push(result[i][1])
                }
                valid = [2,5,7,9]
                for (var i in valid) {
                    assert(second.indexOf(valid[i]))
                }
                
                done()
            })
 
        })
    
    })

})
