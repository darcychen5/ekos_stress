import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

stress_svcname_tmp = "stress-bootstorm-lb-"
svc_num = 3

ip = sys.argv[1]
testbed = sys.argv[2]


stress_node_list = [{'name': 'stress1','vm':["EKOS-Offline-Stress-12","EKOS-Offline-Stress-13","EKOS-Offline-Stress-14"]},{'name': 'stress2','vm':["EKOS-Offline-Stress-17","EKOS-Offline-Stress-18","EKOS-Offline-Stress-19"]},{'name': 'stress3','vm':["EKOS-offline-darcy-62","EKOS-offline-darcy-63","EKOS-offline-darcy-64"]}]
node_list = []
for my_list in stress_node_list:
	if my_list['name'] == testbed:
		node_list = my_list['vm']
		break
if not node_list:
	error('wrong testbed!')
	sys.exit()


#create 3 app
def run_test():
	#create stress_app
	app_name = "stress_app"
	cookies = my_utils._get_cookie(ip)
	my_utils.create_app(ip,app_name)

	info('sleep 1200 seconds')
	my_utils.bar_sleep(5)

	#create stress_svc 	
	cookies = my_utils._get_cookie(ip)
	url = "http://" + ip + ":30000/service/stack/api/app"
	obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress_app","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/hello:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}]},"volumes":[],"desc":""}
	for i in range(svc_num):
		obj_json['name'] = stress_svcname_tmp + str(i)
		rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json))
		if "success" in json.loads(rtn)['status']:
			info('create application: %s successfully' %obj_json['name'])
		else:
			return False

		info('sleep 1200 seconds')
		my_utils.bar_sleep(10)
	
	#create lb for each loadbalances
	rtn = my_utils.create_tcp_lb_for_each_app(ip,80) 
	if rtn != True:
		sys.exit()
	info('sleep 120 seconds')
	my_utils.bar_sleep(120)  

	################################################check_app_status and check_lb_status########################################
	#get app name
	svc_list = []
	for i in range(svc_num):
		svcname = stress_svcname_tmp + str(i)
		svc_list.append(svcname)
	print "check_app_status first time"

	#check app status
	rtn = my_utils.check_app_status(ip,svc_list)
	if rtn != True:
		sys.exit()	
	"""
	rtn = my_utils.k8s_pod_health_check(ip)
	if rtn != True:
		return False
	
	#check_lb_status
	rtn = my_utils.check_lb_status(ip)
	if rtn != True:
		sys.exit()
	info('lb_status is ok!')
	"""	
	#let runnning 10 min
	my_utils.bar_sleep(60)
	print"check_app_status after runnning 10 min"	
	#check app status
	rtn = my_utils.check_app_status(ip,svc_list)
	if rtn != True:
		sys.exit()	
	"""
	rtn = my_utils.k8s_pod_health_check(ip)
	if rtn != True:
		return False

	#check_lb_status
	rtn = my_utils.check_lb_status(ip)
	if rtn != True:
		sys.exit()
	info('lb_status is ok!')	
	"""	
#main
rtn = run_test()
if rtn == True:
	my_utils.clean_testbed(ip)
	info('ok')
else:
	error('run test case ek-465 failed!')