import os,sys,time,json
sys.path.insert(0, '/root/ekos_stress')
from log import *
import ekosUtils
my_utils = ekosUtils.Utils()
ip = sys.argv[1]
lb_name = "lb-tt"

rtn = my_utils.delete_all_tenant(ip)
print rtn


