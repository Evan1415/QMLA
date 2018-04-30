import RedisSettings as rds
import argparse
import redis 

parser = argparse.ArgumentParser(description='Redis settings.')

parser.add_argument(
  '-rh', '--redis_host_name', 
  help="Redis host.",
  type=str,
  default='localhost'
)

parser.add_argument(
  '-rpn', '--redis_port_number', 
  help="Redis port number.",
  type=int,
  default=6379
)

parser.add_argument(
  '-rqid', '--redis_qmd_id', 
  help="QMD ID.",
  type=str,
  default=0
)

arguments = parser.parse_args()

host_name = arguments.redis_host_name
port_number = arguments.redis_port_number
qid = arguments.redis_qmd_id

try:
    redis_conn = redis.Redis(host=host_name, port=port_number)
    print("redis-ready")
except redis.ConnectionError:
    print("redis-not-ready")        
    

