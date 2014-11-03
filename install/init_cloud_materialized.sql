-- Nimbodata initialization script for PostgreSQL
-- Copyright (C) 2014  Bradley Alan Smith

-------------------------------------------------------------------------------
------ SETUP CORE -------------------------------------------------------------
-------------------------------------------------------------------------------

CREATE EXTENSION postgis;
CREATE LANGUAGE plpython2u;


DROP SCHEMA "_adm-registries" CASCADE;

CREATE SCHEMA "_adm-registries";

SET search_path TO "_adm-registries";



CREATE TABLE "_adm-entitymethods" (
    entitytype text PRIMARY KEY,
    methods text[]
);

CREATE FUNCTION newrowid ()
    RETURNS text
AS $$
    if 'uuid' in GD:
        uuid = GD['uuid']
    else:
        from uuid import uuid4 as uuid
        GD['uuid'] = uuid
    return 'row-'+str(uuid()).replace('-','')
$$ LANGUAGE plpython2u;

CREATE FUNCTION "to_Integer" (val text)
    RETURNS integer
AS $$
    if len(str(val)) == 0:
        return None
    else:
        try:
            return int(val)
        except:
            return None
$$ LANGUAGE plpython2u;

CREATE FUNCTION "to_Text" (val text)
    RETURNS text
AS $$
    return val
$$ LANGUAGE plpython2u;

CREATE FUNCTION "to_Text" (val float)
    RETURNS text
AS $$
    return str(val)
$$ LANGUAGE plpython2u;

CREATE FUNCTION "to_Text" (val integer)
    RETURNS text
AS $$
    return str(val)
$$ LANGUAGE plpython2u;

CREATE FUNCTION "to_Float" (val text)
    RETURNS float
AS $$
    if len(str(val)) == 0:
        return None
    else:
        try:
            return float(val)
        except:
            return None
$$ LANGUAGE plpython2u;

CREATE FUNCTION "to_TextArray" (val text)
    RETURNS text[]
AS $$
    if len(str(val)) == 0:
        return None
    else:
        retVal = []
        repl = val.replace('[','')
        repl = repl.replace(']','')
        return repl.split(',')
$$ LANGUAGE plpython2u;

CREATE FUNCTION "to_IntegerArray" (val text)
    RETURNS integer[]
AS $$
    if len(str(val)) == 0:
        return None
    else:
        retVal = []
        repl = val.replace('{','') # SRSLYWTF, it swapped my brackets in text
        repl = repl.replace('}','') # SRSLYWTF, it swapped my brackets in text
        for item in repl.split(','):
            try:
                retVal.append(int(item))
            except (ValueError,TypeError):
                retVal.append(None)
        return retVal
$$ LANGUAGE plpython2u;

CREATE FUNCTION "to_FloatArray" (val text)
    RETURNS float[]
AS $$
    if len(str(val)) == 0:
        return None
    else:
        retVal = []
        repl = val.replace('{','') # SRSLYWTF, it swapped my brackets in text
        repl = repl.replace('}','') # SRSLYWTF, it swapped my brackets in text
        for item in repl.split(','):
            try:
                retVal.append(float(item))
            except (ValueError,TypeError):
                retVal.append(None)
        return retVal
$$ LANGUAGE plpython2u;


CREATE TABLE "_adm-entityregistry" (
    name text,
    owner text,
    objid text,
    parent_objid text,
    entitytype text REFERENCES "_adm-entitymethods"(entitytype),
    datatype text,
    datadetail text,
    weight integer,
    alias text,
    cols text[],
    dobj jsonb,
    creationtime timestamp with time zone DEFAULT clock_timestamp()
);

CREATE INDEX ON "_adm-entityregistry"(name);
CREATE INDEX ON "_adm-entityregistry"(objid);
CREATE INDEX ON "_adm-entityregistry"(parent_objid);
CREATE INDEX ON "_adm-entityregistry"(entitytype);
CREATE INDEX ON "_adm-entityregistry"(creationtime);
CREATE INDEX ON "_adm-entityregistry"(weight);

CREATE TABLE "_adm-userregistry" (
    usrname text PRIMARY KEY,
    usrid text unique,
    usrcreationtime timestamp with time zone DEFAULT clock_timestamp()
);

CREATE TABLE "_adm-viewcolumns" (
    viewid text not null,
    colid text not null,
    datatype text not null,
    weight int,
    transform jsonb,
    creationtime timestamp with time zone DEFAULT clock_timestamp()
);

CREATE INDEX ON "_adm-viewcolumns"(weight);
CREATE INDEX ON "_adm-viewcolumns"(viewid);
CREATE INDEX ON "_adm-viewcolumns"(colid);
CREATE INDEX ON "_adm-viewcolumns"(creationtime);

--Provides a view for immediate access to the most recent entry for entities
CREATE MATERIALIZED VIEW "_adm-entityinfo" AS
WITH max_insert AS (
    SELECT objid as maxobjid, MAX(creationtime) as maxtime
    FROM "_adm-entityregistry"
    GROUP BY objid
)
SELECT "_adm-entityregistry"."name",
    "_adm-entityregistry"."owner",
    "_adm-entityregistry"."objid",
    "_adm-entityregistry"."parent_objid",
    "_adm-entityregistry"."entitytype",
    "_adm-entityregistry"."datatype",
    "_adm-entityregistry"."weight",
    "_adm-entityregistry"."alias",
    "_adm-entityregistry"."cols",
    "_adm-entityregistry"."dobj",
    "_adm-entitymethods"."methods"    
FROM "_adm-entityregistry"
INNER JOIN max_insert
    ON "_adm-entityregistry"."creationtime" = max_insert.maxtime
      AND "_adm-entityregistry"."objid" = max_insert.maxobjid
