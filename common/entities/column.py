"""Module implements the table column."""
# Copyright (C) 2014  Bradley Alan Smith

try:
    import common.expressions.comparable as comparable
    import common.datatypes as datatypes
except ImportError:
    import nimbodata.common.expressions.comparable as comparable
    import nimbodata.common.datatypes as datatypes

from . import * 

class Column(Entity,comparable.Comparable):

    objid_prefix = 'col'

    def __init__(self,name=None,objid=None,info=None):
        Entity.__init__(self,name,objid,info)
        
    def __getattr__(self,attr):
        if attr in ('info','columns'):
            raise AttributeError
        try:
            dty = getattr(datatypes,self.info['datatype'])
            func = getattr(dty,attr)
        except TypeError as e:
            print attr
            raise e
        def outer(other):
            return func(self,other)
        return outer


