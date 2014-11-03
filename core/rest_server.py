"""Module implements a dynamic REST API for Nimbodata using Flask."""
# Copyright (C) 2014  Bradley Alan Smith

from gevent import monkey; monkey.patch_all()

import datetime
import sys
import json
from functools import partial

from flask import Flask, request, abort
from flask.views import MethodView
from flask.ext import login
from flask.ext.cors import CORS, cross_origin

sys.path.append('../')
import common
import common.errors as errors
import common.datatypes.fallback_json as fb
import common.api

from cloud import get_api

api = get_api()

load,dump,pretty_dump = fb.load, fb.dump, fb.pretty_dump

import pg.entities
import pg.select
import pg.expressions
api.login = login
pg.select.api = api
pg.expressions.inject_api(api)

import auth


app = Flask(__name__)
cors = CORS(
    app,
    headers=['Content-Type','Accept','Cookie'],
    origins=[
        'http://ubupgbeta:5000',
        'http://andydev:8000',
        'http://localhost:8000',
        'http://access.nimbodata.org:8000',
        'http://earth-mgmt.com',
        'http://www.earth-mgmt.com',
        'https://preview-545-54528d357e2193572d3411d1-545294e97e2193cc232ce011.monaca.mobi'
    ],
    supports_credentials=True
)


@app.route('/<path:path>', methods=['OPTIONS'])
@app.route('/favicon.ico',methods=['GET'])
def nada():
    """Sometimes we want to do nothing very quickly and successfully."""
    return ""

@app.route('/', methods=['GET'])
def indexview():
    """Root index - points to www.nimbodata.com as source for CSS/JS."""
    with open('./index/index.html','r') as ifile:
        return ifile.read()

@app.route('/<appname>/app.json',methods=['GET'])
def appjson(appname):
    """Return the json spec for the app."""
    appdb = api.get_entity('Database')(appname)
    assets = appdb.Table('assets')
    fname, val = assets.columns()
    return dump(assets.select())
    
@app.route('/<appname>/',methods=['GET'])
def appindex(appname):
    """Return the html file for the app."""
    with open('./index/index.html','r') as ifile:
        return ifile.read()

@app.route('/app.json',methods=['GET'])
def appview():
    """The launcher app spec."""
    appdb = api.get_entity('Database')('earth-mgmt')
    assets = appdb.Table('assets')
    fname, val = assets.columns()
    return dump(assets.select())

@app.route('/watertree.json',methods=['GET'])
def watertreeeee():
    """The launcher app spec."""
    return open('../apps/water-mgmt/watertree.json','r').read()

@app.route('/api/', methods=['GET'])
def apiresponder():
    """Get a copy of the api in json."""
    return dump(api.api)

def responder(method,rfunc,objid=None):
    """Handle I/O and Error translation between API and REST."""
    if method == 'POST' and objid is None:
        # creating an entity
        try:
            return dump(rfunc(load(request.data)))
        except errors.RelationExists:
            abort(409)
        except errors.NotAuthorized:
            abort(401)
    elif method == 'POST':
        # modifying an entity
        try:
            return dump(rfunc(objid=objid,params=load(request.data)))
        except errors.IntegrityError as e:
            return dump(e.strerror)
        except errors.NotAuthorized:
            abort(401)
    elif method == 'PUT':
        # modifying an entity
        return dump(rfunc(objid=objid,params=load(request.data)))
    try:
        # get or othere
        return dump(rfunc(objid=objid))
    except errors.NotAuthorized:
        abort(401)
    except errors.RelationExists:
        abort(409)
    except errors.RelationDoesNotExist:
        abort(410)
        
# Parse the API and add the URL routes attached to the API endpoints.
for urlspec,rfunc in api.urls.items():
    verb,path = urlspec
    app.add_url_rule(
        path,
        view_func = partial(responder,verb,rfunc),
        endpoint = str(urlspec),
        methods = [verb]
    )