INNER JOIN "_adm-entitymethods"
    ON "_adm-entitymethods"."entitytype" = "_adm-entityregistry"."entitytype";

CREATE INDEX ON "_adm-entityinfo"(name);
CREATE INDEX ON "_adm-entityinfo"(objid);
CREATE INDEX ON "_adm-entityinfo"(parent_objid);
CREATE INDEX ON "_adm-entityinfo"(entitytype);
CREATE INDEX ON "_adm-entityinfo"(weight);

CREATE OR REPLACE FUNCTION "_adm-trig_refresh_entinfo"() RETURNS trigger AS
$$
BEGIN
    REFRESH MATERIALIZED VIEW "_adm-registries"."_adm-entityinfo";
    RETURN NULL;
END;
$$
LANGUAGE plpgsql ;

CREATE TRIGGER "_adm-triggo_refresh_entinfo" AFTER TRUNCATE OR INSERT OR UPDATE OR DELETE
   ON "_adm-entityregistry" FOR EACH STATEMENT
   EXECUTE PROCEDURE "_adm-trig_refresh_entinfo"();
   
CREATE TRIGGER "_adm-triggo_refresh_entinfo2" AFTER TRUNCATE OR INSERT OR UPDATE OR DELETE
   ON "_adm-viewcolumns" FOR EACH STATEMENT
   EXECUTE PROCEDURE "_adm-trig_refresh_entinfo"();

--Provides a view for immediate access to the current max colindex for a table
CREATE VIEW "_adm-maxcolindex" AS
SELECT parent_objid as parent_objid, max(weight) as maxindex
FROM "_adm-entityinfo"
WHERE "entitytype" = 'Column'
GROUP BY parent_objid;

--Provides a view of column info taking into account multiple associations
CREATE MATERIALIZED VIEW "_adm-viewcolinfo" AS
WITH max_insert AS (
    SELECT viewid as maxviewid, colid as maxcolid, MAX(creationtime) as maxtime
    FROM "_adm-viewcolumns"
    GROUP BY viewid, colid
)
SELECT viewcols.viewid, entityinfo.parent_objid, entityinfo.entitytype,
    viewcols.weight, entityinfo.name, viewcols.datatype, entityinfo.owner, 
    viewcols.colid objid, entityinfo.alias
FROM "_adm-viewcolumns" as viewcols
INNER JOIN max_insert
    on viewcols.creationtime = max_insert.maxtime
        AND viewcols.colid = max_insert.maxcolid
INNER JOIN "_adm-entityinfo" as entityinfo
    on viewcols.colid = entityinfo.objid;
    
CREATE INDEX ON "_adm-viewcolinfo"(weight);
CREATE INDEX ON "_adm-viewcolinfo"(objid);
CREATE INDEX ON "_adm-viewcolinfo"(viewid);
CREATE INDEX ON "_adm-viewcolinfo"(parent_objid);
CREATE INDEX ON "_adm-viewcolinfo"(entitytype);
CREATE INDEX ON "_adm-viewcolinfo"(name);
CREATE INDEX ON "_adm-viewcolinfo"(datatype);
    
CREATE OR REPLACE FUNCTION "_adm-trig_refresh_viewcolinfo"() RETURNS trigger AS
$$
BEGIN
    REFRESH MATERIALIZED VIEW "_adm-registries"."_adm-viewcolinfo";
    RETURN NULL;
END;
$$
LANGUAGE plpgsql ;

CREATE TRIGGER "_adm-triggo_viewcolinfo" AFTER TRUNCATE OR INSERT OR UPDATE OR DELETE
   ON "_adm-entityregistry" FOR EACH STATEMENT
   EXECUTE PROCEDURE "_adm-trig_refresh_viewcolinfo"();
   
CREATE TRIGGER "_adm-triggo_viewcolinfo2" AFTER TRUNCATE OR INSERT OR UPDATE OR DELETE
   ON "_adm-viewcolumns" FOR EACH STATEMENT
   EXECUTE PROCEDURE "_adm-trig_refresh_viewcolinfo"();

-------------------------------------------------------------------------------
------ USERS ------------------------------------------------------------------
-------------------------------------------------------------------------------

DROP OWNED BY dml_agent;
DROP USER dml_agent;


CREATE USER dml_agent;

REVOKE CONNECT ON DATABASE cloud_admin FROM dml_agent;

GRANT CONNECT ON DATABASE cloud_admin TO dml_agent;

/* DQL User - needs to select in registries and any schema created */

DROP OWNED BY dql_agent;
DROP USER dql_agent;
CREATE USER dql_agent;

REVOKE CONNECT ON DATABASE cloud_admin FROM dql_agent;
GRANT CONNECT ON DATABASE cloud_admin TO dql_agent;

GRANT USAGE
ON SCHEMA "_adm-registries"
TO dql_agent;

GRANT SELECT
ON ALL TABLES IN SCHEMA "_adm-registries"
TO dql_agent;

ALTER DEFAULT PRIVILEGES 
IN SCHEMA "_adm-registries"
GRANT SELECT ON TABLES
TO dql_agent;

/* DDL User - needs to create only on schema after they are created */

DROP OWNED BY ddl_agent;
DROP USER ddl_agent;
CREATE USER ddl_agent;

REVOKE CONNECT ON DATABASE cloud_admin FROM ddl_agent;
GRANT CONNECT ON DATABASE cloud_admin TO ddl_agent;

GRANT USAGE
ON SCHEMA "_adm-registries"
TO ddl_agent;


/* This stuff below is just dev crap. */


INSERT INTO "_adm-userregistry" VALUES (
    'TestUser',
    'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'
);

INSERT INTO "_adm-userregistry" VALUES (
    'b',
    'usr-c40884a6-fc9c-4ba3-be97-ad72f770f8a9'
);

