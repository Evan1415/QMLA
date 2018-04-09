from __future__ import print_function # so print doesn't show brackets
import redis
import os, sys
import pickle
#TODO do as list?
#TODO do in function and return unique set of dbs.. or else set list of port ids in QMD, cycle through them so several QMDs can be run simultaneously. 


"""
try:
	host_name = os.getenv("QMD_REDIS_HOST")
except:
	print("Couldn't find environment variable for Redis server name.")
	host_name= 'localhost'


if host_name is None:
    host_name= 'localhost'
#    host_name = 'redis://localhost:6379/1'



print("Using host name ", host_name)
port_number = 6379
"""



print("Redis settings")

read_env = True


print("in redis settings, parent pid:", os.getppid())

try:
    try:
        env_vars = pickle.load(open('/home/bf16951/Dropbox/QML_share_stateofart/QMD/ExperimentalSimulations/environment_variables.p', 'rb')) # TODO don't use absolute path of my laptop!
    except:
	    env_vars = pickle.load(open('/panfs/panasas01/phys/bf16951/QMD/ExperimentalSimulations/environment_variables.p', 'rb')) ## For blue crystal


except:
    print("Failed; directory:", os.getcwd())
    print("Paths:")
    for p in sys.path:
        print(p)
    read_env = False


#sys.path.append(os.path.join("..", "Libraries","QML_lib"))



if read_env:
    print("Reading from environment_variables pickled object.")
    test_workers = env_vars['use_rq']
    host_name = env_vars['host']
    port_number = env_vars['port']
else:
    test_workers = False
    host_name = 'localhost'
    port_number = 6379

print("test workers:", test_workers)
print("host name", host_name)
print("port number", port_number)


qmd_info_db = redis.StrictRedis(host=host_name, port=port_number, db=0)
learned_models_info = redis.StrictRedis(host=host_name, port=port_number, db=1)
learned_models_ids = redis.StrictRedis(host=host_name, port=port_number, db=2)
bayes_factors_db = redis.StrictRedis(host=host_name, port=port_number, db=3) 
bayes_factors_winners_db = redis.StrictRedis(host=host_name, port=port_number, db=4)
active_branches_learning_models = redis.StrictRedis(host=host_name, port=port_number, db=5)
active_branches_bayes = redis.StrictRedis(host=host_name, port=port_number, db=6)
active_interbranch_bayes =  redis.StrictRedis(host=host_name, port=port_number, db=7)





try:
    import pickle
    pickle.HIGHEST_PROTOCOL=2
    from rq import Connection, Queue, Worker

    redis_conn = redis.Redis(host=host_name, port=port_number)
    q = Queue(connection=redis_conn, async=test_workers, default_timeout=3600) # TODO is this timeout sufficient for ALL QMD jobs?
    parallel_enabled = True
except:
    parallel_enabled = False    



def flushdatabases():
    try:
        qmd_info_db.flushdb()
        learned_models_info.flushdb()
        learned_models_ids.flushdb()
        bayes_factors_db.flushdb()
        bayes_factors_winners_db.flushdb()
        active_branches_learning_models.flushdb()
        active_branches_bayes.flushdb()
        active_interbranch_bayes.flushdb()
    except:
        print("Databases don't exist on Redis yet.")
    
def countWorkers():
    # TODO this isn't working
    return Worker.count(connection=redis_conn)
    
    
def hello():
    print("Hello")    
