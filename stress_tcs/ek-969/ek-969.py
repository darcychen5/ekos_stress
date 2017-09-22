import sys,json,time,random,re
sys.path.insert(0, '/root/ekos_stress/')
import ekosUtils
from log import *
ip = sys.argv[1]
testbed = sys.argv[2]

my_utils = ekosUtils.Utils()

images_num = 100
images_list = []
app_name = "stress-app"

def run_test():
	#create app
	my_utils.create_app(ip,app_name)
	#check if need upload stress img
	cmd = "docker images |grep stress_centos"
	rtn = my_utils.ssh_cmd(ip,"root","password",cmd)
	if not rtn['stdout']:
		info('download and push images!')
		my_utils.download_upload_img(master_ip)

	for i in range(images_num):
		images_name = 'library/stress_centos-' + str(i)
		images_list.append(images_name)
		#check if exists
		all_list = my_utils.get_all_images(ip)
		if images_name not in all_list:
			#tag
			cmd = 'docker tag registry.ekos.local/library/stress_centos registry.ekos.local/' + images_name
			my_utils.ssh_cmd(ip,"root","password",cmd)

			#push
			cmd = 'docker push registry.ekos.local/' + images_name
			my_utils.ssh_cmd(ip,"root","password",cmd)

	
	#check if pushed
	all_list = my_utils.get_all_images(ip)
	print all_list
	for images in images_list:
		if images not in all_list:
			error('images %s upload failed!' % images)
			return False
		info('images %s upload successfully~' % images)

		if re.search('stress_centos',images):
			#create service
			obj_json = {"name":"stress-svc-ha-1","namespace":"default","stack":"stress-app","stateful":"none","	replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/stress_centos:latest","command":"","envs":[],"logDir":"","	healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[]	,"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}	]},"volumes":[],"desc":""}
			obj_json['containers'][0]['image'] = 'registry.ekos.local/' + images
			obj_json['name'] = "stress-centos-" + images.split('-')[-1]
			url = url = "http://" + ip + ":30000/service/stack/api/app"
			rtn = my_utils.call_rest_api(url,"POST",json=json.dumps(obj_json))


	my_utils.bar_sleep(300)
	#check all service
	service_list = my_utils.get_service_by_app(ip,app_name)
	rtn = my_utils.check_service_status(ip,service_list)
	if rtn != True:
		return False

	my_utils.bar_sleep(1800)

	#check all service again
	service_list = my_utils.get_service_by_app(ip,app_name)
	rtn = my_utils.check_service_status(ip,service_list)
	if rtn != True:
		return False

	my_utils.bar_sleep(10)
	#remove all images
	for images in images_list:
		if re.search('stress_centos',images):
			rtn = my_utils.delete_image(ip,images)
			if rtn != True:
				return False
	return True

#main
rtn = run_test()
if rtn != True:
	error('execute TC ek-969 failed!')
	sys.exit()
else:
	my_utils.clean_testbed(ip)
	info('ok')




		






	
