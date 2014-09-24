"""Module implements PostgreSQL syntax implemented as Python functions."""
# Copyright (C) 2014  Bradley Alan Smith

###############################################################################
### UTILITY FUNCTIONS #########################################################
###############################################################################

def _get_tqn(schemaid,tblid):
    return '"' + str(schemaid) + '"."' + str(tblid) + '"'

get_tqn = _get_tqn

def _get_cqn(schemaid,tblid,colname):
    return '"' + schemaid + '"."' + tblid + '"."' + colname + '"'

###############################################################################
### DDL #######################################################################
###############################################################################    

def create_db(schemaid):
    stmt = """CREATE SCHEMA "%(schemaid)s" """
    subStr = {'schemaid':schemaid}
    return stmt % subStr

def create_table(schemaid,tblid):
    stmt = """CREATE TABLE %(tqn)s """
    subStr = {'tqn':_get_tqn(schemaid,tblid)}
    return stmt % subStr
    
def create_managed_table(schemaid,tblid):
    return"""
            CREATE TABLE %(qtn)s
                ("_adm-timestamp" timestamp with time zone DEFAULT clock_timestamp(),
                 "_adm-rowid" text DEFAULT "_adm-registries".newrowid())
           """ % {'qtn':get_tqn(schemaid,tblid)}

def create_view(schemaid,viewid,select,temporary=False):
    return ( """
        CREATE %(temp)s VIEW  %(qtn)s
        AS
        
    """ % {
            'qtn':get_tqn(schemaid,viewid),
            'temp': ' TEMPORARY ' if temporary else ''
          } 
    ) + select

def alter_column_type(schemaid,tblid,colid,newtype):
    stub = """
                ALTER TABLE %(qtn)s
                ALTER COLUMN "%(colid)s"
                TYPE %(coltype)s
           """
    if newtype != 'Text':
        stub += """
                USING
                    "_adm-registries"."to_%(coltype)s"("%(colid)s")
           """
    return stub % {
                    'qtn':get_tqn(schemaid,tblid),
                    'colid':colid,
                    'coltype':newtype
                 }
           
def add_column(schemaid,tblid,colid,dtype,pk=None):
    subStr = {
            'tqn':_get_tqn(schemaid,tblid),
            'const':'"' + str(tblid) + '_pkuq"',
            'colid':str(colid),
            'dtype':str(dtype),
            }
    if pk is None:
        stmt = """ALTER TABLE %(tqn)s ADD COLUMN "%(colid)s" %(dtype)s """
    elif pk is True:
        stmt = """
                ALTER TABLE %(tqn)s
                ADD COLUMN "%(colid)s" %(dtype)s,
                ADD CONSTRAINT %(const)s UNIQUE ("%(colid)s"),
                ADD PRIMARY KEY ("%(colid)s")  """
    return stmt % subStr

def add_index(schemaid,tblid,indid,colid,unique=False,index_type=None):
    stub = """
        CREATE %(uq)s INDEX "%(indid)s" ON "%(schemaid)s"."%(tblid)s" 
    """ 
    if index_type is not None:
        stub += """
            USING %(index_type)s ( "%(colid)s" )
        """
    else:
        stub += """
            ( "%(colid)s" )
        """
    return stub % {
        'uq':'UNIQUE' if unique else '',
        'indid':indid,
        'tblid':tblid,
        'colid':colid,
        'schemaid':schemaid,
        'index_type':index_type
    }

def add_constraint_check(schemaid, tblid, conid, const_stmt):
    l, o, r = const_stmt
    subStr = {
        'tqn': _get_tqn(schemaid,tblid),
        'conid': conid,
        'const_stmt': '"' + l + '" ' + o + ' %(compval)s',
        'compval':'%(compval)s'
    }
    
    stmt =  \
        """
        ALTER TABLE %(tqn)s
        ADD CONSTRAINT "%(conid)s"
        CHECK (%(const_stmt)s)
        """
    return stmt % subStr
    
def add_constraint_notnull(schemaid, tblid, colid):
    return \
        """
        ALTER TABLE %(tqn)s
        ALTER COLUMN "%(colid)s"
        SET NOT NULL
        """ % {'tqn':_get_tqn(schemaid,tblid),'colid':colid}

def add_constraint_unique(schemaid, tblid, conid, colid):
    return \
        """
        ALTER TABLE %(tqn)s
        ADD CONSTRAINT "%(conid)s"
        UNIQUE("%(colid)s")
        """ % {'tqn':_get_tqn(schemaid,tblid),'conid':conid,'colid':colid}
    
def drop_db(schemaid):
    subStr = {
        'schemaid':schemaid
    }
    
    stmt = """DROP SCHEMA "%(schemaid)s" CASCADE """
    return stmt % subStr
    
