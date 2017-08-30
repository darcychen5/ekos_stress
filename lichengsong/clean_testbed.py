import json,time,sys,yaml
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()
ip = sys.argv[1]

'''
rtn = my_utils.get_all_app(ip)
print rtn
'''
rtn = my_utils.delete_all_app(ip)
