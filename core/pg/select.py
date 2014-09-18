"""Module implements query functionality against Nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith

import string,random,copy

import psycopg2

import engine
import common.errors as errors
import common.results as results
import entities
import syntax
import datatypes
import common.comparable as comparable

def subid():
    return ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase)
            for dontcare in range(10)
    )

class Select(engine.Engine):
    """A customized Postgres engine providing various query capabilities."""
    allowed_funcs = ['max','min','avg']

    def __init__(self):
        """Instantiate the PG engine as dql_agent and set session read-only."""
        engine.Engine.__init__(self,'dql_agent')
        self.conn.set_session(readonly=True,autocommit=True)
    
    def _qtn(self,viewinfo):
        """Given the info for a relation, return the qualified table name."""
        return '"%(dbid)s"."%(relationid)s"' % {
            'dbid':viewinfo['parent_objid'],
            'relationid':viewinfo['objid']
        }
    
    def _target(self,viewid,cols,join,alias=True,viewcreate=False):
        """Process the target columns into SQL and parameters."""
        stmt = """\nSELECT """
        viewinfo = api.get_byid(objid=viewid)
        viewname = viewinfo['name']
        colinfo = viewinfo.columns()
        colinfo_by_colname = dict((x['name'],x) for x in colinfo)
        
        decoder = dict((x['name'],x['objid']) for x in colinfo)
        decoder.update(
            dict((viewname+"."+x['name'],x['objid']) for x in colinfo)
        )
        decoder.update(
            dict((x['objid'],x['objid']) for x in colinfo)
        )
        
        geocols = [x['name'] for x in viewinfo.geo_columns()]
                
        join_stmt = ""
        
        if join is not None:
            try:
                joininfo = join[0].info
            except:
                join[0] = api.get_byid(objid=join[0])
                joininfo = join[0].info
            j_colinfo = join[0].columns()
            j_viewname = joininfo['name']
            
            j_decoder = dict((x['name'],x['objid']) for x in j_colinfo)
            j_decoder.update(
                dict((x['objid'],x['objid']) for x in j_colinfo)
            )
            j_decoder.update(
                dict((j_viewname+"."+x['name'],x['objid']) for x in j_colinfo)
            )
            
            if alias:
                join_stmt += """JOIN  "%(joinview)s" AS "%(joinshort)s"\nON """
            else:
                join_stmt += """JOIN  "%(joinview)s"\nON """
            
            strSub = {}
            strSub['joinshort'] = joininfo['name']
            strSub['joinview'] = joininfo['parent_objid']+'"."'+joininfo['objid']
            
            join_stmt = join_stmt % strSub
            
            if isinstance(join[1],basestring):
                whereCol, whereCmp, whereCond = join[1].split(' ')
            else:
                whereCol, whereCmp, whereCond = join[1]
            whereCol = '"%s"' % decoder[whereCol]
            whereCond = '"%s"' % j_decoder[whereCond]
            
            if whereCmp not in comparable.operators:
                raise ValueError("Invalid comparison operator")
            
            join_stmt += ' '.join((whereCol,whereCmp,whereCond))
        
        
        # COLUMNS
        if (cols is None or cols == '') and join is None:
            cols = [x['name'] for x in colinfo]
            out_colinfo = [colinfo_by_colname[x].row_dict for x in cols]
        elif (cols is None or cols == '') and join is not None:
            cols = [viewname+"."+x['name'] for x in colinfo]
            out_colinfo = [x.row_dict for x in colinfo]
            for x in out_colinfo:
                x['name'] = viewname+'.'+x['name']
            cols += [j_viewname+'.'+x['name'] for x in j_colinfo]
            j_colinfo = [x.row_dict for x in j_colinfo]
            for x in j_colinfo:
                x['name'] = j_viewname+'.'+x['name']
            out_colinfo += j_colinfo
            
        else:
            # Otherwise we need a lookup tool
            out_colinfo = []
            for col in cols:
                if col == '_adm-rowid':
                    continue
                try:
                    out_colinfo.append(colinfo_by_colname[col].row_dict)
                except KeyError:
                    out_colinfo.append(entities.Column(col.replace('"','')).row_dict)
                except TypeError:
                    col = tuple(col)
                    out_colinfo.append(colinfo_by_colname[col[1]].row_dict)
                
        # Now, we dance.  With the columns... to build the target for select
        col_sub = []
        
        for i,colspec in enumerate(cols):
            if colspec == '_adm-rowid':
                colid = '_adm-rowid'
                colname = '_adm-rowid'
                funcname = None
                continue
            
            # This is truly silly
            try:
                try:
                    colid = decoder[colspec]
                except TypeError:
                    colspec = tuple(colspec)
                    colid = decoder[colspec]
                except KeyError:
                    try:
                        colid = j_decoder[colspec]
                    except TypeError:
                        colspec = tuple(colspec)
                        colid = j_decoder[colspec]
                colname = colspec
                funcname = None
            except KeyError:
                if colspec[0] not in self.allowed_funcs:
                    print colspec[0]
                    raise errors.InvalidFunction
                colid = decoder[colspec[1]]
                colname = colspec[1]
                funcname = colspec[0]
            
            if colname in geocols:
                colStr = datatypes.Geographic().sql_target(colid,colname,alias,viewcreate)
            elif funcname is not None:
                colStr = datatypes.Function().sql_target(colid,funcname)
            else:
                colStr = datatypes.Datatype().sql_target(colid,colname,alias)
            
            col_sub.append(colStr)        
        
        stmt += ', '.join(col_sub) + "\n"
                
        return stmt, join_stmt, {}, out_colinfo, decoder
    
    def _from(self,viewinfo):
        """Process the FROM component of the select query."""
        viewid = viewinfo['objid']
        stub = 'FROM %(qtn)s AS "%(viewname)s" ' % {
            'qtn':self._qtn(viewinfo),
            'viewname':viewinfo['name']
        }
        return stub,{}
        
    def _where(self,where,decoder):
        """Process the WHERE component of the select query."""
        params = {}
        w_params = {}
        if where is not None and where != [] and where != {}:
            
            def process_clause(whereClause):                
                if isinstance(whereClause,basestring):
                    whereCol, whereCmp, whereCond = whereClause.split(' ')
                else:
                    if isinstance(whereClause,comparable.WhereClause):
                        whereCol, whereCmp, whereCond = whereClause.data
                    else:
                        try:
                            whereCol, whereCmp, whereCond = whereClause
                        except ValueError as e:
                            print type(whereClause), whereClause
                
                colid = decoder[whereCol]
                whereCol = '"%s"' % colid
                
                try:
                    whereCond = '"%s"' % decoder[whereCond]
                except (KeyError,TypeError):
                    try:
                        whereCondCol = entities.Column(objid=str(whereCond))
                        whereCond = '"' + whereCondCol['objid'] + '"'
                    except errors.RelationDoesNotExist:
                        sub = subid()
                        fmtstring = '%(' + sub + ')s'
                        col_type = entities.Column(colid)['datatype']
                        col_type = getattr(datatypes,col_type)
                        # Is fail permissive a good idea??? I don't know.
                        try:
                            params[sub] = col_type(whereCond)
                        except (TypeError,ValueError):
                            params[sub] = whereCond
                        w_params[sub] = fmtstring
                        whereCond = fmtstring

                
                if whereCmp not in comparable.operators:
                    raise ValueError("Invalid comparison operator")
                
                return ' '.join((whereCol,whereCmp,whereCond))
            
            
            if isinstance(where,basestring) or isinstance(where,tuple):
                where = [where]
            
            elif isinstance(where,comparable.WhereClause):
                if isinstance(where.data,dict):
                    where = where.data
                elif not isinstance(where,dict):
                    where = [where.data]
                else:
                    where = where.data
            
            if isinstance(where,list):
                if len(where) == 3 and where[1] in comparable.operators:
                    where = [tuple(where)]
                whereClauses = []
                for whereClause in where:
                    whereClauses.append(process_clause(whereClause))
                stmt = "WHERE \n" + ' AND '.join(whereClauses) + "\n"
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
            
            if _all is None and _any is None:
                pass
            else:
                where_sub = {'all':_all,'any':_any}
                where_sub.update(w_params)
                whereStmt = whereStmt % where_sub
                stmt = "WHERE" + whereStmt
                return stmt, params
        
        
        return "", params
        
    def _group_by(self,group_by):
        """Process the GROUP BY component of a select query."""
        if group_by is not None:
            stmt = '''GROUP BY "''' + '", "'.join(group_by) + '"'
        else:
            stmt = ""
        return stmt, {}
        
    def _order_by(self,order_by,decoder):
        stmt = ""
        if order_by is not None and order_by != []:
            order_parts = []
            
            if isinstance(order_by,basestring):
                order_by = [order_by]
            
            for orderClause in order_by:
                split = orderClause.split(' ')
                if len(split) == 2 and split[1].lower() not in ('asc','desc','dsc'):
                    raise ValueError("Invalid sort directive")
                split[0] = '"' + decoder[split[0]] + '"'
                order_parts.append(' '.join(split))
            
            stmt = "ORDER BY " + ' , '.join(order_parts) + '\n'
            
        return stmt, {}
    
    def _limit(self,limit):
        """Process the LIMIT component of a select query."""
        stmt = ""
        if limit is not None:
            stmt += "LIMIT " + str(int(limit))
        return stmt, {}
    
    def _prepare_select(self,viewid=None,cols=None,join=None,where=None,
               group_by=None,order_by=None,limit=None,alias=True,viewcreate=False):
        """Takes all of the select parameters and returns SQL and sub params."""
        # First we get the prerequisite info to build the query
        viewinfo = api.get_byid(viewid)
        dbid,viewname = viewinfo['parent_objid'],viewinfo['name']
        viewid = viewinfo['objid']
        
        colinfo = api.get_byid(objid=viewid).columns()
        
        stmt, join_stmt, params, out_colinfo, decoder = self._target(
            viewid,cols,join,alias,viewcreate
        )
        
        from_stmt,from_params = self._from(viewinfo)
        stmt += from_stmt + "\n"
        params.update(from_params)
        
        stmt += join_stmt + "\n"
        
        where_stmt, where_params = self._where(where,decoder)
        stmt += where_stmt + "\n"
        params.update(where_params)
                
        group_stmt, group_params = self._group_by(group_by)
        stmt += group_stmt + "\n"
        params.update(group_params)
        
        order_stmt, order_params = self._order_by(order_by,decoder)
        stmt += order_stmt + '\n'
        params.update(order_params)
        
        limit_stmt, limit_params = self._limit(limit)
        stmt += limit_stmt
        params.update(limit_params)
        
        return stmt,params,out_colinfo
    
    def get_array(self,viewid=None,col=None,join=None,where=None,
               group_by=None,order_by=None,limit=None):
        """Returns an array of a single column from a select query."""
        stmt,params,out_colinfo = self._prepare_select(
            viewid,
            [col],
            join,where,
            group_by,
            order_by,limit
        )
        
        if stmt is None and out_colinfo is None:
            return []
        
        r = self.execute(stmt,params)
        
        return [x[0] for x in r]
    
    def get_byrowid(self,viewid,ids,alias=False):
        """Returns a row from a specified relation."""
        viewinfo = entities.Entity(str(viewid))
        if bool(alias) is False:
            label = lambda x: x['name']
        elif bool(alias) is True:
            label = lambda x: x['name'] if x['alias'] is None else x['alias']
        ent = getattr(entities,viewinfo['entitytype'])
        cols = [label(x) for x in ent(objid=viewid).columns()]
        dbid = viewinfo['parent_objid']
        if isinstance(ids,basestring):
            stmt = """SELECT * FROM %(tqn)s WHERE "_adm-rowid" = %(rowid)s"""
            stmt = stmt % {
                'tqn':syntax._get_tqn(dbid,viewid),
                'rowid':'%s'
            }
            begin_index = 2 if str(viewid).startswith('tbl') else 1
            return [(col,val) for col,val in 
                    zip(cols,self._get_first(stmt,[ids])[begin_index:])]
        else:
            return [self.getby_id(viewid,x) for x in ids]

    def execute(self,stmt,params=None):
        """Execute the SQL statement using the provided parameters."""
        #print self.mogrify(stmt,params)
        return engine.Engine.execute(self,stmt,params)

    def select(self,viewid=None,cols=None,join=None,where=None,
               group_by=None,order_by=None,limit=None):
        """Execute a select query."""
        stmt,params,out_colinfo = self._prepare_select(
            viewid,cols,join,where,group_by,order_by,limit
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
            raise e
        
        view = api.get_byid(viewid)
        viewinfo = view.info
        viewinfo['cols'] = view.columns()

        return results.Results(out_colinfo,list(r),viewinfo)
