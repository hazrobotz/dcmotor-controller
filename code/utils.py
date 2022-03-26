import timeit
from cloudant.client import CouchDB
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
    dbclient = CouchDB(db_name, db_pass, url=db_uri, connect=True)

    if 'tasks' in dbclient.keys(remote=True):
        db = dbclient['tasks']
    else:
        db = dbclient.create_database('tasks')

    if task not in db.keys(remote=True):
        my_document = db.create_document(data1)
        my_document.save()
        my_document = db.create_document(data2)
        my_document.save()
    else:
        raise ValueError("Task already initialized")

def gettaskmds():
    task = os.getenv('TASK', "widget1")
    #connect to the service, access the task database
    dbclient = CouchDB(db_name, db_pass, url=db_uri, connect=True)

    if 'tasks' not in dbclient.keys(remote=True):
        inittaskmds()
        #raise ValueError("No metadata for tasks")
    db = dbclient['tasks']

    if task in db.keys(remote=True):
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

    if 'jobs' in dbclient.keys(remote=True):
        db = dbclient['jobs']
    else:
        db = dbclient.create_database('jobs')
    
    if job_name not in db.keys(remote=True):
        my_document = db.create_document(data)
        my_document.save()
    else:
        raise ValueError("Job already initialized")

def finishjobmds():
    #connect to the service, access the job database
    dbclient = CouchDB(db_name, db_pass, url=db_uri, connect=True)

    if 'jobs' in dbclient.keys(remote=True):
        db = dbclient['jobs']
    else:
        raise("Jobs DB does not exist")

    if job_name in db:
        db[job_name]['completion_date']=timeit.time.time()
        db[job_name]['output_file']=job_name+".log"
        db[job_name].save()
    else:
        raise ValueError("Job %s does not exist"%job_name)
