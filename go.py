"""Demo sanitizer.  Quick and dirty - if ten minutes """

import json
import datetime, time
import subprocess


while True:
    lastdata = open('./core/lastaccess','r').read()
    try:
        lastaccess = datetime.datetime(*json.loads(lastdata))
    except ValueError:
        print 'waiting for 5 minutes'
        time.sleep(60*5)
        continue
    
    if datetime.datetime.now() - lastaccess > datetime.timedelta(minutes=10):
        p = subprocess.Popen(['python','init_db.py'],cwd='./install/')
        p.wait()
        p = subprocess.Popen(['python','load.py'],cwd='./examples/baseball/')
        p.wait()
        p = subprocess.Popen(['python','load.py'],cwd='./examples/rivers/')
        p.wait()
        p = subprocess.Popen(['python','load.py'],cwd='./examples/places/')
        p.wait()
        open('./core/lastaccess','w').write('clean')
    else:
        print 'No need.'
        
    print 'waiting for 5 minutes'
    time.sleep(60*5)
    
