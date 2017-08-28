import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
stress_node_list = [{'name': 'stress1','vm':["EKOS-Offline-Stress-12","EKOS-Offline-Stress-13","EKOS-Offline-Stress-14"]},{'name': 'stress2','vm':["EKOS-Offline-Stress-17","EKOS-Offline-Stress-18","EKOS-Offline-Stress-19"]},{'name': 'stress3','vm':["EKOS-offline-darcy-62","EKOS-offline-darcy-63","EKOS-offline-darcy-64"]},{'name': 'stress4','vm':["EKOS-offline-Stress-10-84","EKOS-offline-Stress-10-85","EKOS-offline-Stress-10-86","EKOS-offline-Stress-10-87","EKOS-offline-Stress-10-88","EKOS-offline-Stress-10-89"]}]
ip = sys.argv[1]
testbed = sys.argv[2]
my_utils = ekosUtils.Utils()


def run_test():
	volume_prefix = "volume-"
	svc_prefix = "stress-nfs-"
	volume_number = 1
	svc_num = 5
	nfs_name = "darcy-nfs"

	#add nfs 
	nfs_server = "192.168.20.254"
	nfs_dir = "/mnt/nfs-share-1"
	rtn = my_utils.create_nfs_storage(ip,nfs_name,nfs_server,nfs_dir)
	if rtn == False:
		error('create nfs storage failed!')
		return False
	info('create nfs storage done')
	my_utils.bar_sleep(60)

	#check nfs
	rtn = my_utils.get_nfs_status(ip,nfs_name)
	info("nfs is in %s state" % rtn)
	if rtn != "ok":
		return False
	
	#create volumes 20Gi
	for i in range(volume_number):
		full_volume_name = volume_prefix + str(i)
		rtn = my_utils.create_nfs_volume(ip,nfs_name,full_volume_name,quantity="20Gi")
		if rtn == False:
			return False
	my_utils.bar_sleep(60)
	
	#create app	
	my_utils.create_app(ip,"stress-app")
	my_utils.bar_sleep(5)
	
	#create svc
	url = "http://" + ip + ":30000/service/stack/api/app" 
	#obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}]},"volumes":[],"desc":""}
	obj_json = {"name":"stress-test-2","namespace":"default","stack":"stress-app","stateful":"share","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"stress-test-4","image":"registry.ekos.local/library/stress_centos:latest","command":"sh","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}]},"volumes":[{"persistentVolumeClaim":{"claimName":"volume-test-2","mountPath":"/mnt/volume/","readOnly":False}}],"desc":""}

	volume_list = my_utils.get_nfs_volume_name(ip,nfs_name)
	svc_list = []
	
	for i in range(svc_num):
		obj_json['name'] = svc_prefix + str(i)
		svc_list.append(obj_json['name'])
		obj_json['volumes'][0]['persistentVolumeClaim']['claimName'] = full_volume_name
		rtn = my_utils.call_rest_api(url,"POST",json=json.dumps(obj_json))
		if "success" in json.loads(rtn)['status']:
			info('create application: %s successfully' % obj_json['name'])
		else:
			return False
	
	my_utils.bar_sleep(60)
	
	#check svc status
	rtn = my_utils.check_service_status(ip,svc_list)
	if rtn != True:
		return False
	
	#let runnning 30 min
	my_utils.bar_sleep(60)

	#check svc status
	rtn = my_utils.check_service_status(ip,svc_list)
	if rtn != True:
		return False
	nfs_list = my_utils.get_nfs_list(ip)
	rtn = my_utils.check_nfs_status(ip,nfs_list)
	if rtn != True:
		return False

	return True	

#main
rtn = run_test()
if rtn == True:
	my_utils.clean_testbed(ip)
	info('ok')
else:
	error('run test case ek-626 failed!')