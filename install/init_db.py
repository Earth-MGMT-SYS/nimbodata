import subprocess
from pprint import pprint

command = r"""
psql -U cloud_admin cloud_admin -t -c "select 'drop schema \"' || schema_name || '\" cascade;' from information_schema.schemata where schema_name like 'dbi-%'" | psql -U cloud_admin cloud_admin
"""

subprocess.call(command, shell=True)

command = 'psql -U cloud_admin -d cloud_admin -f init_cloud.sql'

subprocess.call(command, shell=True)

import psycopg2
import nimbodata.cloud as cc

cloud = cc.Cloud('bozo')

def walk(api):
    retVal = []
    for name,details in api.items():
        retVal.append([name,[x for x in details.keys() if x != 'create']])
    return retVal

rows = walk(cloud.api.api)

conn = psycopg2.connect('dbname=cloud_admin user=cloud_admin')
with conn.cursor() as cur:
    for row in rows:
        cur.execute("""INSERT INTO "_adm-registries"."_adm-entitymethods" VALUES (%s,%s)""",row)
    conn.commit()
    
    cur.execute("""SELECT * FROM "_adm-registries"."_adm-entitymethods" """)
    #pprint([x for x in cur])
conn.close()
