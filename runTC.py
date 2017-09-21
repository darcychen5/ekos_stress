import os,sys,time,ekosUtils,re,ConfigParser
from log import *

configfile = "/root/ekos_stress/install/config.ini"

my_utils = ekosUtils.Utils()

refresh_testbed = False
my_testbed = {}
if len(sys.argv) == 4:
	workdir = sys.argv[1]
	cycle_number = int(sys.argv[2])
	testbed = sys.argv[3]
elif len(sys.argv) == 5:
	workdir = sys.argv[1]
	cycle_number = int(sys.argv[2])
	testbed = sys.argv[3]
	refresh_testbed = sys.argv[4]
else:
	error('wrong args!')
	sys.exit()

conf = ConfigParser.ConfigParser()
conf.read(configfile)
testbed_list = conf.sections()
print testbed_list
if testbed not in testbed_list:
	error('no such testbed %s' % testbed)
	sys.exit()


testbed_name = testbed

#get master ip or vip
inventory_list = eval(my_utils._get_config(testbed_name,"inventory_list",configfile))
if "-" in inventory_list['master'] or "," in inventory_list['master']:
	master_ip = my_utils._get_config(testbed_name,"vip",configfile)
else:
	master_ip = inventory_list['master']

#refresh testbed
test_build = my_utils.get_latest_build()
if str(refresh_testbed) == "True" or str(refresh_testbed) == "true":
	info('refresh testbed!')
	cmd = "unbuffer python /root/ekos_stress/install/install_ekos.py " + testbed_name + " >/tmp/install.log"
	rtn = my_utils.runcmd(cmd)
	info(rtn)
	if rtn == False:
		sys.exit()
	my_utils.bar_sleep(300)

	#active plugin
	rtn = my_utils.active_plugin(master_ip)
	my_utils.bar_sleep(60)
	if rtn != True:
		error('active plugin failed')
		sys.exit()

#check if need upload stress img
cmd = "docker images |grep stress_centos"
rtn = my_utils.ssh_cmd(master_ip,"root","password",cmd)
if not rtn['stdout']:
	info('download and push images!')
	my_utils.download_upload_img(master_ip)

log_dir = "/var/log/"

test_result = {}
success_case_num = 0
failed_case_num = 0

for tc in os.listdir(workdir):

	flag = 0
	path = os.path.join(workdir, tc)
	tc_name = tc.split('.')[-2]
	test_result[tc_name] = {}
	logname = log_dir + tc_name + ".log"
	cmd = "unbuffer python " + path + " " + master_ip + " " + testbed_name + " >" + logname
	start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	for i in range(1, cycle_number + 1):
		my_utils.runcmd(cmd)
		f = open(logname,'r')
		try:
			f.seek(-7,2)
			line = f.read(2)
		except:
			error('file %s is empty' % logname)
			sys.exit()
		info(line)
		if re.search('ok',line):
			info('testcase: %s execute %d successfully' % (tc_name,i))
			my_utils.bar_sleep(300)
		else:
			info('testcase %s execute %d failed!' % (tc_name,i))
			flag = 1
			break
		my_utils.bar_sleep(60)

	end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	test_result[tc_name]['tc_id'] = tc_name
	test_result[tc_name]['start_time'] = start_time
	test_result[tc_name]['end_time'] = end_time
	if flag == 0:
		test_result[tc_name]['result'] = "success"
		success_case_num = success_case_num + 1
	else:
		test_result[tc_name]['result'] = "failed"
		failed_case_num = failed_case_num + 1


info(test_result)
all_content = "<h3>build: %s  </h3> \n test cycle: %d \n success: %d \n failed: %d \n testbed: %s \n <tr bgcolor=\"blue\" style=\"color:white\"><td>TC ID</td><td>Start Time</td><td>End Time</td><td>Result</td></tr>" % (test_build,cycle_number,success_case_num,failed_case_num,testbed)
for result in test_result.keys():
	if test_result[result]['result'] == 'failed':
		content = "<tr style=\"font-size:15px\"><td>%s</td><td>%s</td><td>%s</td><td ><font color=\"red\">%s</font></td></tr>\n" % (test_result[result]['tc_id'],test_result[result]['start_time'],test_result[result]['end_time'],test_result[result]['result'])
	else:
		content = "<tr style=\"font-size:15px\"><td>%s</td><td>%s</td><td>%s</td><td ><font color=\"green\">%s</font></td></tr>\n" % (test_result[result]['tc_id'],test_result[result]['start_time'],test_result[result]['end_time'],test_result[result]['result'])
	all_content = all_content + '\n' + content
html_content = "<table border=\"1\" cellpadding=\"2\" width=\"800\">" + all_content + "</table>"
cmd = "echo \"" + html_content + "\"" "| mail -s \"$(echo -e \"stress result\\nContent-Type: text/html;charset=gb2312\")\" chenlong@ghostcloud.cn fengqianjun@ghostcloud.cn helimeng@ghostcloud.cn lichengsong@ghostcloud.cn xiebin@ghostcloud.cn, zhufuchun@ghostcloud.cn wangmeng@ghostcloud.cn weijunxu@ghostcloud.cn lixu@ghostcloud.cn"
my_utils.runcmd(cmd)

