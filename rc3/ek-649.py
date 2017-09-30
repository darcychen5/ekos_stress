import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()
ip = sys.argv[1]
app_name = "stress-app"
svc_num = 200
stress_svcname_tmp = "stress-bootstorm-"
cookies = my_utils._get_cookie(ip)

def run_test():
	#create stress_app
	cookies = my_utils._get_cookie(ip)
	my_utils.create_app(ip,app_name)

	info('sleep 5 seconds')
	my_utils.bar_sleep(5)

	#create stress_svc		
	url = "http://" + ip + ":30000/service/stack/api/app"                                 
	obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"container01","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":33,"memPercent":33,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]},{"name":"container02","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":33,"memPercent":33,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]},{"name":"container03","image":"registry.ekos.local/library/hello:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":33,"memPercent":33,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":666,"servicePort":888}]},"volumes":[],"desc":""}
	for i in range(svc_num):
		obj_json['name'] = stress_svcname_tmp + str(i)
		app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json)) 
		if "success" in json.loads(app_rtn)['status']:
			info('create application: %s successfully' % obj_json['name'])
		else:
			return False
			
	info('sleep 60 seconds')
	my_utils.bar_sleep(60)
			
	#get svc name
	svc_list = my_utils.get_sevice_by_app(ip,app_name)
	print "check_svc_status first time"
	#check app status
	times =1
	while times <= 10:
		rtn = my_utils.check_service_status(ip,svc_list)
		if times == 11:
			info('check 10 times done! have svc not running!tc-649 faied!')
			return False
		if rtn != True:
			info('this is %s times check,have svc not Running,sleep 60 try again'%times)
			my_utils.bar_sleep(60)
			times = times +1
		else:
			return True
			break
		
#main
rtn = run_test()
if rtn == True:
	my_utils.delete_all_app(ip)
	info('ok')
else:
	error('run test case ek-649 failed!')

	
