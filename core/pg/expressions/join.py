"""Module implements join expressions in select queries for nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *

from common import errors

class Join(base.Join):
    """Represent a nimbodata query join expression."""

    def join_cols(self,src,cols=None):
        
        colinfo = src.columns()
        
        if cols is None or cols == '':
            cols = [src['name']+"."+x['name'] for x in colinfo]
            try:
                out_colinfo = [x.row_dict for x in colinfo]
            except AttributeError:
                out_colinfo = [x for x in colinfo]
            for x in out_colinfo:
                x['name'] = src['name']+'.'+x['name']
            cols += [self.target['name']+'.'+x['name'] for x in self.target.columns()]
            try:
                j_colinfo = [x.row_dict for x in self.target.columns()]
            except AttributeError:
                j_colinfo = self.target.columns()
            for x in j_colinfo:
                x['name'] = self.target['name']+'.'+x['name']
            out_colinfo += j_colinfo
            
        return cols,out_colinfo
    
    def sql_exp(self,alias,decoder):
        """Process a canonical join statement into validated SQL."""
        
        try:
            joininfo = self.target.info
        except AttributeError:
            try:
                tobj = self.target['objid']
                self.target = api.get_byid(objid=tobj)
            except TypeError:
                self.target = api.get_byid(objid=self.target)
            except KeyError:
                print self.target
            joininfo = self.target.info
            
        if not joininfo['parent_objid'].startswith('dbi'):
            tbl = api.get_byid(joininfo['parent_objid'])
            joininfo['parent_objid'] = tbl['parent_objid']
        
        j_colinfo = self.target.columns()
        j_viewname = self.target['name']
        
        j_decoder = prototype.get_decoder(self.target)
        for jcol in j_colinfo:
            decoder[jcol['objid']] = jcol['objid']
        
        if alias:
            join_stmt = """JOIN  "%(joinview)s" AS "%(joinshort)s"\nON """
        else:
            join_stmt = """JOIN  "%(joinview)s"\nON """
        
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
            src_cols = set(get_base(x['name']) for x in self.src.columns())
            trg_cols = set(get_base(x['name']) for x in self.target.columns())
            overlap = src_cols.intersection(trg_cols)
            if len(overlap) != 1:
                print src_cols, trg_cols
                raise ValueError("Join condition unclear, must specify")
            else:
                oncol = overlap.pop()
                whereCol,whereCmp,whereCond = decoder[oncol],'=',j_decoder[oncol]
        else:
            try:
                whereCol, whereCmp, whereCond = self.on.data
            except ValueError:
                whereCmp = self.on.data['fname']
                whereCol, whereCond = self.on.data['args']
        
        try:
            whereCol = '"%s"' % decoder[whereCol]
        except KeyError:
            print whereCol
            whereCol = '"%s"' % decoder[whereCol.split('.')[1]]
        whereCond = '"%s"' % j_decoder[whereCond]
        
        if whereCond == whereCol:
            whereCol = ('"%s".' + whereCol) % self.src['objid']
            whereCond = ('"%s".' + whereCond) % joininfo['objid']
        
        return join_stmt + ' '.join((whereCol,whereCmp,whereCond)),j_decoder
