import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()
testbed = sys.argv[2]
ip = sys.argv[1]
stress_svcname_tmp = "stress-ha-"
svc_num = 200
node_list = eval(my_utils._get_config(testbed,"node_name_list","/root/ekos_stress/install/config.ini"))

def run_test():
	#create stress_app
	app_name = "stress-app"
	cookies = my_utils._get_cookie(ip)
	my_utils.create_app(ip,app_name)

	#create stress_svc
	cookies = my_utils._get_cookie(ip)
	url = "http://" + ip + ":30000/service/stack/api/app"
	obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"container01","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":33,"memPercent":33,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]},{"name":"container02","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":33,"memPercent":33,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]},{"name":"container03","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":33,"memPercent":33,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":666,"servicePort":888}]},"volumes":[],"desc":""}
	for i in range(svc_num):
		obj_json['name'] = stress_svcname_tmp + str(i)
		app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json))
		if "success" in json.loads(app_rtn)['status']:
			info('create application: %s successfully' %obj_json['name'])
		else:
			return False
	info('sleep 800 seconds')
	my_utils.bar_sleep(800)
	
	#get app name
	svc_list = my_utils.get_service_by_app(ip,app_name)
	#check app running
	rtn = my_utils.check_service_status(ip,svc_list)
	if rtn != True:
		return False
	
	#check node ready
	rtn = my_utils.check_node_ready(ip,"root","password")
	if rtn != True:
		return False

	# power off random node	
	poweroff_nodes = random.sample(node_list,1)
	for poweroff_node in poweroff_nodes:
		my_utils.poweroff_vm(poweroff_node)

	print"sleep 120 after power off random node"

	my_utils.bar_sleep(600)
		
	#check app running
	rtn = my_utils.check_service_status(ip,svc_list)
	if rtn != True:
		return False
		
	#power on the node
	for poweroff_node in poweroff_nodes:
		my_utils.poweron_vm(poweroff_node)

	my_utils.bar_sleep(300)

	#check node ready
	rtn = my_utils.check_node_ready(ip,"root","password")
	if rtn != True:
		return False

	#check app running
	rtn = my_utils.check_service_status(ip,svc_list)
	if rtn != True:
		return False


	return True
#main
rtn = run_test()
if rtn == True:
	my_utils.clean_testbed(ip)
	info('ok')
else:
	error('run test case ek-535 failed!')







