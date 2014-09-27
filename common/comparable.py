"""Module implements the comparable base class and WhereClause."""
# Copyright (C) 2014  Bradley Alan Smith

operators = ['<','>','>=','<=','=','<>','!=']
# The operator list may be appended to by other modules implementing extended
# operators.

class WhereClause(object):
    """Override `&` and `|` for relational use."""
    
    def __init__(self,a,comp,b):
        if comp in ('any','all'):
            self.data = {comp:(a,b)}
        else:
            self.data = (a,comp,b)
        
    def __and__(self,other):
        return WhereClause(self,'all',other)
        
    def __or__(self,other):
        return WhereClause(self,'any',other)
        
    def __str__(self):
        try:
            ' '.join(*self.data)
        except TypeError:
            return str(self.data)

class UnaryExpression(object):
    """Encapsulates SQL/Nimbodata unary expression."""
    
    def __init__(self,exp,a):
        self.data = (exp,a)

class BinaryExpression(object):
    """Encapsulates SQL/Nimbodata expressions."""
    
    def __init__(self,a,exp,b):
        self.data = (a,exp,b)
        
class TwoValExpression(object):
    """Encapsulates SQL/Nimbodata expressions."""
    
    def __init__(self,exp,a,b):
        self.data = (exp,a,b)

class Comparable(object):
    """Override comparison operators for relational use."""
    
    def __lt__(self,other):
        return WhereClause(self['name'],'<',other)
        
    def __gt__(self,other):
        return WhereClause(self['name'],'>',other)
        
    def __eq__(self,other):
        return WhereClause(self['name'],'=',other)
        
    def __ne__(self,other):
        return WhereClause(self['name'],'<>',other)
        
    def __le__(self,other):
        return WhereClause(self['name'],'<=',other)
        
    def __ge__(self,other):
        return WhereClause(self['name'],'>=',other)

    def __add__(self,other):
        return BinaryExpression(self['name'],'+',other)
    
    def __sub__(self,other):
        return BinaryExpression(self['name'],'-',other)
        
    def __mul__(self,other):
        return BinaryExpression(self['name'],'*',other)
        
    def __div__(self,other):
        return BinaryExpression(self['name'],'/',other)
        
    
