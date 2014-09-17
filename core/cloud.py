"""Module implements the Nimbodata API as a local library."""
# Copyright (C) 2014  Bradley Alan Smith

import sys
import functools
import inspect

sys.path.append('../../')
import common

from common.errors import *
from common.api import CloudAPI

import pg.entities
import pg.select

def get_api():
    """Get an API for Nimbodata, for Select and the Entities."""
    api = CloudAPI(pg.entities.bases + [pg.select.Select])
    pg.entities.api = api
    return api


class Cloud(object):
    """Encapsulates all Nimbodata functionality as a local object.
    
    Designed to act with a local PostgreSQL connection.
    
    """
    def __init__(self,user):
        """Get a cloud instance for the user."""
        self.api = get_api()
        pg.select.api = self.api
        self.api.session = {'user':user}
        self.get_byid = self.api.get_byid
    
    def select(self,*args,**kwargs):
        return self.api.get_entity('Select')().select(*args,**kwargs)
    
    def __getattr__(self, attr):
        """Dynamic lookup for method calls.
        
        If a method starts with '_', it is a private method and can't be
        callsed.  If the method starts with 'create', we return an entity
        class of the appropriate type.  Should all else fail, route to
        Select engine.
        
        """
        return self.api.get_attr(attr)