def drop_table(schemaid,tblid):
    subStr = {
        'tqn': _get_tqn(schemaid,tblid)
    }
    
    stmt = """DROP TABLE %(tqn)s CASCADE """
    return stmt % subStr

def drop_column(schemaid,tblid,colid):
    return """
        ALTER TABLE %(tqn)s
        DROP COLUMN "%(colid)s"
    """ % {
        'tqn':_get_tqn(schemaid,tblid),
        'colid':colid
    }
    
def drop_constraint(schemaid, tblid, conid):
    return \
        """
        ALTER TABLE %(tqn)s
        DROP CONSTRAINT "%(conid)s"
        """ % {
            'tqn':_get_tqn(schemaid,tblid),
            'conid':conid
        }
        
def drop_constraint_notnull(schemaid, tblid, colid):
    return \
        """
        ALTER TABLE %(tqn)s
        ALTER COLUMN "%(colid)s"
        DROP NOT NULL
        """ % {
            'tqn':_get_tqn(schemaid,tblid),
            'colid':colid
        }
    
###############################################################################
### PERMISSIONS ###############################################################
###############################################################################

def grant_usage(schemaid,uname):
    return """
        GRANT USAGE
        ON SCHEMA "%(schemaid)s"
        TO "%(uname)s"
        
        """ % {'schemaid':schemaid,'uname':uname}
    
def alter_default(schemaid,uname):
    return """                        
            ALTER DEFAULT PRIVILEGES 
            IN SCHEMA "%(schemaid)s"
            GRANT SELECT ON TABLES
            TO "%(uname)s";
        
        """ % {'schemaid':schemaid,'uname':uname}

###############################################################################
### DML #######################################################################
###############################################################################


def insert(schemaid, tblid, values=None, colnames=False):
    subStr = {'tqn': _get_tqn(schemaid,tblid)}
    if colnames:
        subStr['cols'] = '"' + '", "'.join(colnames) + '"'
        stmt = """INSERT INTO %(tqn)s (%(cols)s) """
    else:
        stmt = """INSERT INTO %(tqn)s """
    if values is not None:
        subStr['vals'] = ', '.join(str(x) for x in values)
        stmt += """VALUES (%(vals)s) """
        return stmt % subStr
    elif values is None and colnames:
        stmt = stmt % subStr
        sub = {'vals':','.join(("%("+col+")s" for col in colnames))}
        stmt += """VALUES (%(vals)s) """ % sub
        return stmt
    
def update(schemaid, tblid, values, colnames=False):
    return insert(schemaid, tblid, values, colnames=False)
    
###############################################################################
### DQL #######################################################################
###############################################################################   

def process_where(schemaid,tblid,clause,i=None):
    whereAdd = _get_tqn(schemaid,tblid) +'."'+ clause[0] + '" ' 
    if i is None:
        whereAdd += ' ' + clause[1] + ' %(whereVal)s '
    else:
        whereAdd += ' ' + clause[1] + ' %(whereVal_'+str(i)+')s '
    return whereAdd
    
def select(schemaid, tblid, 
           cols=None, where=None, join=None, group_by=None, order_by=None, 
           limit=None):
    subStr = {
        'tqn':_get_tqn(schemaid,tblid)
    }
    stmt = None
    params = {}
    if cols is not None:
        subStr['cols'] = ', '.join(_get_tqn(schemaid,tblid)+'."'+str(x)+'"' 
                                   for x in cols)
        stmt = \
                """
                SELECT %(cols)s 
                FROM %(tqn)s
                """
    else:
        stmt = \
                """
                SELECT * 
                FROM %(tqn)s
                """
    if join is not None:
        stmt += """
                JOIN %(jtbl)s
                ON %(on)s
                """
        subStr['jtbl'] = _get_tqn(join[0],join[1])
        subStr['on'] = _get_tqn(schemaid,tblid)+'."'+join[2]+'" '+join[3]
        subStr['on'] += ' ' + _get_tqn(join[0],join[1])+'."'+join[4]+'"'

    if where is not None:
        stmt += "\nWHERE "
        subStr['where'] = ''
        if isinstance(where[0],tuple) or isinstance(where[0],list):
            for i,clause in enumerate(where):
                if i > 0:
                    subStr['where'] += ' AND '
                params['whereVal_'+str(i)] = clause[2]
                subStr['where'] += process_where(schemaid,tblid,clause,i)
        else:
            subStr['where'] += process_where(schemaid,tblid,where)
            params['whereVal'] = where[2]
        stmt += """ %(where)s """
    
    if group_by is not None:
        subStr['group'] = ','.join(_get_cqn(schemaid,tblid,x)
                                   for x in group_by)
        stmt += """
                GROUP BY %(group)s
                """
    
    if order_by is not None:
        if len(order_by) == 1:
            subStr['order'] = order_by[0]
        else:
            subStr['order'] = ', '.join(_get_cqn(schemaid,tblid,x[0])+' '+x[1]
                                for x in order_by)
        
        stmt += """
                \nORDER BY %(order)s
                """
    
    if limit is not None:
        subStr['limit'] = limit
        stmt += """
                LIMIT %(limit)s
                """
    
    return stmt % subStr,params

