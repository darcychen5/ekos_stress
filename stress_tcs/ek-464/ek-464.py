import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()
ip = sys.argv[1]
svc_num = 250
stress_svcname_tmp = "stress-bootstorm-"
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
	
	#check node 

	rtn = my_utils.check_node_ready(ip,"root","password")
	if rtn != True:
		return False

	#get app name
	svc_list = my_utils.get_service_by_app(ip,app_name)
	print "check_service_status"
        times = 1
        while times <= 11:
                rtn = my_utils.check_service_status(ip,svc_list)
                if times == 11:
                        return False
                if rtn != True:
                        info("this is %s times check,have pods not Running please wait 60 seconds will try again"%times)
                        my_utils.bar_sleep(60)
                        times=times+1
                else:
                        break
	info("let runnning 30 min")
	my_utils.bar_sleep(1800)
	
	print "check_service_status after runnning 30 min"	
	#check app status
        times = 1
        while times <= 11:
                rtn = my_utils.check_service_status(ip,svc_list)
                if times == 11:
                        return False
			info("running 20 minutes pods status not health")
                if rtn != True:
                        info("this is %s times check,have pods not Running please wait 30 seconds will try again"%times)
                        my_utils.bar_sleep(30)
                        times=times+1
                else:
			return True
			break

#main
rtn = run_test()
if rtn == True:
	my_utils.delete_all_app(ip)
	info('ok')
else:
	error('run test case ek-464 failed!')


