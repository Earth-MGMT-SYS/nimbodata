"""Module implements the Nimbodata API as a local library."""
# Copyright (C) 2014  Bradley Alan Smith

import sys
import functools
import inspect

try:
    from common.errors import *
    from common.api import CloudAPI
    import core.pg.entities as pg_entities
    import core.pg.select as pg_select
except ImportError:
    from nimbodata.common.errors import *
    from nimbodata.common.api import CloudAPI
    import nimbodata.core.pg.entities as pg_entities
    import nimbodata.core.pg.select as pg_select

def get_api():
    """Provide the api for insertion elsewhere."""
    api = CloudAPI(pg_entities.bases + [pg_select.Select])
    pg_entities.api = api
    return api


class Cloud(object):
    """Encapsulates all api functionality as a local object."""
    def __init__(self,user):
        """Get a cloud instance for the user."""
        self.api = get_api()
        pg_select.api = self.api # Inject the API into select.
        self.api.session = {'user':user} # User is set from local config.
    
    def select(self,*args,**kwargs):
        return self.api.get_entity('Select')().select(*args,**kwargs)
    
    def __getattr__(self, attr):
        """Route to the API get_attr engine."""
        return self.api.get_attr(attr)