@app.route('/tree/',methods=['GET'])
def tree():
    return dump(api.get_entity('Database')().tree())
    
@app.route('/bypath/',methods=['POST'])
def bypath():
    path = load(request.data)['path'][1:].split('/')
    root = api.get_entity('Database')(path[0])
    last = root
    for level in path[1:]:
        last = last.View(level)
    return dump(last)

@app.route('/select/<objid>/<rowid>/',methods=['GET'])
def getbyrowid(objid,rowid):
    """Handle get select."""
    return dump(api.get_entity('Select')().get_byrowid(objid,rowid,True))

@app.route('/select/<objid>/',methods=['GET'])
def get_select_processor(objid):
    """Handle get select."""
    try:        
        argspec = api.get_args('Select','select')
        kwargs = {
            'objid':objid,
            'limit':50
        }
        return dump(api.get_entity('Select')().select(**kwargs))
    except errors.RelationDoesNotExist as e:
        print objid
        abort(410)
        
@app.route('/tables/<objid>/tile_rowids/<x>/<y>/<z>/',methods=['GET'])
@app.route('/Table/<objid>/tile_rowids/<x>/<y>/<z>/',methods=['GET'])
def table_rowids_handler(objid,x,y,z):
    """Handle get tile."""
    return dump(api.get_entity('Table')(objid).tile_rowids(x,y,z))
    
@app.route('/tables/<objid>/tile/<x>/<y>/<z>/',methods=['GET'])
@app.route('/Table/<objid>/tile/<x>/<y>/<z>/',methods=['GET'])
def table_tile_handler(objid,x,y,z):
    """Handle get tile."""
    try:
        return dump(api.get_entity('Table')(objid).tile(x,y,z))
    except errors.RelationDoesNotExist:
        abort(404)
    
@app.route('/tables/<objid>/tile/<x>/<y>/<z>/<magnitude>/',methods=['GET'])
@app.route('/Table/<objid>/tile/<x>/<y>/<z>/<magnitude>/',methods=['GET'])
def table_tile_handler_mag(objid,x,y,z,magnitude):
    """Handle get tile with specified magnitude column."""
    try:
        return dump(api.get_entity('Table')(objid).tile(x,y,z,magnitude))
    except errors.RelationDoesNotExist:
        abort(404)
    
@app.route('/tables/<objid>/features/',methods=['POST'])
@app.route('/Table/<objid>/features/',methods=['POST'])
def table_features_handler(objid):
    """Handle get features."""
    rdat = load(request.data)
    print [str(x) for x in rdat['rowids']]
    return dump(api.get_entity('Table')(objid).features(rdat['rowids']))

@app.route('/views/<objid>/tile_rowids/<x>/<y>/<z>/',methods=['GET'])
@app.route('/View/<objid>/tile_rowids/<x>/<y>/<z>/',methods=['GET'])
def view_rowids_handler(objid,x,y,z):
    """Handle get tile rowids."""
    return dump(api.get_entity('View')(objid).tile_rowids(x,y,z))
    
@app.route('/views/<objid>/tile/<x>/<y>/<z>/',methods=['GET'])
@app.route('/View/<objid>/tile/<x>/<y>/<z>/',methods=['GET'])
def view_tile_handler(objid,x,y,z):
    """Handle get tile rowids."""
    try:
        return dump(api.get_entity('View')(objid).tile(x,y,z))
    except errors.RelationDoesNotExist:
        abort(404)

@app.route('/views/<objid>/tile/<x>/<y>/<z>/<magnitude>/',methods=['GET'])
@app.route('/View/<objid>/tile/<x>/<y>/<z>/<magnitude>/',methods=['GET'])
def view_tile_handler_mag(objid,x,y,z,magnitude):
    """Handle get tile with specified magnitude column."""
    try:
        return dump(api.get_entity('View')(objid).tile(x,y,z,magnitude))
    except errors.RelationDoesNotExist:
        abort(404)
    
