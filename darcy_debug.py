import os,sys,time,json
sys.path.insert(0, '/root/ekos_stress')
from log import *
import ekosUtils
my_utils = ekosUtils.Utils()
ip = sys.argv[1]

lb = "demo-springlcoud"
my_utils.create_lb(ip,lb)
rtn = my_utils.add_http_rule_for_all_service(ip,lb)
print rtn
