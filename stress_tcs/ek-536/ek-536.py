import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
ip = sys.argv[1]
testbed = sys.argv[2]
stress_svcname_tmp = "powercycle-"
stress_appname_tmp = "powercycle-app-"
svc_num = 4
app_num = 50
my_utils = ekosUtils.Utils()
node_list = eval(my_utils._get_config(testbed,"node_name_list","/root/ekos_stress/install/config.ini"))
def run_test():
        #create stress_app
        cookies = my_utils._get_cookie(ip)
        for j in range(app_num):
            app_name = stress_appname_tmp + str(j)
            my_utils.create_app(ip,app_name)
            cookies = my_utils._get_cookie(ip)
            url = "http://" + ip + ":30000/service/stack/api/app"
            obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}]},"volumes":[],"desc":""}
            for i in range(svc_num):
                    obj_json['name'] = "stress" + str(j) + "-powercycle-" + str(i)
                    obj_json['stack'] = app_name
                    app_rtn = my_utils.call_rest_api(url,"POST",cookies=cookies,json=json.dumps(obj_json))
                    if "success" in json.loads(app_rtn)['status']:
                            info('create application: %s successfully' % obj_json['name'])
                    else:
                            return False

        info('sleep 600 seconds')
        my_utils.bar_sleep(600)

        #get app name
        app_list = my_utils.get_all_app(ip)
        #check app running
        for app in app_list:
            service_name = my_utils.get_service_by_app(ip,app)
            rtn = my_utils.check_service_status(ip,service_name)
            if rtn != True:
                return False

        #power off nodes sequentially
        for node in node_list:
                rtn = my_utils.poweroff_vm(node)
                if rtn != True:
                        error("power off node failed!")
                        return False
                my_utils.bar_sleep(10)

        info('power off node done,sleep 120 seconds')
        my_utils.bar_sleep(120)

                #power on all nodes

        for node in node_list:
                rtn = my_utils.poweron_vm(node)
                if rtn != True:
                        error('power on node failed')
                        return False

        info('Power on node done,sleep 10 minutes')
        my_utils.bar_sleep(800)

        #check node ready
        rtn = my_utils.check_node_ready(ip,"root","password")
        if rtn != True:
                return False

        print "check_app_status begining"

        rtn = my_utils._get_cookie(ip)
        #check app status
        for app in app_list:
            service_name = my_utils.get_service_by_app(ip,app)
            rtn = my_utils.check_service_status(ip,service_name)
            if rtn != True:
                return False
        return True
#clean testbed
#main
rtn = run_test()
if rtn == True:
        my_utils.clean_testbed(ip)
        info('ok')
else:
        error('run test case ek-536 failed!')
