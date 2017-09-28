import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()
testbed = sys.argv[2]
ip = sys.argv[1]
svc_num = 200
stress_svcname_tmp = "stress-svc-ha-"
node_list = eval(my_utils._get_config(testbed,"node_name_list","/root/ekos_stress/install/config.ini"))

def run_test():
	#create stress_app
	app_name = "stress-app"
	cookies = my_utils._get_cookie(ip)
	my_utils.create_app(ip,app_name)

	info('sleep 5 seconds')
	my_utils.bar_sleep(5)

	#create stress_svc 	
	url = "http://" + ip + ":30000/service/stack/api/app"
	obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}]},"volumes":[],"desc":""}
	for i in range(svc_num):
		obj_json['name'] = stress_svcname_tmp + str(i)
		rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json))
		if "success" in json.loads(rtn)['status']:
			info('create application: %s successfully' %obj_json['name'])
		else:
			return False


	#get svc name
	svc_list = my_utils.get_service_by_app(ip,app_name)
	#check svc running
	times = 1
	while times <= 11:
		rtn = my_utils.check_service_status(ip,svc_list) 
		if times == 11:
			return False
		elif rtn != True:
			info("this is %s check,please wait 60 seconds"%times)
			my_utils.bar_sleep(60)
			times=times+1
		else:
 			break
		
	
	#check node ready
	rtn = my_utils.check_node_ready(ip,"root","password")
	if rtn != True:
		return False
	# power off random node
	poweroff_nodes = random.sample(node_list,1)
	for poweroff_node in poweroff_nodes:
		my_utils.poweroff_vm(poweroff_node)

        #check svc running
        times = 1
        while times <= 11:
                rtn = my_utils.check_service_status(ip,svc_list)
                if times == 11:
                        return False
                elif rtn != True:
                        info("this is %s check,please wait 60 seconds"%times)
                        my_utils.bar_sleep(60)
                        times=times+1
                else:
                        break
		
	#power on the node
	for poweroff_node in poweroff_nodes:
		my_utils.poweron_vm(poweroff_node)

		
	return True

#main
rtn = run_test()
if rtn == True:
	my_utils.clean_testbed(ip)
	info('ok')
else:
	error('run test case ek-296 failed!')







