import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()


ip = sys.argv[1]
testbed = sys.argv[2]
svcname_tmp1 = "stress-server-"
svcname_tmp2 = "stress-client-"
svc_num = 200
node_list = []
apache_server_name_list = []
apache_client_name_list = []


def run_test():
	#create stress-app
	app_name_server = "stress-app-server"
	app_name_client = "stress-app-client"
	cookies = my_utils._get_cookie(ip)
	my_utils.create_app(ip,app_name_server)
	my_utils.create_app(ip,app_name_client)


	info('sleep 5 seconds after creating stress-app')
	my_utils.bar_sleep(5)

	#create stress_svc
	cookies = my_utils._get_cookie(ip)
	url = "http://" + ip + ":30000/service/stack/api/app"
	obj_json = {"name":"apache-server-1","namespace":"default","stack":"ttttt","stateful":"share","replicas":1,"cpu":250,"memory":64,"diskSize":20000,"scheduler":None,"containers":[{"name":"apache-server-1","image":"registry.ekos.local/library/apache-server:latest","command":"","stdin":False,"tty":False,"envs":[],"healthCheck":None,"cfgFileMounts":[],"secretMounts":[],"hostMounts":[],"cpuPercent":100,"memPercent":100}],"service":{"ports":[{"containerPort":80,"servicePort":80,"protocol":"TCP"}]},"volumes":[],"desc":""}
	for i in range(svc_num):
		if i < (svc_num / 2):
			obj_json['stack'] = app_name_server
			obj_json['name'] = svcname_tmp1 + str(i)
			apache_server_name_list.append(obj_json['name'])
			app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json))
			if "success" in json.loads(app_rtn)['status']:
				info('create application: %s successfully' %obj_json['name'])
			else:
				return False
		else:
			obj_json['stack'] = app_name_client
			obj_json['name'] = svcname_tmp2 + str(i)
			apache_client_name_list.append(obj_json['name'])
			obj_json['containers'][0]['image'] = "registry.ekos.local/library/apache-client:latest"  
			obj_json['containers'][0]['command'] = "sh -c \"sleep 300m\""  
			app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json))
			if "success" in json.loads(app_rtn)['status']:
				info('create application: %s successfully' %obj_json['name'])
			else:
				return False

	info('sleep 300s after create app')
	my_utils.bar_sleep(300)

	#check app status
	app_list = my_utils.get_all_app(ip)
	#check app running
	for app in app_list:
		service_name = my_utils.get_service_by_app(ip,app)
		rtn = my_utils.check_service_status(ip,service_name)
		if rtn != True:
			return False

	#one pod access to another pod  
	for server_name in apache_server_name_list:
		for client_name in apache_client_name_list:
			cmd = "kubectl exec -it " + client_name + "-" + str(0) + " -- curl -O " + server_name + "-" + str(0) + "." + server_name + ":80/filebench_stress.tgz"
			rtn = my_utils.ssh_cmd(ip, "root", "password", cmd)	
			info('sleep 5s downloadding the file from another pod')
			my_utils.bar_sleep(1)		
	
	info("sleep 300s afer pod to pod")
	my_utils.bar_sleep(300)
	
	#check app status
	app_list = my_utils.get_all_app(ip)
	#check app running
	for app in app_list:
		service_name = my_utils.get_service_by_app(ip,app)
		rtn = my_utils.check_service_status(ip,service_name)
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







