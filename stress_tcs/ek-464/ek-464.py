import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

ip = sys.argv[1]
testbed = sys.argv[2]
svc_num = 300
stress_svcname_tmp = "stress-bootstorm-"


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
	#create stress_app
	app_name = "stress-app"
	cookies = my_utils._get_cookie(ip)
	my_utils.create_app(ip,app_name)

	info('sleep 5 seconds')
	my_utils.bar_sleep(5)

	#create stress_svc 	
	cookies = my_utils._get_cookie(ip)
	url = "http://" + ip + ":30000/service/stack/api/app"
	obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}]},"volumes":[],"desc":""}
	for i in range(svc_num):
		obj_json['name'] = stress_svcname_tmp + str(i)
		rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json))
		if "success" in json.loads(rtn)['status']:
			info('create application: %s successfully' %obj_json['name'])
		else:
			return False

#	info('sleep 600 seconds after creating all(300) stress_svc')
#	my_utils.bar_sleep(900)
	
	#check node 

	rtn = my_utils.check_node_ready(ip,"root","password")
	if rtn != True:
		return False

	#get app name
	svc_list = []
	for i in range(svc_num):
		svcname = stress_svcname_tmp + str(i)
		svc_list.append(svcname)

	print "check_service_status"
        times = 1
        while times <= 11:
                rtn = my_utils.check_service_status(ip,svc_list)
                if rtn != True:
                        info("this is %s times check,have pods not Running please wait 30 seconds will try again"%times)
                        my_utils.bar_sleep(30)
                        times=times+1
                elif times == 11:
                        return False
                else:
                        break
	"""
	rtn = my_utils.k8s_pod_health_check(ip)
	if rtn != True:
		return False
	"""
	info("let runnning 30 min")
	my_utils.bar_sleep(1800)
	
	print "check_service_status after runnning 30 min"	
	#check app status
        times = 1
        while times <= 11:
                rtn = my_utils.check_service_status(ip,svc_list)
                if rtn != True:
                        info("this is %s times check,have pods not Running please wait 30 seconds will try again"%times)
                        my_utils.bar_sleep(30)
                        times=times+1
                elif times == 11:
			info("running 20 minutes pods status not health")
                        return False
                else:
			return True
			break
	"""
	rtn = my_utils.k8s_pod_health_check(ip)
	if rtn != True:
		return False
	"""

#main
rtn = run_test()
if rtn == True:
	my_utils.delete_all_app(ip)
        cmd = "kubectl get po | grep " + stress_svcname_tmp + "| grep Running"
	times=1
        info("checking clean testbed status ! this is %s checking"%times)
	while times <= 11:
        	rtn = my_utils.ssh_cmd(ip,"root","password",cmd)
        	if rtn["stdout"] != "":
                	print "cleaning testbed not done... please wait 30 senconds will try again "
                	my_utils.bar_sleep(30)
			times=times+1
		elif times == 11:
			error("have any pod not delete success,run test case ek-464 failed")
		else:
			info("ok")
			break
else:
	error('run test case ek-464 failed!')


