import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

ip = sys.argv[1]
svc_num = 300
svcname_tmp = "mysql-stress-"
cookies = my_utils._get_cookie(ip)
def run_test():
	#create stress-app
	app_name = "stress-app"
	cookies = my_utils._get_cookie(ip)
	my_utils.create_app(ip,app_name)

	info('sleep 5 seconds after creating stress-app')
	my_utils.bar_sleep(5)

	#create stress_svc
	url = "http://" + ip + ":30000/service/stack/api/app"                                 
	obj_json = {"name":"mysql","namespace":"default","stack":"test","stateful":"share","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"collectLog":True,"scheduler":None,"containers":[{"name":"test","image":"registry.ekos.local/library/mysql:latest","command":"","stdin":False,"tty":False,"envs":[],"healthCheck":None,"cfgFileMounts":[],"secretMounts":[],"hostMounts":[],"volumes":[],"cpuPercent":100,"memPercent":100}],"service":{"ports":[{"containerPort":3306,"servicePort":3306,"protocol":"TCP"}]},"desc":""}
	for i in range(svc_num):
		obj_json['name'] = svcname_tmp + str(i)
		app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json)) 
		if "success" in json.loads(app_rtn)['status']:
			info('create application: %s successfully' % obj_json['name'])
		else:
			return False
			
	info('sleep 60 seconds')
	my_utils.bar_sleep(60)
			
	#get app name
	svc_list = my_utils.get_service_by_app(ip,app_name)
	#check app status
	print "check_app_status first time"	
	times = 1
	while times <= 10:
		rtn = my_utils.check_service_status(ip,svc_list)
		if times == 11:
			info('check 10 times done! have svc not Running,tc-728 faied')
			return False
		if rtn != True:
			info('this is %s times check have svc not running sleep 60s try again'%times)
			my_utils.bar_sleep(60)
			times = times +1
		else:
			break
	#mysql-stress test with mysqlslap 
	for i in svc_list:
		cmd = "kubectl exec -it " + i + "-" + str(0) + " -- " + "mysqlslap -uroot -p123abc --concurrency=10,50,100 --iterations=1000 --auto-generate-sql --auto-generate-sql-load-type=mixed --auto-generate-sql-add-autoincrement --engine=myisam --number-of-queries=10 --debug-info --only-print"
		rtn = my_utils.ssh_cmd(ip, "root", "password", cmd)	
	
	info("let it runnning 60s")
	my_utils.bar_sleep(60)
	
	#check app status
	print "check_app_status second time"	
	rtn = my_utils.check_service_status(ip,svc_list)
	if rtn != True:
		return False

	for i in svc_list:
		cmd = "kubectl exec -it mysql-test-0 -- mysql -u root -e \"use test;\""
		rtn = my_utils.ssh_cmd(ip, "root", "password", cmd)
		if rtn != {}:
			return error
	
	info("sleep 30s")
	my_utils.bar_sleep(30)

	return True
		
#main
rtn = run_test()
if rtn == True:
	my_utils.clean_testbed(ip)
	info('ok')
else:
	error('run test case ek-728 failed!')

	
