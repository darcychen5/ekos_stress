import os,sys,time,json
sys.path.insert(0, '/root/ekos_stress')
from log import *
import ekosUtils
my_utils = ekosUtils.Utils()
ip = sys.argv[1]

rtn = my_utils.delete_image(ip,'stress_centos-1')
print rtn
