"""Module implements join expressions in select queries for nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *
from prototype import TwoValExpression
from where import Where

try:
    from common import errors
except ImportError:
    from nimbodata.common import errors

class Join(base.Join):
    """Represent a nimbodata query join expression."""
    jtype = ""

    def join_cols(self,src,cols=None):
        
        colinfo = src['cols']
        jcols = self.target.columns()
        self.cols = colinfo
        self.jcols = jcols
        
        if cols is None or cols == '':
            cols = [src['name']+"."+x['name'] for x in colinfo]
            try:
                out_colinfo = [x.row_dict for x in colinfo]
            except AttributeError:
                out_colinfo = [dict(x) for x in colinfo]
            for x in out_colinfo:
                x['name'] = src['name']+'.'+x['name']
            cols += [self.target['name']+'.'+x['name'] for x in jcols]
            try:
                j_colinfo = [x.row_dict for x in jcols]
            except AttributeError:
                j_colinfo = jcols
            for x in j_colinfo:
                x['name'] = self.target['name']+'.'+x['name']
            out_colinfo += j_colinfo
            
        return cols,out_colinfo
    
    def sql_exp(self,alias,decoder):
        """Process a canonical join statement into validated SQL."""
        
        try:
            joininfo = self.target.row_dict
        except AttributeError:
            try:
                tobj = self.target['objid']
                self.target = api.get_byid(objid=tobj)
            except TypeError:
                self.target = api.get_byid(objid=self.target)
            joininfo = self.target.row_dict
            
        if not joininfo['parent_objid'].startswith('dbi'):
            tbl = api.get_byid(joininfo['parent_objid'])
            joininfo['parent_objid'] = tbl['parent_objid']
        
        j_colinfo = self.target.columns()
        j_viewname = self.target['name']
        
        j_decoder = prototype.get_decoder(self.target)
        for jcol in j_colinfo:
            decoder[jcol['objid']] = (joininfo['objid'],jcol['objid'])
        
        join_stmt = self.jtype + """ JOIN  "%(joinview)s"\nON """
        
        strSub = {}
        strSub['joinshort'] = joininfo['name']
        strSub['joinview'] = joininfo['parent_objid']+'"."'+joininfo['objid']
        
        join_stmt = join_stmt % strSub
        
        def get_base(item):
            """If the colname has been joined in the past, namespace."""
            if '.' in item:
                return item.split('.')[1]
            else:
                return item
        
        if self.on is None:
            try:
                src_cols = set(get_base(x['name']) for x in self.cols)
                trg_cols = set(get_base(x['name']) for x in self.jcols)
            except AttributeError:
                src_cols = set(get_base(x['name']) for x in self.src.columns())
                trg_cols = set(get_base(x['name']) for x in self.target.columns())
            overlap = src_cols.intersection(trg_cols)
            if len(overlap) != 1:
                oncol = '_adm-rowid'
                whereCol,whereCmp,whereCond = '_adm-rowid','=','_adm-rowid'
            else:
                oncol = overlap.pop()
                whereCol,whereCmp,whereCond = decoder[oncol],'=',j_decoder[oncol]
        else:
            try:
                whereCol, whereCmp, whereCond = self.on.data
            except ValueError:
                if 'fname' not in self.on.data:
                    jstmt, params = Where.sql(self.on,decoder,j_decoder,'join')
                    return join_stmt + '\n' + jstmt, j_decoder
                elif len(self.on.data['fname']) > 1:
                    whereCmp = None
                else:
                    whereCmp = self.on.data['fname']
                whereCol, whereCond = self.on.data['args']
        
        try:
            print decoder[whereCol]
            whereCol = '"%s"."%s"' % decoder[whereCol]
        except KeyError:
            whereCol = '"%s"."%s"' % whereCol # Make sure this gets validated...
        try:
            whereCond = '"%s"."%s"' % j_decoder[whereCond]
        except KeyError:
            whereCond = '"%s"."%s"' % whereCond
        
        if whereCond == whereCol:
            whereCol = ('"%s".' + whereCol) % self.src['objid']
            whereCond = ('"%s".' + whereCond) % joininfo['objid']
        
        if whereCmp is None:
            return join_stmt + ' %(func)s ( %(a)s, %(b)s ) ' % {
                'func':self.on.data['fname'],
                'a': whereCol,
                'b': whereCond
            }, j_decoder
        else:
            return join_stmt + ' '.join((whereCol,whereCmp,whereCond)),j_decoder

class LeftOuterJoin(Join):
    """Left Outer Join"""
    jtype = "LEFT OUTER"
    
class RightOuterJoin(Join):
    """Right Outer Join"""
    jtype = "RIGHT OUTERr"
    
class FullOuterJoin(Join):
    """Full Outer Join"""
    jtype = "FULL OUTER"
