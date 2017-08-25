import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()
app_num = 200
appname_tmp = "stress-bootstorm-"
ip = sys.argv[1]

#get app name
print "begining check_app_status"
app_list = []
for i in range(app_num):
	appname = appname_tmp + str(i)
	app_list.append(appname)

#check app running
rtn = my_utils.check_app_status(ip,app_list)
if rtn != True:
	print error
info('ok')	 
