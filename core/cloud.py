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
    """Encapsulates all Nimbodata functionality as a local object."""
    def __init__(self,user):
        """Get a cloud instance for the user."""
        self.api = get_api()
        pg.select.api = self.api # Inject the API into select.
        self.api.session = {'user':user} # User is set from local config.
    
    def select(self,*args,**kwargs):
        return self.api.get_entity('Select')().select(*args,**kwargs)
    
    def __getattr__(self, attr):
        """Route to the API get_attr engine."""
        return self.api.get_attr(attr)

