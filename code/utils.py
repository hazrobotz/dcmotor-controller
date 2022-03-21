import timeit
from cloudant.client import CouchDB
import os
import timeit

job_name = os.getenv('HOSTNAME')
db_name = os.getenv('DB_NAME')
db_pass = os.getenv('DB_PASS')
db_uri = os.getenv('MDS_URI')

def inittaskmds():
    task="widget1"
    data = {
        '_id': task, 
        'data': {
            'xkernel': "cos",
            'xamplitude': 3,
            'xfrequency': .02
        },
        'creation_date': timeit.default_timer()
    }

    #connect to the service, access the task database
    dbclient = CouchDB(db_name, db_pass, url=db_uri, connect=True)
    dbclient['tasks']

    if 'tasks' in dbclient:
        db = dbclient['tasks']
    else:
        db = dbclient.create_database('tasks')

    if task not in db:
        my_document = db.create_document(data)
        my_document.save()
    else:
        raise ValueError("Task already initialized")

def gettaskmds():
    task = os.getenv('TASK', "widget1")
    #connect to the service, access the task database
    dbclient = CouchDB(db_name, db_pass, url=db_uri, connect=True)
    dbclient['tasks']
    if 'tasks' in dbclient:
        db = dbclient['tasks']
    else:
        raise ValueError("No metadata for tasks")

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
    dbclient = CouchDB(db_name, db_pass, url=db_uri, connect=True)
    dbclient['jobs']

    if 'jobs' in dbclient:
        db = dbclient['jobs']
    else:
        db = dbclient.create_database('jobs')
    
    if job_name not in db:
        my_document = db.create_document(data)
        my_document.save()
    else:
        raise ValueError("Job already initialized")

def finishjobmds():
    #connect to the service, access the job database
    dbclient = CouchDB(db_name, db_pass, url=db_uri, connect=True)
    dbclient['jobs']
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
