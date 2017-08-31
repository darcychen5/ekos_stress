import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

lb_name = "stress-lb"
app_name = "stress-app"
stress_svcname_tmp = "stress-bootstorm-lb-"
svc_num = 300

ip = sys.argv[1]
testbed = sys.argv[2]


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
	cookies = my_utils._get_cookie(ip)
	my_utils.create_app(ip,app_name)

	info('sleep 5 seconds')
	my_utils.bar_sleep(5)

	#create stress_svc 	
	cookies = my_utils._get_cookie(ip)
	url = "http://" + ip + ":30000/service/stack/api/app"
	obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/hello:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":80,"servicePort":80}]},"volumes":[],"desc":""}
	for i in range(svc_num):
		obj_json['name'] = stress_svcname_tmp + str(i)
		rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json))
		if "success" in json.loads(rtn)['status']:
			info('create application: %s successfully' %obj_json['name'])
		else:
			return False

	info('create all svc success,sleep 20 minutes')
	my_utils.bar_sleep(1200)
	
        #get svc name
        svc_list = []
        for i in range(svc_num):
                svcname = stress_svcname_tmp + str(i)
                svc_list.append(svcname)

        #check svc status
        print"beginning check svc status frist time"
        rtn = my_utils.check_service_status(ip,svc_list)
        if rtn != True:
                sys.exit()

	#create lb 
	rtn = my_utils.create_lb(ip,lb_name) 
	if rtn != True:
		sys.exit()

	info('create lb success,sleep 30 seconds')
	my_utils.bar_sleep(30)

	#create_http rule for all service
	rtn = my_utils.add_http_rule_for_all_service(ip,lb_name)
	if rtn != True:
		return False  

	info("create http rule for all svc success,sleep 5 minutes")
        my_utils.bar_sleep(300)
	################################################check_app_status and check_lb_status########################################
	#get svc name
	svc_list = []
	for i in range(svc_num):
		svcname = stress_svcname_tmp + str(i)
		svc_list.append(svcname)

	#check svc status
	print"beginning check svc status second times"	
	rtn = my_utils.check_service_status(ip,svc_list)
	if rtn != True:
		sys.exit()	

	#check lb status
	print "beginning check lb"
	rtn = my_utils.check_lb_status(ip)
	if rtn != True:
		return False
	return True
#main
rtn = run_test()
if rtn == True:
	my_utils.clean_testbed(ip)
	info("wait for clean testbed,sleep 10 minutes")
	my_utils.bar_sleep(600)
	cmd = "kubectl get po | grep " + stress_svcname_tmp + "| grep Running"
	rtn = my_utils.ssh_cmd(ip,"root","password",cmd)
	if rtn["stdout"] == "":
		print "clean testbed successful!"
		info('ok')
	else:
		error("have any pod not delete success,run test case ek-465 failed")
else:
	error('run test case ek-465 failed!')
