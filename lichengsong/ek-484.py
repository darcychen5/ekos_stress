import sys,json,time,random
sys.path.insert(0, '/root/ekos_auto/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

ip = sys.argv[1]
#testbed = sys.argv[2]

#add 10 node

#cookies = my_utils._get_cookie(ip)
url = "http://" + ip + ":30000/service/node/api/node/install"                                
obj_json = {"auth_type":"username_password","ssh_username":"root","ssh_password":"password","ssh_key":"","node_ip":["192.168.10.154"]}
obj_json['node_ip'] = ["192.168.10.155","192.168.10.156"]
node_rtn = my_utils.call_rest_api(url,"POST",json=json.dumps(obj_json)) 
print node_rtn

if "ok" in json.loads(node_rtn)['result']:
	info('add node: %s successfully' % obj_json['node_ip']) 
else:
	sys.exit()

		
info('sleep 120 seconds')
my_utils.bar_sleep(120) 