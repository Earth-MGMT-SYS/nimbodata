"""Module implements general expressions in select queries for nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *
from prototype import BinaryExpression

class Where(object):
    """Base class for any math function in PostgreSQL."""
    
    @staticmethod
    def sql(where,decoder,j_decoder,mode=None):
        params = {}
        w_params = {}
        if where is not None and where != [] and where != {}:
            
            stub = "WHERE \n" if mode is None else ''
            
            def process_clause(clause):
                clause = BinaryExpression(clause)
                clstr,c_params,cw_params = clause.sql_exp(decoder,j_decoder)
                params.update(c_params)
                w_params.update(cw_params)
                return clstr
            
            if isinstance(where,basestring) or isinstance(where,tuple):
                where = [where]
            elif isinstance(where,BinaryExpression) or 'Binary' in type(where).__name__:
                if isinstance(where.data,dict):
                    where = where.data
                elif not isinstance(where,dict):
                    where = [where.data]
                else:
                    where = where.data
            elif isinstance(where,dict) and 'fname' in where:
                where = [where]
            
            if isinstance(where,list):
                if len(where) == 3 and where[1] in operators:
                    where = [tuple(where)]
                whereClauses = []
                for whereClause in where:
                    whereClauses.append(process_clause(whereClause))
                stmt = stub + ' AND '.join(whereClauses) + "\n"
                return stmt, params
            
            try:
                _all = ' AND '.join(process_clause(x) for x in where['all'])
                if _all == '':
                    _all = None
            except (KeyError,TypeError):
                _all = None
                        
            try:
                _any = ' OR '.join(process_clause(x) for x in where['any'])
                if _any == '':
                    _any = None
            except (KeyError,TypeError):
                _any = None
            
            whereStmt = ''
            if _all is not None and _any is None:
                whereStmt += '(' + _all + ')'
            elif _all is None and _any is not None:
                whereStmt += '(' + _any + ')'
            elif _all is not None and _any is not None:
                whereStmt += '(' + _all + ') AND (' + _any + ')'
            
            if _all is not None or _any is not None:
                where_sub = {'all':_all,'any':_any}
                where_sub.update(w_params)
                whereStmt = whereStmt % where_sub
                stmt = stub + whereStmt
                return stmt, params
        
        return "", params
