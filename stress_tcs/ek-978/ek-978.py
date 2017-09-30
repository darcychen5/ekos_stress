import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
ip = sys.argv[1]
my_utils = ekosUtils.Utils()
app1_name = "stress-nginx"
app2_name = "stress-stress"
svc_num = 100
lb_name = "stress-nginx-lb"
nginx_svc_list = []
stress_svc_list = []
httprule_port_tmp = 15000

def run_test():
	#create nginx app
	cookies = my_utils._get_cookie(ip)
	rtn = my_utils.create_app(ip,app1_name)
	if rtn != True:
		return False
	else:
		info('create app succeessfully!sleep 5s')
		my_utils.bar_sleep(5)
	
	#create  nginx_svc
	cookies = my_utils._get_cookie(ip)
	url = "http://" + ip + ":30000/service/stack/api/app"
	obj_json = {"name":"nginx","namespace":"default","stack":"aaaaa","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"scheduler":None,"containers":[{"name":"nginx","image":"registry.ekos.local/library/nginx:latest","command":"","stdin":False,"tty":False,"envs":[],"healthCheck":None,"cfgFileMounts":[],"secretMounts":[],"hostMounts":[],"cpuPercent":100,"memPercent":100}],"service":{"ports":[{"containerPort":80,"servicePort":80,"protocol":"TCP"}]},"volumes":[],"desc":""}
	for i in range(svc_num):
		nginx_svc_name = app1_name + '-svc-' + str(i)
		obj_json['name'] = nginx_svc_name
		obj_json['stack'] = app1_name
		rtn = my_utils.call_rest_api(url,'POST',json=json.dumps(obj_json))
                if "success" in json.loads(rtn)['status']:
                        info('create service %s successful'%obj_json['name'])
                else:
                        return False
	info('create nginx_svc done!sleep 60s will check svc status!')
	my_utils.bar_sleep(60)
	
	#check node ready
	rtn = my_utils.check_node_ready(ip,'root','password')
        if rtn != True:
                return False	

        #get svc_list
        nginx_svc_list = my_utils.get_service_by_app(ip,app1_name)

        #check nginx svc status
	info('check nginx svc status')
        times = 1
        while  True:
                rtn = my_utils.check_service_status(ip,nginx_svc_list)
                if times == 11:
			info('check 10 times done! have svc not running faied!')
                        return False
                elif rtn != True:
                        info("this is %s times check,have pods not Running please wait 60 seconds will try again"%times)
                        my_utils.bar_sleep(60)
                        times = times + 1
                else:
                        break
	#create stress app
        cookies = my_utils._get_cookie(ip)
        rtn = my_utils.create_app(ip,app2_name)
        if rtn != True:
                return False
        else:
                info('create app succeessfully!sleep 5s')
                my_utils.bar_sleep(5)

	#create stress_svc
        cookies = my_utils._get_cookie(ip)
        url = "http://" + ip + ":30000/service/stack/api/app"
        obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/stress_centos:latest","command":"stress -c 1","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}]},"volumes":[],"desc":""}
        for i in range(svc_num):
		stress_svc_name = app2_name + '-svc-' + str(i)
                obj_json['name'] = stress_svc_name
		obj_json['stack'] = app2_name 
                rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json))
                if "success" in json.loads(rtn)['status']:
                        info('create application: %s successfully' %obj_json['name'])
                else:
                        return False
	#get svc list for stress_svc
	stress_svc_list = my_utils.get_service_by_app(ip,app2_name)
	#check stess_svc status
        times = 1
        while  True:
                rtn = my_utils.check_service_status(ip,stress_svc_list)
                if times == 11:
                        info('check 10 times done! have svc not running faied!')
                        return False
                elif rtn != True:
                        info("this is %s times check,have pods not Running please wait 60 seconds will try again"%times)
                        my_utils.bar_sleep(60)
                        times = times + 1
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
        while True:
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
        rtn = my_utils.add_http_rule_per_app(ip,lb_name,app1_name)
        if rtn != True:
                return False

        #add stress
        lb_hostip = my_utils.get_lb_hostip(ip,lb_name)
	for i in range(20):
        	for port in range(httprule_port_tmp,httprule_port_tmp+svc_num):
                	cmd = 'ab -c 1000 -n 5000 http://%s'%lb_hostip[0] + ':' + str(port)+'/'
                	my_utils.runcmd(cmd)

	#check svc and lb again
	info('check svc and lb after add stress')
        #check svc status
        times = 1
        while  True:
                rtn = my_utils.check_service_status(ip,nginx_svc_list)
                if times == 11:
			info('after add stress check 10 times done! have svc not running!faied!')
                        return False
                elif rtn != True:
                        info("after add stress this is %s times check,have pods not Running please wait 60 seconds will try again"%times)
                        my_utils.bar_sleep(60)
                        times = times + 1
                else:
                        break

        #check lb status
        info('check lb status after add stress')
        times = 1
        while True:
                rtn = my_utils.check_lb_status(ip)
                if times == 11:
                        info('after add stress check done...lb abnormal pleaase manule check it!!!')
                        return False
                elif rtn != True:
                        info('after add stress this is %s times check,lb status abnormal please wait 60 seconds will try again!'%times)
                        my_utils.bar_sleep(60)
                        times = times+1
                else:
       	                break
#=================================================let all svc sleep 30min===========================================================================================
	my_utils.bar_sleep(1800)
        #check lb status
        info('check lb status after add sleep 30min')
        times = 1
        while True:
                rtn = my_utils.check_lb_status(ip)
                if times == 11:
                        info('after sleep 30min check done...lb abnormal pleaase manule check it!!!')
                        return False
                elif rtn != True:
                        info('after sleep 30min this is %s times check,lb status abnormal please wait 60 seconds will try again!'%times)
                        my_utils.bar_sleep(60)
                        times = times+1
                else:
                        break

	#check nginx_svc status 
        times = 1
        while  True:
                rtn = my_utils.check_service_status(ip,nginx_svc_list)
                if times == 11:
                        info('after sleep 30min check 10 times done! have svc not running!faied!')
                        return False
                elif rtn != True:
                        info("after sleep 30min this is %s times check,have pods not Running please wait 60 seconds will try again"%times)
                        my_utils.bar_sleep(60)
                        times = times + 1
                else:
                        break

        #check stress_svc status
        times = 1
        while  True:
                rtn = my_utils.check_service_status(ip,stress_svc_list)
                if times == 11:
                        info('after sleep 30min check 10 times done! have svc not running!faied!')
                        return False
                elif rtn != True:
                        info("after sleep 30min this is %s times check,have pods not Running please wait 60 seconds will try again"%times)
                        my_utils.bar_sleep(60)
                        times = times + 1
                else:
			return True
                        break

	
#main
rtn = run_test()
if rtn != True:
	error('run ek-978 faied')
else:
	my_utils.clean_testbed(ip)
	info('ok')
