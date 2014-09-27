import sys

sys.path.append('../../')

from client import pyclient

sys.path.append('../../test/')
import config_cloud as cfg

cloud = pyclient.connect('http://localhost:5000',cfg.user)
db = cloud.Database('Baseball')
master = db.Table('Master')
m_cols = dict((x['name'],x) for x in master.Columns())
m_plyr = m_cols['playerid']
first,last = m_cols['namefirst'],m_cols['namelast']

def batting_stats():
    bat = db.Table('Batting')
    b_cols = dict((x['name'],x) for x in bat.Columns())
    b_plyr, b_year = bat.Columns()[0:2]
    r,h,hr = b_cols['r'],b_cols['h'],b_cols['hr'],
    
    try:
        db.View('SixtiesRuns').drop()
        db.View('Homers').drop()
    except Exception:
        pass
    
    # The best single-season batters of the 1960s by runs, ties broken by hits.
    sixties = db.create_view('SixtiesRuns',{
        'viewid':bat,
        'cols':[first,last,'yearid','g','g_batting','r','h'],
        'where':((b_year < 1970) & (b_year > 1959)),
        'join':(master,('playerid','=',m_plyr)),
        'order_by':[(r,'desc'),(h,'desc')]
    })
    
    # All-time single-season home runs.
    homers = db.create_view('Homers',{
        'viewid':bat,
        'cols':[first,last,'yearid','g_batting','hr','r','h'],
        'order_by':[(hr,'desc'),(r,'desc'),(h,'desc')],
        'where':hr > 0,
        'join':(master,('playerid','=',m_plyr)),
        'order_by':[(hr,'desc')]
    })
    
    
if __name__ == '__main__':
    batting_stats()