###############################################################################
### DQL for POSTGIS ###########################################################
###############################################################################   

def select_geography(schemaid,tblid,colid,colname,bb=None,geotype=None,z=None):
    z = int(z)
    stmt = """
            WITH data AS (
                SELECT *
                FROM "%(schemaid)s"."%(tblid)s"
            )
            SELECT "_adm-rowid" as rowid,
           """
    if z < 16:
        stmt += """
            %(output_func)s(ST_simplify("%(colid)s"::geometry,%(tolerance)s))
           """
    else:
        stmt += """
            %(output_func)s("%(colid)s")
           """
    stmt += """
                as "%(colname)s"
            FROM data
            
        """
    if bb is not None:
        stmt += """WHERE ST_Intersects(%(bb)s, "%(colid)s")"""
    
    output_func = 'ST_AsGeoJSON'
    if geotype is not None:
        if geotype == 'wkb':
            output_func = 'ST_AsBinary'
        elif geotype == 'wkt':
            output_func = 'ST_AsEWKB'
        
    stmt = stmt % {
        'bb':bb,
        'colid':colid,
        'colname':colname,
        'schemaid':schemaid,
        'tblid':tblid,
        'output_func':output_func,
        'tolerance':1/(3**float(z))
    }
    
    return stmt
    
def select_geography_poly(schemaid,tblid,colid,colname,bb=None,geotype=None,z=None):
    z = int(z)
    stmt = """
            WITH data AS (
                SELECT *
                FROM "%(schemaid)s"."%(tblid)s"
            )
            SELECT "_adm-rowid" as rowid,
           """
    if z < 8:
        stmt += """
            %(output_func)s(ST_PointOnSurface("%(colid)s"::geometry))
           """
    elif z < 16:
        stmt += """
            %(output_func)s(ST_Simplify("%(colid)s"::geometry,%(tolerance)s))
           """
    else:
        stmt += """
            %(output_func)s("%(colid)s")
           """
    stmt += """
                as "%(colname)s"
            FROM data
            
        """
    
    if bb is not None:
        stmt += """WHERE ST_Intersects(%(bb)s, "%(colid)s")"""
    
    output_func = 'ST_AsGeoJSON'
    if geotype is not None:
        if geotype == 'wkb':
            output_func = 'ST_AsBinary'
        elif geotype == 'wkt':
            output_func = 'ST_AsEWKB'
        
    stmt = stmt % {
        'bb':bb,
        'colid':colid,
        'colname':colname,
        'schemaid':schemaid,
        'tblid':tblid,
        'output_func':output_func,
        'tolerance':1/(3**float(z))
    }
    
    return stmt
    
def select_features_byrowid(schemaid,tblid,colid,colname,rowids,z=None):
    stmt = """ WITH data AS (
                    SELECT *
                    FROM "%(schemaid)s"."%(tblid)s"
                    WHERE "_adm-rowid" IN %(rowids)s
                )
                SELECT "_adm-rowid" as rowid,
                    %(output_func)s("%(colid)s") as "%(colname)s"
                FROM data
            
        """
    
    output_func = 'ST_AsGeoJSON'
    
    
    # HOLY HELL THIS IS UNGUARDED!
    if len(rowids) == 1:
        rowids = (str(rowids[0]),str(rowids[0]))
    else:
        rowids = tuple(str(x) for x in rowids)
        
    stmt = stmt % {
        'colid':colid,
        'colname':colname,
        'schemaid':schemaid,
        'tblid':tblid,
        'rowids':rowids,
        'output_func':output_func,
        'tolerance':None if z is None else 1/(3**float(z))
    }
    
    return stmt

def select_geography_rowids(schemaid,tblid,colid,bb,z):
    stmt = """
            WITH data AS (
                SELECT *
                FROM "%(schemaid)s"."%(tblid)s"
            )
            SELECT "_adm-rowid" as rowid
            FROM data
            WHERE ST_Intersects(%(bb)s, "%(colid)s")
            """
    
    stmt = stmt % {
        'bb':bb,
        'colid':colid,
        'schemaid':schemaid,
        'tblid':tblid
    }
    
    return stmt


def delete_row(schemaid,tblid,where):
    stmt = """
        DELETE FROM %(qtn)s
        WHERE 
    """
    
    stmt = stmt % {
        'qtn':_get_tqn(schemaid,tblid),
    }
    
    stmt += process_where(schemaid,tblid,where) % {'whereVal':"'"+where[2]+"'"}
    return stmt
    

