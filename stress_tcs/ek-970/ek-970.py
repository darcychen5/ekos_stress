import sys,json,time,random,re
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
ip = sys.argv[1]
testbed = sys.argv[2]

my_utils = ekosUtils.Utils()

registry_num = 100
images_num_per_registry = 2
registry_name_prefix = "darcy"
registry_list = []
app_name = "stress-app"

def run_test():

	#create user
	project_id,password = my_utils.create_user(ip,'darcytest')
	debug('project id: %d' % project_id)
	debug('password %s' % password)
	#create app
	my_utils.create_app(ip,app_name)

	#check if need upload stress img
	cmd = "docker images |grep stress_centos"
	rtn = my_utils.ssh_cmd(ip,"root","password",cmd)
	if not rtn['stdout']:
		info('download and push images!')
		my_utils.download_upload_img(ip)

	for i in range(registry_num):
		#create registry
		registry_name = registry_name_prefix + str(i)
		registry_list.append(registry_name)
		rtn = my_utils.create_registry(ip,registry_name,owner_id=project_id)
		if rtn != True:
			return False

		#tag
		cmd = 'docker tag registry.ekos.local/library/stress_centos registry.ekos.local/' + registry_name + "/stress_centos"
		my_utils.ssh_cmd(ip,"root","password",cmd)
		#push scress img to the registry
		cmd = 'docker push registry.ekos.local/' + registry_name + '/stress_centos'
		my_utils.ssh_cmd(ip,"root","password",cmd)
		#check if pushed
		rtn = my_utils.get_regitry_id_by_name(ip,registry_name)
		if not rtn:
			error('img upload failed')
			return False
		#create service
		for j in range(images_num_per_registry):
			obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","	replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","	healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[]	,"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}	]},"volumes":[],"desc":""}
			obj_json['containers'][0]['image'] = 'registry.ekos.local/' + registry_name + "/stress_centos:latest"
			obj_json['name'] = "stress-centos-" + registry_name + str(j)
			url = url = "http://" + ip + ":30000/service/stack/api/app"
			rtn = my_utils.call_rest_api(url,"POST",json=json.dumps(obj_json))
	#sleep 300
	my_utils.bar_sleep(300)

	#check service
	service_list = my_utils.get_service_by_app(ip,app_name)
	rtn = my_utils.check_service_status(ip,service_list)
	if rtn != True:
		return False
	#sleep 1800
	my_utils.bar_sleep(1800)

	rtn = my_utils.check_node_ready(ip,'root','password')
	if rtn != True:
		return False

	rtn = my_utils.check_service_status(ip,service_list)
	if rtn != True:
		return False

	return True

#main
rtn = run_test()
if rtn != True:
	error('execute TC ek-970 failed!')
	sys.exit()
else:
	my_utils.clean_testbed(ip)
	info('ok')
