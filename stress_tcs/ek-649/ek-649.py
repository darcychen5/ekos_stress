import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

ip = sys.argv[1]
testbed = sys.argv[2]
app_num = 200
appname_tmp = "stress-bootstorm-"
cookies = my_utils._get_cookie(ip)


stress_node_list = [{'name': 'stress1','vm':["EKOS-Offline-Stress-12","EKOS-Offline-Stress-13","EKOS-Offline-Stress-14"]},{'name': 'stress2','vm':["EKOS-Offline-Stress-17","EKOS-Offline-Stress-18","EKOS-Offline-Stress-19"]},{'name': 'stress3','vm':["EKOS-offline-darcy-62","EKOS-offline-darcy-63","EKOS-offline-darcy-64"]}]
node_list = []
for my_list in stress_node_list:
	if my_list['name'] == testbed:
		node_list = my_list['vm']
		break
if not node_list:
	error('wrong testbed!')
	sys.exit()


#create 300 app
def run_test():
	for j in range(50):	
		url = "http://" + ip + ":30000/service/stack/api/app"                                 
		obj_json = {"name":"hello-test2","namespace":"default","stateful":"none","replicas":1,"cpu":100,"memory":256,"diskSize":20000,"containers":[{"name":"container01","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100},{"name":"container02","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100},{"name":"container03","image":"registry.ekos.local/library/hello:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100}],"service":{"ports":[{"protocol":"TCP","containerPort":666,"servicePort":666}]},"volumes":[],"desc":"111"}
		for i in range(app_num):
			obj_json['name'] = appname_tmp + str(i)
			app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json)) 
			if "success" in json.loads(app_rtn)['status']:
				info('create application: %s successfully' % obj_json['name'])
			else:
				return False
				
		info('sleep 300 seconds')
		my_utils.bar_sleep(300)
				
		#get app name
		app_list = []
		for i in range(app_num):
			appname = appname_tmp + str(i)
			app_list.append(appname)
		print "check_app_status first time"

		#check app status
		rtn = my_utils.check_app_status(ip,app_list)
		if rtn != True:
			return False	

		"""
		rtn = my_utils.k8s_pod_health_check(ip)
		if rtn != True:
			return False
		"""
		my_utils.clean_app(ip)
	return True
		
#main
rtn = run_test()
if rtn == True:
	#my_utils.clean_testbed(ip)
	info('create-delete-cycle is ok')
else:
	error('run test case ek-649 failed!')

	