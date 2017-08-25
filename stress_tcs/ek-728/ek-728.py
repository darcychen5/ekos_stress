import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

ip = sys.argv[1]
testbed = sys.argv[2]
app_num = 150
appname_tmp = "mysql-stress-"
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
	url = "http://" + ip + ":30000/service/stack/api/app"                                 
	obj_json = {"name":"hello-test2","namespace":"default","stateful":"share","replicas":1,"cpu":100,"memory":256,"diskSize":20000,"containers":[{"name":"hello-test","image":"registry.ekos.local/ekos/mysql:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100}],"service":{"ports":[{"protocol":"TCP","containerPort":666,"servicePort":666}]},"volumes":[],"desc":"111"}
	for i in range(app_num):
		obj_json['name'] = appname_tmp + str(i)
		app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json)) 
		if "success" in json.loads(app_rtn)['status']:
			info('create application: %s successfully' % obj_json['name'])
		else:
			return False
			
	info('sleep 600 seconds')
	my_utils.bar_sleep(600)
			
	#get app name
	app_list = []
	for i in range(app_num):
		appname = appname_tmp + str(i)
		app_list.append(appname)
	
	#check app status
	print "check_app_status first time"	
	rtn = my_utils.check_app_status(ip,app_list)
	if rtn != True:
		return False	

	"""
	rtn = my_utils.k8s_pod_health_check(ip)
	if rtn != True:
		return False
	"""
	#mysql-stress test with mysqlslap 
	for i in app_list:
		cmd = "kubectl exec -it " + i + "-" + str(0) + " -- " + "mysqlslap -uroot -p123abc --concurrency=10,50,100 --iterations=1000 --auto-generate-sql --auto-generate-sql-load-type=mixed --auto-generate-sql-add-autoincrement --engine=myisam --number-of-queries=10 --debug-info --only-print"
		rtn = my_utils.ssh_cmd(ip, "root", "password", cmd)	
		#info('executing mysqlslap for 120s')
		#my_utils.bar_sleep(120)			
	
	info("let it runnning 120s")
	my_utils.bar_sleep(120)
	
	#check app status
	print "check_app_status second time"	
	rtn = my_utils.check_app_status(ip,app_list)
	if rtn != True:
		return False

	for i in app_list:
		cmd = "kubectl exec -it mysql-test-0 -- mysql -u root -e \"use test;\""
		rtn = my_utils.ssh_cmd(ip, "root", "password", cmd)
		#if rtn != {}:
			#return error
	
	info("sleep 300s")
	my_utils.bar_sleep(300)

	return True
		
#main
rtn = run_test()
if rtn == True:
	my_utils.clean_testbed(ip)
	info('create-delete-cycle is ok')
else:
	error('run test case ek-728 failed!')

	