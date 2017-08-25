import sys,json,time,random
sys.path.insert(0, '/root/ekos_auto/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

appname_tmp = "stress-bootstorm-lb-"
app_num = 3

#create 3 app
ip = sys.argv[1]
cookies = my_utils._get_cookie(ip)
url = "http://" + ip + ":30000/service/stack/api/app"                                 
obj_json = {"name":"hello-test2","namespace":"default","stateful":"none","replicas":10,"cpu":100,"memory":256,"diskSize":20000,"containers":[{"name":"hello-test","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100}],"service":{"ports":[{"protocol":"TCP","containerPort":666,"servicePort":666}]},"volumes":[],"desc":"111"}
for i in range(app_num):
	obj_json['name'] = appname_tmp + str(i)
	app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json)) 				
	if "success" in json.loads(app_rtn)['status']:
		info('create application: %s successfully' % obj_json['name']) 
	else:
		sys.exit()		
info('sleep 120 seconds')
my_utils.bar_sleep(120)     

#create lb for each loadbalances
rtn = my_utils.create_tcp_lb_for_each_app(ip,80) 
if rtn != True:
	sys.exit()
info('sleep 120 seconds')
my_utils.bar_sleep(120)  

################################################check_app_status and check_lb_status########################################
#get app name
app_list = []
for i in range(app_num):
	appname = appname_tmp + str(i)
	app_list.append(appname)
	
#check app status
rtn = my_utils.check_app_status(ip,app_list)
if rtn != True:
	sys.exit()	

#check_lb_status
rtn = my_utils.check_lb_status(ip)
if rtn != True:
	sys.exit()
info('lb_status is ok!')
	
#let runnning 30 min
my_utils.bar_sleep(60)
	
#check app status
rtn = my_utils.check_app_status(ip,app_list)
if rtn != True:
	sys.exit()	

#check_lb_status
rtn = my_utils.check_lb_status(ip)
if rtn != True:
	sys.exit()
info('lb_status is ok!')	
	
#clean testbed
my_utils.clean_app(ip)
my_utils.delete_all_lb(ip)
info('ok')	

	