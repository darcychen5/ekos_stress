import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

stress_node_list = [{'name': 'stress1','vm':["EKOS-Offline-Stress-12","EKOS-Offline-Stress-13","EKOS-Offline-Stress-14"]},{'name': 'stress2','vm':["EKOS-Offline-Stress-17","EKOS-Offline-Stress-18","EKOS-Offline-Stress-19"]},{'name': 'stress3','vm':["EKOS-offline-darcy-62","EKOS-offline-darcy-63","EKOS-offline-darcy-64"]},{'name': 'stress4','vm':["EKOS-offline-Stress-10-84","EKOS-offline-Stress-10-85","EKOS-offline-Stress-10-86","EKOS-offline-Stress-10-87","EKOS-offline-Stress-10-88","EKOS-offline-Stress-10-89"]}]

ip = sys.argv[1]
testbed = sys.argv[2]
svcname_tmp1 = "stress-bootstorm-pod-eachother-server-"
svcname_tmp2 = "stress-bootstorm-pod-eachother-client-"
svc_num = 8
node_list = []
apache_server_name_list = []
apache_client_name_list = []
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
	cookies = my_utils._get_cookie(ip)
	url = "http://" + ip + ":30000/service/stack/api/app"
	obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}]},"volumes":[],"desc":""}
	for i in range(svc_num):
		if i < (svc_num / 2):
			obj_json['name'] = svcname_tmp1 + str(i)
			apache_server_name_list.append(obj_json['name'])		
			app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json))
			if "success" in json.loads(app_rtn)['status']:
				info('create application: %s successfully' %obj_json['name'])
			else:
				return False
		else:
			obj_json['name'] = svcname_tmp2 + str(i)
			apache_client_name_list.append(obj_json['name'])
			obj_json['containers'][0]['image'] = "registry.ekos.local/library/apache-client:latest"  
			app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json))
			if "success" in json.loads(app_rtn)['status']:
				info('create application: %s successfully' %obj_json['name'])
			else:
				return False

	svc_list = my_utils.get_all_app(ip)
	if not svc_list:
		error('No app running!')
		return False

	info('sleep 60s after create app')
	my_utils.bar_sleep(60)

	#check app status
	rtn = my_utils.check_service_status(ip,svc_list)
	if rtn != True:
		return False

	#one pod access to another pod  
	for server_name in apache_server_name_list:
		for client_name in apache_client_name_list:
			cmd = "kubectl exec -it " + client_name + "-" + str(0) + " -- curl -O " + server_name + "-" + str(0) + "." + server_name + ":80/filebench_stress.tgz"
			rtn = my_utils.ssh_cmd(ip, "root", "password", cmd)	
			info('sleep 30s downloadding the file from another pod')
			my_utils.bar_sleep(30)			
	
	info("sleep 60s afer pod to pod")
	my_utils.bar_sleep(60)
	
	#check app running	
	rtn = my_utils.check_service_status(ip,svc_list)
	if rtn != True:
		return False
		
	#rtn = my_utils.k8s_pod_health_check(ip)
	#if rtn == True:
	#	return True
	#else:
	#	return False

	#clean testbed
	#my_utils.clean_app(ip)

	return True

#main
rtn = run_test()
if rtn == True:
	my_utils.clean_testbed(ip)
	info('ok')
else:
	error('run test case ek-690 failed!')







