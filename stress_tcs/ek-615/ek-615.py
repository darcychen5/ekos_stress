import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

ip = sys.argv[1]
testbed = sys.argv[2]
svc_num = 300
stress_svcname_tmp = "stress-bootstorm-"
cookies = my_utils._get_cookie(ip)


stress_node_list = [{'name': 'stress1','vm':["EKOS-Offline-Stress-12","EKOS-Offline-Stress-13","EKOS-Offline-Stress-14"]},{'name': 'stress2','vm':["EKOS-Offline-Stress-17","EKOS-Offline-Stress-18","EKOS-Offline-Stress-19"]},{'name': 'stress3','vm':["EKOS-offline-darcy-62","EKOS-offline-darcy-63","EKOS-offline-darcy-64"]}]
node_list = []
for my_list in stress_node_list:
	if my_list['name'] == testbed:
		node_list = my_list['vm']
		break
if not node_list:
	error('wrong testbed!')
	sys.exit()



def run_test():
	#create stress-app
	app_name = "stress-app"
	cookies = my_utils._get_cookie(ip)
	my_utils.create_app(ip,app_name)

	info('sleep 5 seconds after creating stress-app')
	my_utils.bar_sleep(5)

	#create stress_svc
	url = "http://" + ip + ":30000/service/stack/api/app"                                 
	#obj_json = {"name":"hello-test2","namespace":"default","stateful":"none","replicas":1,"cpu":100,"memory":256,"diskSize":20000,"containers":[{"name":"hello-test","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100}],"service":{"ports":[{"protocol":"TCP","containerPort":666,"servicePort":666}]},"volumes":[],"desc":"111"}
	obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}]},"volumes":[],"desc":""}
	for i in range(svc_num):
		obj_json['name'] = stress_svcname_tmp + str(i)
		app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json)) 
		if "success" in json.loads(app_rtn)['status']:
			info('create application: %s successfully' % obj_json['name'])
		else:
			return False
			
	info('sleep 600 seconds after creating 200 stress-svc')
	my_utils.bar_sleep(60)
			
	#get app name
	app_list = []
	for i in range(svc_num):
		appname = stress_svcname_tmp + str(i)
		app_list.append(appname)
		
	#check app status
	rtn = my_utils.check_service_status(ip,app_list)
	if rtn != True:
		return False	

	"""
	rtn = my_utils.k8s_pod_health_check(ip)
	if rtn != True:
		return False
	"""

	info('let it running 1800s')
	my_utils.bar_sleep(60)

	#check app status
	rtn = my_utils.check_service_status(ip,app_list)
	if rtn != True:
		return False

	my_utils.delete_app(ip,"stress-app")

	return True
		
#main
rtn = run_test()
if rtn == True:
	my_utils.clean_testbed(ip)
	info('create-delete-cycle is ok')
else:
	error('run test case ek-615 failed!')

	