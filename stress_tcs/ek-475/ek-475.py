import sys,json,time,random
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *

ip = sys.argv[1]
testbed = sys.argv[2]
my_utils = ekosUtils.Utils()
app_stack_name = "stress-app"
volume_prefix = "-volume-"
app_prefix = "hello-nfs-"
nfs_name_prefix = "darcy-nfs-"
nfs_dir_name_prefix = "/mnt/nfs-share-"
nfs_name_list = []
volume_number = 40
nfs_num = 5


def run_test():
	#add nfs 
	for i in range(nfs_num):
		nfs_server = "192.168.20.254"
		full_nfs_dir_name = nfs_dir_name_prefix + str(i+1)
		full_nfs_name = nfs_name_prefix + str(i+1)
		nfs_name_list.append(full_nfs_name)
		rtn = my_utils.create_nfs_storage(ip,full_nfs_name,nfs_server,full_nfs_dir_name)
		if rtn == False:
			error('create nfs storage failed!')
			sys.exit()
		info('create nfs volume done')
		my_utils.bar_sleep(40)

	print"check_nfs_status first time"   #nfs
	
	#check nfs 
	#nfs_list = my_utils.get_nfs_list(ip)
	rtn = my_utils.check_nfs_status(ip,nfs_name_list)
	if rtn != True:
		sys.exit()
	
	#create volume for each nfs
	print nfs_name_list
	for nfs_name in nfs_name_list:
		for i in range(volume_number):
			full_volume_name = nfs_name + volume_prefix + str(i) #volume name can't equal in each nfs
			rtn = my_utils.create_nfs_volume(ip,nfs_name,full_volume_name)
			if rtn == False:
				sys.exit()
		print"create volume for %s ok" % nfs_name
		my_utils.bar_sleep(5)

	#create app for each volume
	my_utils.create_app(ip,app_stack_name)
	my_utils.bar_sleep(5)
		
	url = "http://" + ip + ":30000/service/stack/api/app" 
	obj_json = {"name":"stress-test-2","namespace":"default","stack":app_stack_name,"stateful":"share","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"stress-test-4","image":"registry.ekos.local/library/hello:latest","command":"sh","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":88}]},"volumes":[{"persistentVolumeClaim":{"claimName":"volume-test-2","mountPath":"/mnt/volume/","readOnly":False}}],"desc":""}

	
	#create service
	app_list = []
	for nfs_name in nfs_name_list:
		volume_list = my_utils.get_nfs_volume_name(ip,nfs_name)
		for volume in volume_list:
			type(volume)
			obj_json['name'] = app_prefix + volume
			app_list.append(obj_json['name'])
			obj_json['volumes'][0]['persistentVolumeClaim']['claimName'] = volume
			rtn = my_utils.call_rest_api(url,"POST",json=json.dumps(obj_json))
			if "success" in json.loads(rtn)['status']:
				info('create application: %s successfully' % obj_json['name'])
			else:
				sys.exit()

	my_utils.bar_sleep(600)

	print"check_app_status first time"
	#check app status
	rtn = my_utils.check_service_status(ip,app_list)
	if rtn != True:
		sys.exit()


	print"check_app_status after runnning 30 min"
	#let runnning 30 min
	my_utils.bar_sleep(1800)

	print"check_nfs_status after runnning 30 min"
	#check app status
	rtn = my_utils.check_service_status(ip,app_list)
	if rtn != True:
		sys.exit()

	#check nfs status
	nfs_list = my_utils.get_nfs_list(ip)
	rtn = my_utils.check_service_status(ip,nfs_list)
	if rtn != True:
		sys.exit()
	return True

#main
rtn = run_test()
if rtn == True:
	my_utils.clean_testbed(ip)
	info('ok')
else:
	error('run test case ek-475 failed!')
