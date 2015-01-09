"""Module implements query functionality against Nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith

import string,random,copy
from uuid import uuid4 as uuid
from collections import OrderedDict

import psycopg2

try:
    import common.errors as errors
    import common.results as results
except ImportError:
    import nimbodata.common.errors as errors
    import nimbodata.common.results as results

import engine
import entities
import syntax
import datatypes
import expressions


def subid():
    return ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase)
            for dontcare in range(10)
    )
    
def _newcolid():
    """ Creates a new UUID4 prefixed with the correct objid prefix """
    return 'col-'+str(uuid()).replace('-','')

class Select(engine.Engine):
    """A Postgres engine providing various query capabilities."""
    valid_dtypes = datatypes.valid

    def __init__(self):
        """Instantiate the PG engine as dql_agent and set session read-only."""
        engine.Engine.__init__(self,'dql_agent')
        self.conn.set_session(readonly=True,autocommit=True)
    
    def _qtn(self,viewinfo):
        """Given the info for a relation, return the qualified table name."""
        parent_db = api.get_byid(viewinfo['parent_objid'])['parent_db']
        return '"%(dbid)s"."%(relationid)s"' % {
            'dbid':parent_db,
            'relationid':viewinfo['objid']
        }
    
    def _target(self,objid,cols,join,alias=True,viewcreate=False):
        """Process the target columns into SQL and parameters."""
        # PREP
        stmt = """\nSELECT """
        viewinfo = self.viewinfo
        colinfo = viewinfo['cols']
        viewname = viewinfo['name']
        def fqn(parent,info):
            return (parent['objid'],info['objid'])
        colinfo_by_colname = dict((x['name'],fqn(viewinfo,x)) for x in colinfo)
        colinfo_by_colid = dict((fqn(viewinfo,x),x) for x in colinfo)
        colname_by_colid = dict((fqn(viewinfo,x),x['name']) for x in colinfo)
        colalias_by_colid = dict(
            (fqn(viewinfo,x),x['alias'] if x['alias'] else x['name'])
                for x in colinfo
        )
        
        decoder = expressions.get_decoder(viewinfo)
        j_decoder = {}
        
        geo = viewinfo.geo_columns()
        geocols = [x['name'] for x in geo]
        geocolids = [x['objid'] for x in geo]
                
        # JOIN
        join_stmt = ""
        if join is not None:
            try:
                if isinstance(join[0],basestring):
                    raise TypeError
                jrepl = []
                for jstmt in join:
                    j = expressions.Join(jstmt)
                    j.src = viewinfo
                    jadd, jdadd = j.sql_exp(alias,decoder)
                    join_stmt += ("\n" + jadd + "\n")
                    j_decoder.update(jdadd)
                    jrepl.append(j)
                join = jrepl
                    
            except TypeError:
                join = expressions.Join(join)
                join.src = viewinfo
                join_stmt,j_decoder = join.sql_exp(alias,decoder)
                    
        aggregate = False  # not 1-to-1 between rowids and results?
        grouprowid = False
                
        # COLUMNS
        if (cols is None or cols == '') and join is None:
            # SELECT * FROM SINGLEVIEW
            cols = [x['objid'] for x in colinfo]
            try:
                out_colinfo = [x.row_dict for x in colinfo]
            except AttributeError:
                out_colinfo = colinfo
        elif (cols is None or cols == '') and join is not None:
            # SELECT * FROM VIEW JOIN OTHERVIEW
            try:
                cols,out_colinfo = join.join_cols(viewinfo)
            except AttributeError:
                cols, out_colinfo = [],[]
                for j in join:
                    if not isinstance(j,expressions.Join):
                        j = expressions.Join(j)
                    jcols, jout = j.join_cols(viewinfo)
                    cols += jcols
                    out_colinfo += jout
        else:
            # Otherwise we need a lookup tool
            out_colinfo = []
            if join is not None:
                try:
                    dontcare,jcolinfo = join.join_cols(viewinfo)
                    try:
                        joininfo = api.get_byid(join[0])
                    except TypeError:
                        joininfo = api.get_byid(join.target)
                    colinfo_by_colid.update(
                        dict((fqn(joininfo,x),x) for x in jcolinfo)
                    )
                    colalias_by_colid.update(
                        dict((fqn(joininfo,x),x['alias']) for x in jcolinfo)
                    )
                    colname_by_colid.update(
                        dict((fqn(joininfo,x),x['name']) for x in jcolinfo)
                    )
                except AttributeError:
                    dontcare, jcolinfo = [],[]
                    for j in join:
                        if not isinstance(j,expressions.Join):
                            j = expressions.Join(j)
                        jcols, jout = j.join_cols(viewinfo)
                        dontcare += jcols
                        jcolinfo += jout
                        try:
                            joininfo = api.get_byid(j[0])
                        except TypeError:
                            joininfo = api.get_byid(j.target)
                        colinfo_by_colid.update(
                            dict((fqn(joininfo,x),x) for x in jcolinfo)
                        )
                        colalias_by_colid.update(
                            dict((fqn(joininfo,x),x['alias']) for x in jcolinfo)
                        )
                        colname_by_colid.update(
                            dict((fqn(joininfo,x),x['name']) for x in jcolinfo)
                        )
            
            for col in cols:
                if col == '_adm-rowid':
                    if grouprowid is False:
                        grouprowid = 'Maybe'
                    elif grouprowid == 'Maybe':
                        grouprowid = True
                    continue
                else:
                    try: #Simple case, column specified by name or id in main table
                        try:
                            col = decoder[col]
                        except KeyError:
                            col = j_decoder[col]
                        inf = colinfo_by_colid[col]
                        try:
                            inf = inf.row_dict
                        except AttributeError: # Views returns actual dicts now
                            pass
                    except TypeError: # The column is complex
                        if 'newname' in col: # Simple AS
                            col_a = decoder[col['col']]
                            col_b = None
                            inf = colinfo_by_colid[col_a]
                            try:
                                inf = inf.row_dict
                            except AttributeError:
                                pass
                            inf['name'] = col['newname']
                            if col['newalias'] is not None:
                                inf['alias'] = col['newalias']
                        else: # Full expression
                            if col['fname'] in ('MAX','MIN','AVG','unique'):
                                aggregate = True
                            
                            try:
                                col_a = decoder[col['args'][0]]
                            except KeyError:
                                col_a = j_decoder[col['args'][0]]
                            try:
                                col_b = decoder[col['args'][1]]
                            except IndexError:
                                col_b = None
                            except KeyError:
                                try:
                                    col_a = j_decoder[col['args'][1]]
                                except KeyError:
                                    col_b = col['args'][1]
                            
                            if col['fname'] in expressions.operators:
                                inf = colinfo_by_colid[col_a]
                                
                                try:
                                    inf = inf.row_dict
                                except AttributeError:
                                    pass
                                
                                try:
                                    b = colname_by_colid[col_b]
                                    b_alias = colalias_by_colid[col_b]
                                except KeyError:
                                    b_alias = b = col['args'][1]
                                    
                                inf['alias'] = "%(a)s %(op)s %(b)s"%{
                                    'a':colalias_by_colid[col_a],
                                    'b':b_alias,
                                    'op':col['fname']
                                }
                                
                                inf['name'] = "%(a)s %(op)s %(b)s"%{
                                    'a':colname_by_colid[col_a],
                                    'b':b,
                                    'op':col['fname']
                                }
                            else:
                                inf = api.get_entity('Column')(col_a[1],func=col)
                                try:
                                    inf = inf.row_dict
                                except AttributeError:
                                    pass
                                if col['fname'] in datatypes.valid:
                                    inf['datatype'] = col['fname']
                                    
                                    inf['name'] = '%(datatype)s(%(name)s)' % inf
                                    
                                    if inf['alias']:
                                        inf['alias'] = '%(datatype)s(%(alias)s)' % inf
                                
                                else:
                                    try:
                                        colid = decoder[col['args'][0]]
                                    except KeyError:
                                        colid = j_decoder[col['args'][0]]
                                    if len(col['args']) == 1:
                                        inf['name'] = '%(fname)s(%(arg1)s)' % {
                                            'fname':col['fname'],
                                            'arg1':colname_by_colid[colid],
                                        }
                                        if inf['alias']:
                                            inf['alias'] = '%(fname)s(%(arg1)s)' % {
                                                'fname':col['fname'],
                                                'arg1':colalias_by_colid[colid],
                                            }
                                    elif len(col['args']) == 2:
                                        inf['name'] = '%(fname)s(%(arg1)s,%(arg2)s)' % {
                                            'fname':col['fname'],
                                            'arg1':colname_by_colid[colid],
                                            'arg2':col['args'][1]
                                        }
                                        if inf['alias']:
                                            inf['alias'] = '%(fname)s(%(arg1)s,%(arg2)s)' % {
                                                'fname':col['fname'],
                                                'arg1':colalias_by_colid[colid],
                                                'arg2':col['args'][1]
                                            }
                                    
                            newcol = _newcolid()
                            inf['objid'] = newcol
                            if viewcreate:
                                inf['newcol'] = True
                            col['viewcolid'] = newcol
                        
                    out_colinfo.append(inf)
        
        # Now, we dance.  With the columns... to build the target for select
        col_sub,params = [],{}
        colname = False
        if grouprowid is True:
            cols = cols[1:]
        for i,colspec in enumerate(cols):
            fargs, dtype, colStr,funcname = None, None, None, None
            if colspec == '_adm-rowid' and (aggregate is False or grouprowid is True):
                colid = '%s"."_adm-rowid' % viewinfo['objid']
                colname = '_adm-rowid'
                colStr = '"%s"."_adm-rowid" AS "_adm-rowid"' % viewinfo['objid']
            elif colspec == '_adm-rowid' and aggregate is True:
                continue
            elif isinstance(colspec,dict) and 'newname' in colspec:
                # if the value is transformed in some way it becomes a new col.
                colname = colspec['newname']
                colid = decoder[col['col']]
            elif isinstance(colspec,dict):
                funcname = colspec['fname']
                fargs = list(colspec['args'])
                try:
                    colid = decoder[fargs[0]]
                except KeyError:
                    colid = j_decoder[fargs[0]]
                if funcname in self.valid_dtypes:
                    dtype = getattr(datatypes,funcname)
            elif len(colspec) > 1 and colspec[1] in expressions.operators:
                colStr = str(expressions.BinaryExpression(*colspec))
            else:
                try:
                    try:
                        colid = decoder[colspec]
                    except KeyError:
                        colid = j_decoder[colspec]
                    colname = colspec
                except KeyError:
                    raise errors.InvalidFunction
            
            if colStr is not None:
                pass
            elif dtype is not None:
                try:
                    colStr,params = dtype.sql_target(colspec)
                except TypeError:
                    colStr,params = dtype.sql_cast(colspec)
            elif colname in geocols:
                colStr = datatypes.Geographic().sql_target(
                    colid,colname,alias,viewcreate
                )
            elif colname in geocolids:
                colStr = datatypes.Geographic().sql_target(
                    colid,colid,alias,viewcreate
                )
            elif funcname is not None and fargs is None:
                try:
                    func = getattr(expressions,funcname)
                    colStr = func().sql_exp(colid)
                except AttributeError:
                    colStr = datatypes.Function().sql_exp(funcname,colid)
            elif funcname is not None and fargs is not None:
                if funcname in expressions.operators:
                    colStr, t_params, ts_params = expressions.BinaryExpression(
                        {'fname':funcname,'args':fargs}
                    ).sql_exp(decoder,j_decoder)
                    colStr = colStr % ts_params
                    colStr += ' AS "%s"' % colspec['viewcolid']
                    params.update(t_params)
                else:
                    try:
                        func = getattr(expressions,funcname)
                        if 'viewcolid' not in colspec:
                            colspec['viewcolid'] = None
                        if len(fargs) > 1:
                            colStr = func().sql_target(
                                colid,fargs[1],colspec['viewcolid']
                            )
                        else:
                            colStr = func().sql_target(colid,colspec['viewcolid'])
                    except AttributeError:
                        colStr = datatypes.Function().sql_exp(funcname,colid,*fargs)
            else:
                colStr = datatypes.Datatype().sql_target(colid,colname,alias)
            
            col_sub.append(colStr)   
            
        orderedset = OrderedDict((x,None) for x in col_sub)
        col_sub = orderedset.keys()
        
        stmt += ', '.join(col_sub) + "\n"
                
        return stmt, join_stmt, params, out_colinfo, decoder, j_decoder, aggregate
    
    def _from(self,viewinfo):
        """Process the FROM component of the select query."""
        viewid = viewinfo['objid']
        stub = 'FROM %(qtn)s  ' % {
            'qtn':self._qtn(viewinfo),
            'viewname':viewinfo['name']
        }
        return stub,{}
        
    def _where(self,where,decoder,j_decoder):
        """Process the WHERE component of the select query."""
        return expressions.Where.sql(where,decoder,j_decoder)
        
    def _group_by(self,group_by,decoder,aggregate=False):
        """Process the GROUP BY component of a select query."""
        if group_by is not None:
            try:
                stmt = '''GROUP BY "''' + '", "'.join(
                    '%s"."%s' % decoder[x] for x in group_by
                ) + '"'
            except (KeyError,TypeError):
                if aggregate:
                    gb = []
                else:
                    gb = ['"'+decoder['_adm-rowid']+'"']
                for item in group_by:
                    if item == '_adm-rowid' and aggregate:
                        gb.append('"%s"."%s"' % decoder['_adm-rowid'])
                        continue
                    try:
                        gb.append('"%s"."%s"' % decoder[item])
                        continue
                    except (TypeError,KeyError):
                        pass
                    try:
                        gb.append('"'+api.get_byid(item)['objid']+'"')
                    except errors.RelationDoesNotExist:
                        print item
                        func = getattr(expressions,item['fname'])
                        colStr = func().sql_cast(*item['args'])
                        gb.append(colStr)
                stmt = '''GROUP BY ''' + ' , '.join(gb)
        else:
            stmt = ""
        return stmt, {}
        
    def _order_by(self,order_by,decoder,j_decoder):
        stmt = ""
        params = {}
        if order_by is not None and order_by != []:
            order_parts = []
            
            
            if isinstance(order_by,basestring):
                order_by = [order_by]
            
            for orderClause in order_by:
                try:
                    split = orderClause.split(' ')
                except AttributeError:
                    split = orderClause
                try:
                    if len(split) == 2 and split[1].lower() not in ('asc','desc'):
                        raise ValueError("Invalid sort directive")
                    try:
                        fqn = decoder[split[0]][0] + '"."' + decoder[split[0]][1]
                        split[0] = '"' + fqn + '"'
                    except KeyError:
                        fqn = j_decoder[split[0]][0] + '"."' + j_decoder[split[0]][1]
                        split[0] = '"' + fqn + '"'
                    order_parts.append(' '.join(split))
                except KeyError:
                    try:
                        func = getattr(expressions,orderClause['fname'])
                        colStr = func().sql_cast(*orderClause['args'])
                    except AttributeError:
                        func = expressions.BinaryExpression(orderClause)
                        colStr, params, w_params = func.sql_exp(decoder,j_decoder)
                    order_parts.append(colStr)
                
            
            stmt = "ORDER BY " + ' , '.join(order_parts) + '\n'
            
        return stmt, params
    
    def _limit(self,limit):
        """Process the LIMIT component of a select query."""
        stmt = ""
        if limit is not None:
            stmt += "LIMIT " + str(int(limit))
        return stmt, {}
    
    def _prepare_select(self,objid=None,cols=None,join=None,where=None,
            group_by=None,order_by=None,limit=None,alias=True,viewcreate=False):
        """Takes all of the select parameters and returns SQL and sub params."""
        # First we get the prerequisite info to build the query
        try:
            if 'fname' in objid:
                viewinfo = None
            else:
                viewinfo = api.get_byid(objid)
        except KeyError:
            viewinfo = api.get_byid(objid)
        self.viewinfo = viewinfo
        if viewinfo is not None:
            if not viewinfo['parent_objid'].startswith('dbi'):
                parent = api.get_byid(viewinfo['parent_objid'])
                viewinfo = viewinfo.row_dict
                viewinfo['parent_objid'] = parent['parent_objid']
            
            dbid,viewname = viewinfo['parent_objid'],viewinfo['name']
            viewid = viewinfo['objid']
                    
            colinfo = api.get_byid(objid=objid).columns()
            
            stmt, join_stmt, params, out_colinfo, decoder, j_decoder, aggregate = \
                self._target(objid,cols,join,alias,viewcreate)
        
            from_stmt,from_params = self._from(viewinfo)
            stmt += from_stmt + "\n"
            stmt += join_stmt + "\n"
            params.update(from_params)
        else:
            colid = api.get_entity('Column')()._new_id()
            from_func = getattr(expressions,objid['fname'])
            from_stmt,params,out_colinfo = from_func(*objid['args']).sql_from(colid)
            stmt = ' SELECT * FROM ' + from_stmt
            decoder, j_decoder = {}, {}
            aggregate = False
        
        where_stmt, where_params = self._where(where,decoder,j_decoder)
        stmt += where_stmt + "\n"
        params.update(where_params)
                
        group_stmt, group_params = self._group_by(group_by,decoder,aggregate)
        stmt += group_stmt + "\n"
        params.update(group_params)
        
        order_stmt, order_params = self._order_by(order_by,decoder,j_decoder)
        stmt += order_stmt + '\n'
        params.update(order_params)
        
        limit_stmt, limit_params = self._limit(limit)
        stmt += limit_stmt
        params.update(limit_params)
                        
        return stmt,params,out_colinfo
    
    def get_array(self,objid=None,col=None,join=None,where=None,
            group_by=None,order_by=None,limit=None):
        """Returns an array of a single column from a select query."""
        stmt,params,out_colinfo = self._prepare_select(
            objid,
            [col],
            join,where,
            group_by,
            order_by,limit
        )
        
        if stmt is None and out_colinfo is None:
            return []
        
        r = self.execute(stmt,params)
        
        return [x[0] for x in r]
    
    def get_byrowid(self,objid,ids,alias=False):
        """Returns a row from a specified relation."""
        viewinfo = api.get_byid(objid)
        if bool(alias) is False:
            label = lambda x: x['name']
        elif bool(alias) is True:
            label = lambda x: x['name'] if x['alias'] is None else x['alias']
        ent = getattr(entities,viewinfo['entitytype'])
        cols = [label(x) for x in ent(objid).columns()]
        
        if not viewinfo['parent_objid'].startswith('dbi'):
            parent = api.get_byid(viewinfo['parent_objid'])
            viewinfo = viewinfo.row_dict
            viewinfo['parent_objid'] = parent['parent_objid']
        
        dbid = viewinfo['parent_objid']
        if isinstance(ids,basestring):
            stmt = """SELECT * FROM %(tqn)s WHERE "_adm-rowid" = %(rowid)s"""
            stmt = stmt % {
                'tqn':syntax._get_tqn(dbid,objid),
                'rowid':'%s'
            }
            begin_index = 2 if str(objid).startswith('tbl') else 1
            try:
                return [(col,val) for col,val in 
                    zip(cols,self._get_first(stmt,[ids])[begin_index:])]
            except TypeError:
                return [[]]
        else:
            return [self.getby_id(objid,x) for x in ids]

    def execute(self,stmt,params=None):
        """Execute the SQL statement using the provided parameters."""
        #print self.mogrify(stmt,params)
        return engine.Engine.execute(self,stmt,params)

    def select(self,objid=None,cols=None,join=None,where=None,
               group_by=None,order_by=None,limit=None,fname=None,args=None):
        """Execute a select query."""
        if isinstance(objid,dict) and 'fname' not in objid:
            p, vname = objid['parent'], objid['_objid']
            objid = api.get_byid(p).View(vname)['objid']
        if fname is not None and args is not None:
            objid = args[0]['objid']
            stmts = []
            params = {}
            out_colinfo = None
            for arg in args:
                stmt_a,params_a,out_colinfo_a = self._prepare_select(**arg)
                params.update(params_a)
                stmts.append(stmt_a)
                if out_colinfo is None:
                    out_colinfo = out_colinfo_a
            stmt = "\n UNION \n".join(stmts)
            
        else:
            stmt,params,out_colinfo = self._prepare_select(
                objid,cols,join,where,group_by,order_by,limit
            )
            
        if stmt is None and out_colinfo is None:
            return results.Results([],[])
                
        try:
            r = self.execute(stmt,params)
        except psycopg2.ProgrammingError as e:
            try:
                print self.mogrify(stmt,params)
            except:
                print stmt
            raise
        
        try:
            view = api.get_byid(objid)
            expressions.inject_api(api)
            viewinfo = view.row_dict
            viewinfo['cols'] = view.columns()
        except errors.RelationDoesNotExist:
            viewinfo = {}
        
        return results.Results(out_colinfo,list(r),viewinfo)
