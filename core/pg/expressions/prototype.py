
import string,random

try:
    import common.errors as errors
except ImportError:
    import nimbodata.common.errors as errors

from .. import datatypes
from . import *

def subid():
    return ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase)
            for dontcare in range(10)
    )
    

def get_decoder(obj):
    """Return a mapping of identifiers to canonical form.
        
    Given a view or table, collects all the possible identifers as keys to
    a dict where the values are the valid objid.
    
    """
    try:
        colinfo = obj.columns()
    except AttributeError:
        obj = api.get_byid(obj)
        colinfo = obj.columns()
    
    def fqn(info):
        return (obj['objid'],info['objid'])
    
    decoder = dict((x['name'],fqn(x)) for x in colinfo)
    decoder.update(
        dict((obj['name']+"."+x['name'],fqn(x)) for x in colinfo)
    )
    decoder.update(
        dict((x['objid'],fqn(x)) for x in colinfo)
    )
    decoder.update({'_adm-rowid':(obj['objid'],'_adm-rowid')})
    return decoder

class UnaryExpression(base.UnaryExpression):
    """Encapsulates SQL/Nimbodata unary expression."""

class BinaryExpression(base.BinaryExpression):
    """Make canonical a where clause and enable and/or operations."""
        
    def sql_exp(self,decoder,j_decoder=None):
        
        params, w_params = {}, {}
        
        try:
            whereCol, whereCmp, whereCond = self.data
        except ValueError:
            whereCmp = self.data['fname']
            whereCol, whereCond = self.data['args']
        
        try:
            colid = decoder[whereCol]
        except KeyError:
            colid = j_decoder[whereCol]
        whereCol = '"%s"."%s"' % colid
                
        if isinstance(whereCond,basestring) and whereCond.startswith('row-'):
            sub = subid()
            fmtstring = '%(' + sub + ')s'
            params[sub] = whereCond
            w_params[sub] = fmtstring
            whereCond = fmtstring
        elif isinstance(whereCond,dict) and 'fname' in whereCond:
            exp = getexp(whereCond['fname'])()
            whereCond = exp.sql_cast(*whereCond['args'])
        else:
            try:
                try:
                    whereCond = '"%s"."%s"' % decoder[whereCond]
                except KeyError:
                    whereCond = '"%s"."%s"' % j_decoder[whereCond]
            except (KeyError,TypeError):
                try:
                    whereCondCol = api.get_byid(whereCond)
                    repl = (whereCondCol['parent_objid'],whereCondCol['objid'])
                    whereCond = '"%s"."%s"' % repl
                except errors.RelationDoesNotExist:
                    sub = subid()
                    fmtstring = '%(' + sub + ')s'
                    col_type = api.get_byid(colid[1])['datatype']
                    col_type = getattr(datatypes,col_type)
                    # Is fail permissive a good idea??? I don't know.
                    try:
                        params[sub] = col_type(whereCond)
                    except (TypeError,ValueError):
                        params[sub] = whereCond
                    w_params[sub] = fmtstring
                    whereCond = fmtstring
        
        
        if whereCmp not in operators:
            raise ValueError("Invalid comparison operator")
        
        return ' '.join((whereCol,whereCmp,whereCond)), params, w_params


class TwoValExpression(base.TwoValExpression):
    """Encapsulates SQL/Nimbodata expressions."""



class Function(base.Function):
    """Encapsulates Nimbodata generalized function."""
