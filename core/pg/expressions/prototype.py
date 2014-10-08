
import string,random

import common.errors

from .. import datatypes
from . import *

def subid():
    return ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase)
            for dontcare in range(10)
    )
    

def get_decoder(obj):
    try:
        colinfo = obj.columns()
    except AttributeError:
        obj = api.get_byid(obj)
        colinfo = obj.columns()
    
    decoder = dict((x['name'],x['objid']) for x in colinfo)
    decoder.update(
        dict((obj['name']+"."+x['name'],x['objid']) for x in colinfo)
    )
    decoder.update(
        dict((x['objid'],x['objid']) for x in colinfo)
    )
    decoder.update({'_adm-rowid':obj['objid']+'"."_adm-rowid'})
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
        whereCol = '"%s"' % colid
        
        try:
            whereCond = '"%s"' % decoder[whereCond]
        except (KeyError,TypeError):
            try:
                whereCondCol = api.get_byid(whereCond)
                whereCond = '"' + whereCondCol['objid'] + '"'
            except common.errors.RelationDoesNotExist:
                sub = subid()
                fmtstring = '%(' + sub + ')s'
                col_type = api.get_byid(colid)['datatype']
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
