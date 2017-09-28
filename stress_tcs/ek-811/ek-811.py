import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

ip = sys.argv[1]
svc_num = 2
app_num = 100
svcname_tmp = "stress-centos-"
appname_tmp = "stress-app-"
cookies = my_utils._get_cookie(ip)
svc_list = []

def run_test():
	#cr:eate stress-app
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
	my_utils.bar_sleep(60)
					
	#check svc status
	print "check_svc_status first time"	
        times = 1
        while times <= 11:
                rtn = my_utils.check_service_status(ip,svc_list)
                if times == 11:
			info('check 10 times done!have svc not running tc-811 faied!')
                        return False
                if rtn != True:
                        info("this is %s times check,please wait 60 seconds"%times)
                        my_utils.bar_sleep(60)
                        times=times+1
                else:
                        break

	info("let it runnning 600s")
	my_utils.bar_sleep(600)
	
	#check svc status
	print "check_svc_status second time"	
        times = 1
        while times <= 11:
                rtn = my_utils.check_service_status(ip,svc_list)
                if times == 11:
                        info('check 10 times done!have svc not running tc-811 faied!')
                        return False
                if rtn != True:
                        info("this is %s times check,please wait 60 seconds"%times)
                        my_utils.bar_sleep(60)
                        times=times+1
                else:
			return True
                        break
	
#main
rtn = run_test()
if rtn == True:
	my_utils.clean_testbed(ip)
	info('ok')
else:
	error('run test case ek-811 failed!')

	
