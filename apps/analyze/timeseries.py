from common.datatypes import Text,Point,Date,Float
from common.expressions import extract,MIN,MAX,AVG,count,unique,Join,Union, AS

def indexall(rel):
    for col in rel.columns():
        rel.add_index(col)
    try:
        rel.add_index('_adm-rowid')
    except ValueError:
        pass

def make_site_timeseries_views(parent,name,site_table,data_table,
        daily_stats = None, compareTo = None):
    try:
        root = parent.create_view(name+'_internal',{'objid':site_table})
    except:
        parent.View(name+'_internal').drop()
        root = parent.create_view(name+'_internal',{'objid':site_table})
    
    site_cols = dict((x['name'],x) for x in site_table.columns())
    data_cols = dict((x['name'],x) for x in data_table.columns())
    obd, value = data_cols['date'], data_cols['value']
    siteid = site_cols['siteid']
    d_siteid = data_cols['siteid']
    
    if daily_stats is None:
        # Aggregate the min, avg and max for each day of the year
        daily_stats = root.create_view('DailyStats', {
            'objid':site_table,
            'cols':[
                '_adm-rowid',siteid,
                extract(obd,'month'),
                extract(obd,'day'),
                MIN(value),AVG(value),MAX(value)
            ],
            'join':Join(data_table),
            'group_by':[
                '_adm-rowid','siteid',
                extract(data_cols['date'],'month'),
                extract(data_cols['date'],'day')
            ]
        }, materialized = True)

        indexall(daily_stats)
    else:
        daily_stats = root.create_view('DailyStats', {
            'objid':daily_stats
        })
    
    currentdata = root.create_view('CurrentData',{
        'objid':site_table,
        'where':[obd >= Date(2013,10,1),obd < Date(2014,10,1)],
        'join':Join(data_table),
    })
    
    s_siteid, mo, day, mi, av, ma = daily_stats.columns()
    currentstatdata = root.create_view('CurrentStatsData',{
        'objid':currentdata,
        'join':Join(daily_stats,{'all':[
                (d_siteid == s_siteid),
                (extract(obd,'month') == mo),
                (extract(obd,'day') == day),
            ]}
        )
    }, materialized = True)
    indexall(currentstatdata)
    
    currentsites = root.create_view('CurrentSites',{
        'objid':currentdata,
        'cols':[unique(d_siteid)]
    },materialized=True)

    indexall(currentsites)    
    
    site_view = root.create_view('CurrentSiteInfo',{
        'objid':site_table,
        'cols':['_adm-rowid']+site_table.columns(),
        'join':(currentsites,('siteid','=','unique(siteid)'))
    },materialized=True)

    indexall(site_view)
    
    sitepor = root.create_view('SitePOR',{
        'objid':site_table,
        'cols':['_adm-rowid',MIN(obd),MAX(obd),count(obd),site_cols['geom']],
        'join':Join(data_table),
        'group_by':['_adm-rowid',site_cols['geom']]
    },materialized=True)

    indexall(sitepor)
    
    valueaverage = root.create_view('ValueAverageCurrent',{
        'objid':site_table,
        'cols':['_adm-rowid']+[siteid,AVG(value)],
        'where':[obd >= Date(2013,10,1),obd < Date(2014,10,1)],
        'join':Join(data_table),
        'group_by':['_adm-rowid']+[siteid],
        'order_by':[siteid]
    },materialized=True)

    indexall(valueaverage)
    dontcare, current_avg = valueaverage.columns()
    
    if compareTo is None:
        compareTo = -2
        agg = AVG
    elif compareTo.lower() == 'avg' or compareTo.lower() == 'average':
        compareTo = -2
        agg = AVG
    elif compareTo.lower() == 'max' or compareTo.lower() == 'maximum':
        compareTo = -1
        agg = MAX
    
    valueavghist = root.create_view('ValueAverageHistorical',{
        'objid':site_table,
        'cols':['_adm-rowid']+[siteid,agg(daily_stats.columns()[compareTo])],
        'join':Join(daily_stats),
        'group_by':['_adm-rowid',siteid],
        'order_by':[siteid]
    },materialized=True)
    
    indexall(valueavghist)
    dontcare, hist_avg = valueavghist.columns()
    
    compositedaily = root.create_view('CompositeDaily',{
        'objid':valueavghist,
        'cols':['_adm-rowid']+[current_avg,hist_avg],
        'join':(valueaverage,('siteid','=','siteid')) # Too many same name cols.
    },materialized=True)
    indexall(compositedaily)
    
    try:
        parent.View(name).drop()
    except:
        pass
    layer = parent.create_view(name,{
        'objid':compositedaily,
        'cols':['_adm-rowid'] + site_view.columns()[:-1] + [
            current_avg / hist_avg, 'geom'
        ],
        'join':Join(site_view,('_adm-rowid','=','_adm-rowid'))
    },materialized=True)

    layer.columns()[-2].modify({'name':'magnitude'})
    indexall(layer)
    
    snum, mo, da, miv, avv, mav = daily_stats.columns()
    datatab = layer.create_view('CurrentDaily',{
        'objid':site_view,
        'cols':['_adm-rowid']+[obd,value,miv,avv,mav],
        'join':Join(currentstatdata,('_adm-rowid','=','_adm-rowid')),
        'order_by':[siteid]
    },materialized=True)
    
    indexall(datatab)
    
    layer.create_view('POR',{'objid':sitepor})
    layer.create_view('CompositeData',{'objid':compositedaily})
    layer.create_view('CurrentMagnitude',{'objid':currentstatdata})
    
    return layer
