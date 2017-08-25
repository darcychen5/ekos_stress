import sys,json,time,random
sys.path.insert(0, '/root/ekos_auto/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

appname_tmp = "stress-bootstorm-"
app_num = 5


#create 5 app
ip = sys.argv[1]
cookies = my_utils._get_cookie(ip)
url = "http://" + ip + ":30000/service/stack/api/app"                                 #
obj_json = {"name":"hello-test2","namespace":"default","stateful":"none","replicas":1,"cpu":100,"memory":256,"diskSize":20000,"containers":[{"name":"hello-test","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100}],"service":{"ports":[{"protocol":"TCP","containerPort":666,"servicePort":666}]},"volumes":[],"desc":"111"}
for i in range(app_num):
	obj_json['name'] = appname_tmp + str(i)
	app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json)) 
	if "success" in json.loads(app_rtn)['status']:
		info('create application: %s successfully' % obj_json['name']) 
	else:
		sys.exit()
		
info('sleep 120 seconds')
my_utils.bar_sleep(120) 

#get app name
app_list = []
for i in range(app_num):
	appname = appname_tmp + str(i)
	app_list.append(appname)
	
#check app status
rtn = my_utils.check_app_status(ip,app_list)
if rtn != True:
	sys.exit()	

#changePodNum
allappname = my_utils.get_all_app(ip)
#print allappname
PodNum = [3,5,1]
for i in range(len(PodNum)):
	for j in allappname:
		pod_rtn = my_utils.change_app_replica(ip,j,PodNum[i])
		#print pod_rtn
		#info('sleep 60 seconds')
		#check app status
		rtn = my_utils.check_app_status(ip,app_list)
		if rtn != True:
			sys.exit()
		rtn = my_utils.get_all_replica(ip,j)
		if rtn != PodNum[i]:
			sys.exit()
	info('Now PodNum is %s' % PodNum[i])
		
info('sleep 60 seconds')
my_utils.bar_sleep(60) 



#clean testbed
my_utils.clean_app(ip)

info('ok')
