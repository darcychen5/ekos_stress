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
node_list = eval(my_utils._get_config(testbed,"node_name_list","/root/ekos_stress/install/config.ini")) 

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

	
        #get svc name
        svc_list = []
        for i in range(svc_num):
                svcname = stress_svcname_tmp + str(i)
                svc_list.append(svcname)

        #check svc status
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

	#create lb 
	rtn = my_utils.create_lb(ip,lb_name) 
	if rtn != True:
		sys.exit()
	#check lb status
	info('check lb status')
	times = 1
	while times <= 11:
		rtn = my_utils.check_lb_status(ip)
		if rtn != True:
			info('this is %s times check,lb status abnormal please wait 30 seconds will try again!'%times)
			my_utils.bar_sleep(30)
			times = times+1
		elif times == 11:
			info('check done...lb abnormal pleaase manule check it!!!')
			return False
		else:
			break
	#create_http rule for all service
	rtn = my_utils.add_http_rule_for_all_service(ip,lb_name)
	if rtn != True:
		return False  

	################################################check_app_status and check_lb_status########################################
	#get svc name
	svc_list = []
	for i in range(svc_num):
		svcname = stress_svcname_tmp + str(i)
		svc_list.append(svcname)

	#check svc status
	print"beginning check svc status after create http lb rule"	
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

	#check lb status
	print "beginning check lb after create lb http rule"
        times = 1
        while times <= 11:
                rtn = my_utils.check_lb_status(ip)
                if rtn != True:
                        info('this is %s times check,lb status abnormal please wait 30 seconds will try again!'%times)
                        my_utils_bar_sleep(30)
                        times = times+1
                elif times == 11:
                        info('check done...lb abnormal pleaase manule check it!!!')
                        return False
                else:
			return True
                        break

#main
rtn = run_test()
if rtn == True:
        my_utils.clean_testbed(ip)
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
                        error("have any pod not delete success,run test case ek-465 failed")
                else:
                        break
        cmd = "kubectl get po | grep " + lb_name + "| grep Running"
        times=1
        info("checking clean testbed status ! this is %s checking"%times)
        while times <= 11:
                rtn = my_utils.ssh_cmd(ip,"root","password",cmd)
                if rtn["stdout"] != "":
                        print "cleaning testbed not done... please wait 30 senconds will try again "
                        my_utils.bar_sleep(30)
                        times=times+1
                elif times == 11:
                        error("have any pod not delete success,run test case ek-465 failed")
                else:
                        info("ok")
                        break

else:
        error('run test case ek-465 failed!')

