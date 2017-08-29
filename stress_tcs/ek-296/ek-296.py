import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

stress_node_list = [{'name': 'stress1','vm':["EKOS-Offline-Stress-12","EKOS-Offline-Stress-13","EKOS-Offline-Stress-14"]},{'name': 'stress2','vm':["EKOS-Offline-Stress-17","EKOS-Offline-Stress-18","EKOS-Offline-Stress-19"]},{'name': 'stress3','vm':["EKOS-offline-darcy-62","EKOS-offline-darcy-63","EKOS-offline-darcy-64"]},{'name': 'stress4','vm':["EKOS-offline-Stress-10-84","EKOS-offline-Stress-10-85","EKOS-offline-Stress-10-86","EKOS-offline-Stress-10-87","EKOS-offline-Stress-10-88","EKOS-offline-Stress-10-89"]}]

ip = sys.argv[1]
testbed = sys.argv[2] 
svc_num = 10
stress_svcname_tmp = "stress-svc-ha-"
node_list = []

for my_list in stress_node_list:
 	if my_list['name'] == testbed:
 		node_list = my_list['vm']
 		break
if not node_list:
 	error('wrong testbed!')
 	sys.exit()

def run_test():
	#create stress_app
	app_name = "stress-app"
	cookies = my_utils._get_cookie(ip)
	my_utils.create_app(ip,app_name)

	info('sleep 5 seconds')
	my_utils.bar_sleep(5)

	#create stress_svc 	
	#cookies = my_utils._get_cookie(ip)
	url = "http://" + ip + ":30000/service/stack/api/app"
	obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}]},"volumes":[],"desc":""}
	for i in range(svc_num):
		obj_json['name'] = stress_svcname_tmp + str(i)
		rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json))
		if "success" in json.loads(rtn)['status']:
			info('create application: %s successfully' %obj_json['name'])
		else:
			return False

	info('sleep 120 seconds')
	my_utils.bar_sleep(120)

	#get svc name
	svc_list = my_utils.get_service_by_app(app_name)
	#check svc running
	rtn = my_utils.check_service_status(ip,svc_list) #app svc 
	if rtn != True:
		return False
	
	
	#check node ready
	rtn = my_utils.check_node_ready(ip,"root","password")
	if rtn != True:
		return False
		
	# rtn = my_utils.k8s_pod_health_check(ip)
	# if rtn != True:
	# 	return False

	# power off random node
	poweroff_nodes = random.sample(node_list,1)
	for poweroff_node in poweroff_nodes:
		my_utils.poweroff_vm(poweroff_node)

	info("sleep 120 seconds")
	my_utils.bar_sleep(120)
	
	#check pods status
	rtn = my_utils.check_service_status(ip,svc_list)
	if rtn != True:
		return False
		
	#power on the node
	for poweroff_node in poweroff_nodes:
		my_utils.poweron_vm(poweroff_node)

	# my_utils.bar_sleep(1800)
	# rtn = my_utils.k8s_pod_health_check(ip)
	# if rtn == True:
	# 	return True
	# else:
	# 	return False
		
	return True

#main
rtn = run_test()
if rtn == True:
	my_utils.clean_testbed(ip)
	info('create app and svc ok')
else:
	error('run test case ek-296 failed!')







