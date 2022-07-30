import timeit
import couchdb
import os
import timeit

job_name = os.getenv('HOSTNAME')
db_name = os.getenv('DB_NAME')
db_pass = os.getenv('DB_PASS')
db_uri = os.getenv('MDS_URI')

def inittaskmds():
    data1 = {
        '_id': "widget1", 
        'data': {
            'xkernel': "cos",
            'xamplitude': 3,
            'xperiod': 200
        },
        'creation_date': timeit.time.time()
    }
    data2 = {
        '_id': "widget2", 
        'data': {
            'xkernel': "sin",
            'xamplitude': 3,
            'xperiod': 200
        },
        'creation_date': timeit.time.time()
    }

    #connect to the service, access the task database
    dbclient = couchdb.Server("http://%s:%s@%s"%(db_name,db_pass,db_uri))

    if 'tasks' in dbclient:
        db = dbclient['tasks']
    else:
        db = dbclient.create('tasks')

    db.save(data1)
    db.save(data2)

def gettaskmds():
    task = os.getenv('TASK', "widget1")
    #connect to the service, access the task database
    dbclient = couchdb.Server("http://%s:%s@%s"%(db_name,db_pass,db_uri))

    if 'tasks' not in dbclient:
        inittaskmds()
        #raise ValueError("No metadata for tasks")
    db = dbclient['tasks']

    if task in db:
        return db[task]["data"]
    else:
        raise ValueError("Task does not exist in the MDS")

def initjobmds(kernel, amplitude, frequency):
    data = {
        '_id': job_name, 
        'widget': {
            'xkernel': kernel,
            'xamplitude': amplitude,
            'xfrequency': frequency
        },
        'start_date': timeit.time.time()
        }
    #connect to the service, access the job database
    dbclient = couchdb.Server("http://%s:%s@%s"%(db_name,db_pass,db_uri))

    if 'jobs' in dbclient:
        db = dbclient['jobs']
    else:
        db = dbclient.create('jobs')
    
    if job_name not in db.:
        db.save(data)
    else:
        raise ValueError("Job already initialized")

def finishjobmds():
    #connect to the service, access the job database
    dbclient = couchdb.Server("http://%s:%s@%s"%(db_name,db_pass,db_uri))

    if 'jobs' in dbclient:
        db = dbclient['jobs']
    else:
        raise("Jobs DB does not exist")

    if job_name in db:
        db[job_name]['completion_date']=timeit.time.time()
        db[job_name]['output_file']=job_name+".log"
        db[job_name].save()
    else:
        raise ValueError("Job %s does not exist"%job_name)


    if 'data' in dbclient:
        db = dbclient['data']
    else:
        db = dbclient.create('data')
    db[job_name+".log"]={}
    db.put_attachment(db[job_name+".log"], open("somelogs.log"), job_name+".log")