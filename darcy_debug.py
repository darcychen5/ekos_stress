import os,sys,time,json
sys.path.insert(0, '/root/ekos_stress')
from log import *
import ekosUtils
my_utils = ekosUtils.Utils()
#ip = sys.argv[1]
logname = "/var/log/darcy.txt"
#tenant_list = my_utils.get_all_tenant_name(ip)
f = open(logname,'r')
try:
	f.seek(-7,2)
	line = f.read(2)
except:
	error('file %s is empty' % logname)
	sys.exit()
print line
if line == 'ok':
	print 'pass'
else:
	print 'failed'