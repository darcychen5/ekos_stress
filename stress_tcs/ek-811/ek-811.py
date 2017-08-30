import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

ip = sys.argv[1]
testbed = sys.argv[2]
svc_num = 1
app_num = 100
svcname_tmp = "stress-centos-"
appname_tmp = "stress-app-"
cookies = my_utils._get_cookie(ip)
svc_list = []

stress_node_list = [{'name': 'stress1','vm':["EKOS-Offline-Stress-12","EKOS-Offline-Stress-13","EKOS-Offline-Stress-14"]},{'name': 'stress2','vm':["EKOS-Offline-Stress-17","EKOS-Offline-Stress-18","EKOS-Offline-Stress-19"]},{'name': 'stress3','vm':["EKOS-offline-darcy-62","EKOS-offline-darcy-63","EKOS-offline-darcy-64"]},{'name': 'stress4','vm':["EKOS-offline-Stress-10-84","EKOS-offline-Stress-10-85","EKOS-offline-Stress-10-86","EKOS-offline-Stress-10-87","EKOS-offline-Stress-10-88","EKOS-offline-Stress-10-89"]}]
node_list = []
for my_list in stress_node_list:
	if my_list['name'] == testbed:
		node_list = my_list['vm']
		break
if not node_list:
	error('wrong testbed!')
	sys.exit()

def run_test():
	#create stress-app
	for i in range(app_num):	
		app_name = appname_tmp + str(i)
		cookies = my_utils._get_cookie(ip)
		my_utils.create_app(ip,app_name)

		#create stress_svc
		url = "http://" + ip + ":30000/service/stack/api/app"                                 
		obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}]},"volumes":[],"desc":""}
		for j in range(svc_num):
			obj_json['name'] = app_name + "-" + svcname_tmp + str(j)
			svc_list.append(obj_json['name'])
			obj_json['stack'] = app_name
			app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json)) 
			if "success" in json.loads(app_rtn)['status']:
				info('create application: %s successfully' % obj_json['name'])
			else:
				return False					
	info('sleep 60 seconds')
	my_utils.bar_sleep(300)
					
	#get svc name
	# svc_list = []
	# for i in range(app_num*svc_num):
	# 	svcname = svcname_tmp + str(i)
	# 	svc_list.append(svcname)
	
	#check svc status
	print "check_svc_status first time"	
	rtn = my_utils.check_service_status(ip,svc_list)
	if rtn != True:
		return False	

	info("let it runnning 60s")
	my_utils.bar_sleep(60)
	
	#check svc status
	print "check_svc_status second time"	
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
	error('run test case ek-811 failed!')

	