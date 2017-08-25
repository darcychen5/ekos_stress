import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

stress_node_list = [{'name': 'stress1','vm':["EKOS-Offline-Stress-12","EKOS-Offline-Stress-13","EKOS-Offline-Stress-14"]},{'name': 'stress2','vm':["EKOS-Offline-Stress-17","EKOS-Offline-Stress-18","EKOS-Offline-Stress-19"]},{'name': 'stress3','vm':["EKOS-offline-darcy-62","EKOS-offline-darcy-63","EKOS-offline-darcy-64"]}]

ip = sys.argv[1]
testbed = sys.argv[2]
appname_tmp1 = "stress-bootstorm-pod-eachother-server-"
appname_tmp2 = "stress-bootstorm-pod-eachother-client-"
app_num = 150
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
	#create 300 app
	cookies = my_utils._get_cookie(ip)
	url = "http://" + ip + ":30000/service/stack/api/app"
	obj_json = {"name":"hello-test2","namespace":"default","stateful":"share","replicas":1,"cpu":100,"memory":256,"diskSize":20000,"containers":[{"name":"hello-test","image":"registry.ekos.local/library/apache-server:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100}],"service":{"ports":[{"protocol":"TCP","containerPort":666,"servicePort":666}]},"volumes":[],"desc":"111"}
	for i in range(app_num):
		if i < (app_num / 2):
			obj_json['name'] = appname_tmp1 + str(i)
			apache_server_name_list.append(obj_json['name'])		
			app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json))
			if "success" in json.loads(app_rtn)['status']:
				info('create application: %s successfully' %obj_json['name'])
			else:
				return False
		else:
			obj_json['name'] = appname_tmp2 + str(i)
			apache_client_name_list.append(obj_json['name'])
			obj_json['containers'][0]['image'] = "registry.ekos.local/library/apache-client:latest"  
			app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json))
			if "success" in json.loads(app_rtn)['status']:
				info('create application: %s successfully' %obj_json['name'])
			else:
				return False

	app_list = my_utils.get_all_app(ip)
	if not app_list:
		error('No app running!')
		return False

	info('sleep 600s after create app')
	my_utils.bar_sleep(600)

	#check app status
	rtn = my_utils.check_app_status(ip,app_list)
	if rtn != True:
		return False

	#one pod access to another pod  
	for server_name in apache_server_name_list:
		for client_name in apache_client_name_list:
			cmd = "kubectl exec -it " + client_name + "-" + str(0) + " -- curl -O " + server_name + "-" + str(0) + "." + server_name + ":80/filebench_stress.tgz"
			rtn = my_utils.ssh_cmd(ip, "root", "password", cmd)	
			info('sleep 30s downloadding the file from another pod')
			my_utils.bar_sleep(30)			
	
	info("sleep 300s afer pod to pod")
	my_utils.bar_sleep(300)
	
	#check app running	
	rtn = my_utils.check_app_status(ip,app_list)
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







