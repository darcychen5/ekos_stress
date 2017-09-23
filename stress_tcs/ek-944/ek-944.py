import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
ip = sys.argv[1]
testbed = sys.argv[2]
my_utils = ekosUtils.Utils()


def run_test():
	app_prefix = "stress-"
	tenant_name_prefix = "tenant-"
	app_num_per_tenamt = 2
	tenant_num = 100
	username = 'darcytest'
	#add tenant
	# create a user
	project_id = my_utils.create_user(ip,username)

	for i in range(tenant_num):
		tenant_name = tenant_name_prefix + str(i)
		print tenant_name
		rtn = my_utils.add_tenant(ip,tenant_name,owner_id=project_id)
		if rtn != True:
			sys.exit()
		#create app
		app_stack_name = tenant_name
		my_utils.create_app(ip,app_stack_name,namespace=tenant_name)
		url = "http://" + ip + ":30000/service/stack/api/app" 
		obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}]},"volumes":[],"desc":""}
		for j in range(app_num_per_tenamt):
			obj_json['namespace'] = tenant_name
			obj_json['stack'] = app_stack_name
			obj_json['name'] = app_prefix + tenant_name + '-' + str(j)
			rtn = my_utils.call_rest_api(url,"POST",json=json.dumps(obj_json))
			if "success" in json.loads(rtn)['status']:
				info('create application: %s successfully' % obj_json['name'])
			else:
				return False
	
	my_utils.bar_sleep(300)
	
	#check app status
	tenant_list = my_utils.get_all_tenant_name(ip)
	tenant_list.remove('default')
	for tenant in tenant_list:
		service_list = my_utils.get_service_by_app(ip,tenant,namespace=tenant)
		rtn = my_utils.check_service_status(ip,service_list,namespace=tenant)
		if rtn != True:
			return False
	
	#let runnning 30 min
	my_utils.bar_sleep(1800)

	#check 
	for tenant in tenant_list:
		service_list = my_utils.get_service_by_app(ip,tenant,namespace=tenant)
		rtn = my_utils.check_service_status(ip,service_list,namespace=tenant)
		if rtn != True:
			return False
	
	#clean testbed
	my_utils.bar_sleep(60)
	rtn = my_utils.clean_testbed(ip)
	if rtn != True:
		return False
	return True

#main
rtn = run_test()
if rtn != True:
	error('execute TC ek-944 failed!')
	sys.exit()
else:
	#my_utils.clean_testbed(ip)
	info('ok')
