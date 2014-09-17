
import json
import datetime

import jsonpickle

def fallback_json(obj):
    """
    Function used to encode objects to JSON which do not have a standard
    translation.
    
    """
    # Handle date/time

    if isinstance(obj,datetime.datetime) or isinstance(obj,datetime.date) \
            or isinstance(obj,datetime.time):
        return jsonpickle.encode(obj)
    try:
        return obj.toJSON()
    except:
        pass
    # Handle query results
    try:
        return obj.info
    except AttributeError:
        return str(obj)

def dump(x):
    return json.dumps(x,default=fallback_json)
def load(x):
    try:
        return json.loads(x)
    except ValueError:
        print x

def pretty_dump(x):
    return json.dumps(
        x,
        default=fallback_json,
        sort_keys=True,
        indent=4,
        separators=(',',':')
    )
