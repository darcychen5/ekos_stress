import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *

ip = sys.argv[1]
testbed = sys.argv[2]
stress_svcname_tmp = "stress-powercycle-"
svc_num = 200
my_utils = ekosUtils.Utils()
node_list = eval(my_utils._get_config(testbed,"node_name_list","/root/ekos_stress/install/config.ini"))

def run_test():
	#create stress_app
	app_name = "stress-app"
	cookies = my_utils._get_cookie(ip)
	my_utils.create_app(ip,app_name)

	info('sleep 10 seconds after creating stress_app')
	my_utils.bar_sleep(10)

	#create stress_svc 	
	cookies = my_utils._get_cookie(ip)
	url = "http://" + ip + ":30000/service/stack/api/app"
	obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/hello:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}]},"volumes":[],"desc":""}
	for i in range(svc_num):
		obj_json['name'] = stress_svcname_tmp + str(i)
		rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json))
		if "success" in json.loads(rtn)['status']:
			info('create application: %s successfully' %obj_json['name'])
		else:
			return False
	
	info('sleep 60 seconds after creating all stress_svc ')
	my_utils.bar_sleep(60)

	#get app name
	svc_list = my_utils.get_service_by_app(ip,app_name)
	#check app running
	times = 1
	while times <= 10:
		rtn = my_utils.check_service_status(ip,svc_list)
		if times == 11:
			info('check svc 10 times done!have svc not Running.run tc-318 faied!')
			return False
		if rtn != True:
			info('this is %s times check,have svc not Running.sleep 60s will try again!'%times)
			my_utils-bar_sleep(60)
			times = times +1
		else:
			break
	#power off nodes sequentially 
	for node in node_list:
		rtn = my_utils.poweroff_vm(node)
		if rtn != True:
			error("power off node failed!")
			return False
		my_utils.bar_sleep(10)
	
	info('power off node done,sleep 60 seconds')  
	my_utils.bar_sleep(60)
	
	#power on all nodes	
	for node in node_list:
		rtn = my_utils.poweron_vm(node)
		if rtn != True:
			error('power on node failed')
			return False
	
	info('Power on node done,sleep 10 minutes')
	my_utils.bar_sleep(600)
	
	#check node ready
	rtn = my_utils.check_node_ready(ip,"root","password")
	if rtn != True:
		return False

	print "check_service_status begining"
	
	rtn = my_utils._get_cookie(ip)

	#check app status
	rtn = my_utils.check_service_status(ip,svc_list)
	if rtn != True:
		return False

	print "clean testbed begining"
		
	return True
	


	

#main
rtn = run_test()
if rtn == True:
	my_utils.clean_testbed(ip)
	info('ok')
else:
	error('run test case ek-318 failed!')
