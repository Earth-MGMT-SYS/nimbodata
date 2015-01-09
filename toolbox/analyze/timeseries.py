import datetime

from common.datatypes import Text,Point,Date,Float
from common.expressions import extract,MIN,MAX,AVG,SUM,count,unique,Join,Union,\
    AS, now, generate_series, LeftOuterJoin

def indexall(rel):
    for col in rel.columns():
        rel.add_index(col)
    try:
        rel.add_index('_adm-rowid')
    except ValueError:
        pass

def make_site_timeseries_views(parent,name,site_table,data_table,
        daily_stats = None, compareTo = None, begin_month = 10):
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
    
    today = datetime.date.today()
    this_year = today.year
    if today.month >= begin_month:
        begin = this_year, begin_month, 1
        end = this_year + 1, begin_month, 1
    else:
        begin = this_year - 1, begin_month, 1
        end = this_year, begin_month, 1
        
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
    
    annual_stats = root.create_view('AnnualStats', {
        'objid':site_table,
        'cols':[
            '_adm-rowid',siteid,
            extract(obd,'water_year'),
            MIN(value),AVG(value),MAX(value)
        ],
        'join':Join(data_table),
        'group_by':[
            '_adm-rowid','siteid',
            extract(obd,'water_year'),
        ],
        'order_by':[extract(obd,'water_year')]
    }, materialized = True)

    indexall(annual_stats)
        
    alldata = root.create_view('AllData',{
        'objid':site_table,
        'join':Join(data_table)
    })
    
    cycols = alldata.columns()
    currentday = root.create_view('CurrentDay',{
        'objid':alldata,
        'cols':['_adm-rowid']+cycols[:-4]+[MAX(cycols[-2]),cycols[-1]],
        'group_by':['_adm-rowid']+cycols[:-4]+cycols[-1:]
    })
    
    s_siteid, mo, day, mi, av, ma = daily_stats.columns()
    currentstatdata = root.create_view('CurrentStatsData',{
        'objid':alldata,
        'join':Join(daily_stats,{'all':[
                (d_siteid == s_siteid),
                (extract(obd,'month') == mo),
                (extract(obd,'day') == day),
            ]}
        )
    }, materialized = True)
    #})

    indexall(currentstatdata)
    
    currentsites = root.create_view('CurrentSites',{
        'objid':currentday,
        'cols':[unique(siteid)]
    #},materialized=True)
    })
    
    #indexall(currentsites)
    
    site_view = root.create_view('CurrentSiteInfo',{
        'objid':site_table,
        'cols':['_adm-rowid']+site_table.columns(),
        'join':(currentsites,('siteid','=','unique(siteid)'))
    },materialized=True)

    indexall(site_view)
    
    sitepor = root.create_view('SitePOR',{
        'objid':alldata,
        'cols':['_adm-rowid',MIN(obd),MAX(obd),count(obd),site_cols['geom']],
        'group_by':['_adm-rowid',site_cols['geom']]
    },materialized=True)
    
    indexall(sitepor)
    
    valueaverage = root.create_view('ValueAverageCurrent',{
        'objid':alldata,
        'cols':['_adm-rowid']+[siteid,AVG(value)],
        'group_by':['_adm-rowid']+[siteid],
        'order_by':[siteid]
    #},materialized=True)
    })
    
    valuetoday = root.create_view('ValueAverageToday',{
        'objid':site_table,
        'cols':['_adm-rowid']+[siteid,value],
        'join':Join(currentday),
        'order_by':[siteid]
    #},materialized=True)
    })

    #indexall(valueaverage)
    dontcare, current_avg = valuetoday.columns()
        
    valueavghist = root.create_view('StatsHistorical',{
        'objid':site_table,
        'cols':['_adm-rowid']+[
            siteid,
            MIN(mi),
            AVG(av),
            MAX(ma),
        ],
        'join':Join(daily_stats),
        'group_by':['_adm-rowid',siteid],
        'order_by':[siteid]
    },materialized=True)
    
    indexall(valueavghist)
    dontcare, hist_min, hist_avg, hist_max = valueavghist.columns()
    
    curdvstats = root.create_view('CurrentDayVsStats',{
        'objid':valueavghist,
        'cols':['_adm-rowid']+[current_avg,hist_min,hist_avg,hist_max],
        'join':(valuetoday,('siteid','=','siteid')) # Too many same name cols.
    #},materialized=True)
    })
    #indexall(compositedaily)
    
    try:
        parent.View(name).drop()
    except:
        pass
    layer = parent.create_view(name,{
        'objid':curdvstats,
        'cols':['_adm-rowid'] + site_view.columns()[:-1] + [
            current_avg / hist_avg, 'geom'
        ],
        'join':Join(site_view,('_adm-rowid','=','_adm-rowid'))
    },materialized=True)
    #})

    layer.columns()[-2].modify({'name':'magnitude'})
    indexall(layer)
    
    cydates = root.create_view('CYDates',{
        'objid':generate_series(Date(*begin),Date(*end))
    })
    
    snum, mo, da, miv, avv, mav = daily_stats.columns()
    datatab = layer.create_view('CurrentYear',{
        'objid':site_view,
        'cols':['_adm-rowid']+[obd,value,miv,avv,mav],
        'where':[obd >= Date(*begin)],
        'join':[
            LeftOuterJoin(cydates),
            Join(currentstatdata,[
                ('_adm-rowid','=','_adm-rowid'),
                ('date','=','date')
            ])
        ],
        'order_by':[siteid,obd]
    #},materialized=True)
    })
    
    datatab = layer.create_view('LastYear',{
        'objid':site_view,
        'cols':['_adm-rowid']+[obd,value,miv,avv,mav],
        'where':[obd >= Date(*[begin[0]-1]+list(begin[1:])), obd < Date(*begin)],
        'join':Join(currentstatdata,('_adm-rowid','=','_adm-rowid')),
        'order_by':[siteid,obd]
    #},materialized=True)
    })
    
    #indexall(datatab)
    
    layer.create_view('POR',{'objid':sitepor})
    
    return layer
