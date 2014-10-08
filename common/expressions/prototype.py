"""Module implements abstract expressions in select queries for nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *

class UnaryExpression(object):
    """Encapsulates SQL/Nimbodata unary expression."""
    
    def __init__(self,exp,a):
        self.data = {'fname':exp,'args':[a]}

class BinaryExpression(object):
    """Make canonical a where clause and enable and/or operations."""
    
    def __init__(self,a,comp=None,b=None):
        """Create a where clause from either a single string or three parts."""
        if comp is None and b is None:
            if isinstance(a,BinaryExpression):
                self.data = a.data
                return
            try:
                a, comp, b = a.split(' ')
            except AttributeError:
                try:
                    comp = a['fname']
                    a,b = a['args']
                except TypeError:
                    try:
                        a, comp, b = a
                    except:
                        print a
                        raise
        
        if comp not in operators + ['any','all']:
            raise ValueError("Invalid comparison operator")
        
        if comp in ('any','all'):
            self.data = {comp:(a,b)}
        else:
            self.data = {'fname':comp,'args':[a,b]}
        
    def __and__(self,other):
        return BinaryExpression(self,'all',other)
        
    def __or__(self,other):
        return BinaryExpression(self,'any',other)
        
    def __str__(self):
        try:
            return '"%s" %s "%s" ' % self.data
        except TypeError:
            return str(self.data)


class TwoValExpression(object):
    """Encapsulates SQL/Nimbodata expressions."""
    
    def __init__(self,exp,a,b):
        self.data = {'fname':exp,'args':[a,b]}

class Function(object):
    
    def __init__(self,*args):
        self.fargs = args
    
    @property
    def data(self):
        return {
            'fname':type(self).__name__,
            'args':self.fargs
        }
