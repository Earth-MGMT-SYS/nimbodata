var assert = require("better-assert")
GLOBAL.XMLHttpRequest = require('xhr2')
var d3 = require("d3")

var nimbodata = require("../nimbodata")
nimbodata.environment('node')

describe('select',function () {
    
    var cloud, db, table;
    
    before('init connection', function (done) {
        cloud = nimbodata.connect(
            "http://0.0.0.0:5000",
            'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7',
            done
        )
    })
    
    beforeEach('init db',function (done) {
        cloud.create_database('Test',function (e,d) {
            db = d
            
            cols = [
                {'name':'pk','datatype':'Text'},
                {'name':'a','datatype':'Integer'},
                {'name':'b','datatype':'Text'},
            ]
            
            db.create_table('testTable',cols, function (e,tbl) {
                table = tbl
                var values = [
                    ['frank',2,'apple'],
                    ['jerry',5,'orange'],
                    ['ann',7,'fig'],
                    ['francine',9,'tomato']
                ]
                
                table.insert(values,done)
            })
        })
    })
    
    afterEach('drop the db', function (done) {
        cloud.Database('Test').drop(done)
    })
    
    it('simple select', function (done) {
        cloud.select({'viewid':table},function (e,d) {
            assert(d.rows.length == 4)
            assert(d.rows[0].length == 3)
            assert(d.rows[0][0] == 'frank')
            assert(d.rows[0][1] == 2)
            done()
        })
    })
    
    it('target select', function (done) {
        cloud.select({'viewid':table,'cols':['pk','b']},function (e,d) {
            assert(d.rows.length == 4)
            assert(d.rows[0].length == 2)
            assert(d.rows[0][0] == 'frank')
            assert(d.rows[0][1] == 'apple')
            done()
        })
    })
    
    it('select single where', function (done) {       
        cloud.select({
            'viewid':table,
            'where': 'a < 9'
            },function (e,d) {
                assert(d.rows.length == 3)
                done()
            }
        )
    })
    
    it('select multiple where', function (done) {
        cloud.select({
            'viewid':table,
            'where': ['a < 9','a > 2'],
            },function (e,d) {
                assert(d.rows.length == 2)
                done()
            }
        )
    })
    
    it('complex where', function(done) {
        cloud.select({
            'viewid':table,
            'where': {
                'all':['a < 9' , 'a > 2'],
                "any":['b = apple', 'b = fig']
            },
            },function (e,d) {
                assert(d.rows.length == 1)
                assert(d.rows[0][0],'ann')
                done()
            }
        )
    })
})
