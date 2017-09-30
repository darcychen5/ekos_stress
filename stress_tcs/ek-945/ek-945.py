import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
ip = sys.argv[1]
my_utils = ekosUtils.Utils()
svc_num = 200
app_stack_name = "stress-app"
svc_name_tmp = "stress-nginx-"
lb_name = "stress-nginx-lb"
httprule_port_tmp = 15000
def run_test():
	#create app
	cookies = my_utils._get_cookie(ip)
	rtn = my_utils.create_app(ip,app_stack_name)
	info("create app successful ! please wait 5 seconds")
	my_utils.bar_sleep(5)
	#create svc
	cookies = my_utils._get_cookie(ip)
	url = "http://" + ip + ":30000/service/stack/api/app"
	obj_json = {"name":"nginx","namespace":"default","stack":"aaaaa","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"scheduler":None,"containers":[{"name":"nginx","image":"registry.ekos.local/library/nginx:latest","command":"","stdin":False,"tty":False,"envs":[],"healthCheck":None,"cfgFileMounts":[],"secretMounts":[],"hostMounts":[],"cpuPercent":100,"memPercent":100}],"service":{"ports":[{"containerPort":80,"servicePort":80,"protocol":"TCP"}]},"volumes":[],"desc":""}
	for i in range(svc_num):
		svc_name = svc_name_tmp + str(i)
		obj_json['name'] = svc_name
		obj_json['stack'] = app_stack_name
		rtn = my_utils.call_rest_api(url,'POST',json=json.dumps(obj_json))
		if "success" in json.loads(rtn)['status']:
			info('create service %s successful'%obj_json['name'])
		else:
			return False

	#check nodes status
	rtn = my_utils.check_node_ready(ip,'root','password')
	if rtn != True:
		return False
	
	#get svc_list
	svc_list = my_utils.get_service_by_app(ip,app_stack_name)
	#check svc status
        print "check_service_status"
        times = 1
        while times <= 11:
                rtn = my_utils.check_service_status(ip,svc_list)
                if times == 11:
                        return False

                elif rtn != True:
                        info("this is %s times check,have pods not Running please wait 60 seconds will try again"%times)
                        my_utils.bar_sleep(60)
                        times=times+1
                else:
                        break
	#create lb
	rtn = my_utils.create_lb(ip,lb_name)
	if rtn != True:
		return False
	info('craete lb successful!sleep 5 seconds')
	my_utils.bar_sleep(5)
	#check lb status
	info('check lb status')
        times = 1
        while times <= 11:
                rtn = my_utils.check_lb_status(ip)
                if times == 11:
                        info('check done...lb abnormal pleaase manule check it!!!')
                        return False
                elif rtn != True:
                        info('this is %s times check,lb status abnormal please wait 60 seconds will try again!'%times)
                        my_utils.bar_sleep(60)
                        times = times+1
                else:
                        break
        #create_http rule for all service
        rtn = my_utils.add_http_rule_for_all_service(ip,lb_name)
        if rtn != True:
                return False


        #add stress
        lb_hostip = my_utils.get_lb_hostip(ip,lb_name)
        for i in range(10):
                port = random.randint(httprule_port_tmp,httprule_port_tmp+svc_num)
                cmd = 'ab -c 1000 -n 5000 http://%s:%s/' % (lb_hostip[0],str(port))
                my_utils.runcmd(cmd)


        ################################################check_app_status and check_lb_status########################################
        
	#check svc status
        print"beginning check svc status after add stress"
        times = 1
        while times <= 11:
                rtn = my_utils.check_service_status(ip,svc_list)
                if times == 11:
                        return False
                elif rtn != True:
                        info("this is %s times check,have pods not Running please wait 60 seconds will try again"%times)
                        my_utils.bar_sleep(60)
                        times=times+1
                else:
                        break

        #check lb status
        print "beginning check lb after add stress"
        times = 1
        while times <= 11:
                rtn = my_utils.check_lb_status(ip)
                if times == 11:
                        info('check done...lb abnormal pleaase manule check it!!!')
                        return False
                elif rtn != True:
                        info('this is %s times check,lb status abnormal please wait 30 seconds will try again!'%times)
                        my_utils_bar_sleep(30)
                        times = times+1
                else:
                        return True
                        break
#main
rtn = run_test()
if rtn == True:
	my_utils.clean_testbed(ip)
	info('ok')
else:
	error('run test case ek-945 failed')