@app.route('/views/<objid>/features/',methods=['POST'])
@app.route('/View/<objid>/features/',methods=['POST'])
def view_features_handler(objid):
    """Handle get features."""
    rdat = load(request.data)
    print [str(x) for x in rdat['rowids']]
    return dump(api.get_entity('View')(objid).features(rdat['rowids']))

@app.route('/select/',defaults={'objid':None},methods=['POST'])
@app.route('/select/<objid>/',methods=['POST'])
def post_select_processor(objid):
    """Handle post select."""
    lastaccess = open('lastaccess','w')
    now = datetime.datetime.now()
    now = dump((now.year,now.month,now.day,now.hour,now.minute))
    lastaccess.write(now)
    lastaccess.close()
    try:
        kwargs = load(request.data)
        if 'limit' not in kwargs:
            kwargs['limit'] = 50
        return dump(api.get_entity('Select')().select(**kwargs))
    except errors.RelationDoesNotExist as e:
        print objid
        abort(410)


@app.route('/<path:path>', methods=['GET','POST','PUT','DELETE'])
def respond(path):
    """Generic path responder, on its way out."""
    # Standardize to no trailing slash (for parsing purposes)
    try:
        if path[-1] == '/':
            path = path[:-1]
    except IndexError:
        pass
    args = path.split('/')
    if args[0] == 'get_byrowid':
        return dump(api.get_entity('Select')().get_byrowid(*args[1:]))
    elif args[0] == 'get_array':
        return dump(api.get_entity('Select')().get_array(**load(request.data)))
    try:
        return process_entity_identified(*args)
    except errors.RelationDoesNotExist:
        abort(410)
    except TypeError:
        abort(404)
    abort(404)


def process_entity_identified(entityname,objid,method=None,child=None,last=None):
    """Remnants."""  
    if request.method == 'GET' and (method is not None and child is not None and last is None):
        ent = api.get_entity(entityname)(objid)
        meth = getattr(ent,method)
        return dump(
            meth(child)
        )
        
    elif request.method == 'GET' and all(x is not None for x in (method,child,last)):
        outer = api.get_entity(entityname)(objid)
        outer = getattr(outer,method)
        print outer
        return dump(
            getattr(outer,last)()
        )
            
    elif method in ('modify','rename'):
        if request.method == 'OPTIONS':
            return ''
        elif request.method not in ('PUT','POST'):
            abort(405)
        entity = api.get_entity(entityname)(objid)
        try:
            if method == 'modify':
                #try:
                return dump(entity.modify(**load(request.data)))
                #except errors.DataError:
                #    abort(409)
            if method == 'rename':
                return dump(entity.rename(**load(request.data)))
        except errors.NotAuthorized:
            abort(401)
        
    elif request.method == 'POST' and method == 'add_columns':
        entity = api.get_entity(entityname)(objid)
        return dump(entity.add_columns(**load(request.data)))
        
    elif request.method == 'POST' and method == 'add_index':
        entity = api.get_entity(entityname)(objid)
        return dump(entity.add_index(**load(request.data)))
    
    elif method is not None and method.startswith('create_'):
        if request.method != 'POST':
            abort(405)
        try:
            ent = api.get_entity(entityname)(objid)
        except KeyError:
            abort(404)
        return dump(getattr(ent,method)(**load(request.data)))
    
    else:
        if request.method != 'GET':
            abort(405)
        try:
            ent = api.get_entity(entityname)(objid)
        except KeyError:
            abort(404)
        try:
            return dump(getattr(ent,method)())
        except AttributeError:
            abort(404)
        
    abort(404)


login_view = auth.LoginAPI.as_view('login')

app.add_url_rule(
    '/login/',
    view_func = login_view,
    methods = ['POST']
)

login_view = auth.LoginAPI.as_view('login')
app.secret_key = "GeorgeJetson"
app.config.from_object(__name__)

login_manager = login.LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return auth.User(user_id)

login_manager.setup_app(app)
login_manager.init_app(app)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0',debug=True)
    except Exception:
        app.logger.exception('Failed')
