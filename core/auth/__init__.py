"""Implements rudimentary login components for use with Flask-Login."""
# Copyright (C) 2014  Bradley Alan Smith

import json

from flask import request
from flask.views import MethodView
from flask.ext import login

class User(object):
    """Stub object representing an authenticated user."""
    
    def __init__(self,user):
        print user
        self.user = user
        
    def is_authenticated(self):
        return True
        
    def is_active(self):
        return True
        
    def is_anonymous(self):
        return False
        
    def get_id(self):
        return self.user


class LoginAPI(MethodView):
    """Flask view for logging in."""
    
    def post(self):
        """User provides credentials in POST payload."""
        payload = json.loads(request.data)
        login.login_user(User(payload['user']))
        return json.dumps(True)
