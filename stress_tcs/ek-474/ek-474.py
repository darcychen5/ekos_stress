import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
ip = sys.argv[1]
my_utils = ekosUtils.Utils()

def run_test():
	app_stack_name = "stress-app"
	volume_prefix = "volume-"
	app_prefix = "stress-nfs-"
	volume_number = 200
	app_num = 200
	nfs_name = "darcy-nfs"

	#add nfs 
	nfs_server = "192.168.20.254"
	nfs_dir = "/mnt/nfs-share-2"
	rtn = my_utils.create_nfs_storage(ip,nfs_name,nfs_server,nfs_dir)
	if rtn == False:
		error('create nfs storage failed!')
		return False
	info('create nfs volume done')
	my_utils.bar_sleep(60)

	#check nfs
	rtn = my_utils.get_nfs_status(ip,nfs_name)
	info("nfs is in %s state" % rtn)
	if rtn != "ok":
		return False
	
	#create volumes
	for i in range(volume_number):
		full_volume_name = volume_prefix + str(i)
		rtn = my_utils.create_nfs_volume(ip,nfs_name,full_volume_name)
		if rtn == False:
			return False
	my_utils.bar_sleep(600)
	
	#create app
	my_utils.create_app(ip,app_stack_name)
	my_utils.bar_sleep(5)

	url = "http://" + ip + ":30000/service/stack/api/app" 
	obj_json = {"name":"stress-app-volume-1","namespace":"default","stack":"stress-app","stateful":"share","replicas":1,"cpu":125,"memory":128,"diskSize":20000,"scheduler":None,"containers":[{"name":"stress-c-1","image":"registry.ekos.local/library/stress_centos:latest","command":"","stdin":False,"tty":False,"envs":[],"healthCheck":None,"cfgFileMounts":[],"secretMounts":[],"hostMounts":[],"cpuPercent":100,"memPercent":100}],"service":{"ports":[{"containerPort":80,"servicePort":80,"protocol":"TCP"}]},"volumes":[{"persistentVolumeClaim":{"claimName":"volume-1","readOnly":False,"mountPath":"/mnt/volume/"}}],"desc":""}
	volume_list = my_utils.get_nfs_volume_name(ip,nfs_name)
	for volume in volume_list:
		obj_json['stack'] = app_stack_name
		obj_json['name'] = app_prefix + volume
		obj_json['volumes'][0]['persistentVolumeClaim']['claimName'] = volume
		rtn = my_utils.call_rest_api(url,"POST",json=json.dumps(obj_json))
		if "success" in json.loads(rtn)['status']:
			info('create application: %s successfully' % obj_json['name'])
		else:
			return False
	
	my_utils.bar_sleep(600)
	
	#check app status
	service_list = my_utils.get_service_by_app(ip,app_stack_name)
	rtn = my_utils.check_service_status(ip,service_list)
	if rtn != True:
		return False
	
	#let runnning 30 min
	my_utils.bar_sleep(1800)
	#check 
	rtn = my_utils.check_service_status(ip,service_list)
	if rtn != True:
		return False
	nfs_list = my_utils.get_nfs_list(ip)
	rtn = my_utils.check_nfs_status(ip,nfs_list)
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
	error('execute TC ek-474 failed!')
	sys.exit()
else:
	info('ok')
