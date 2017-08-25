import os,sys,time,json
sys.path.insert(0, '/root/ekos_stress')
from log import *
import ekosUtils
my_utils = ekosUtils.Utils()
ip = sys.argv[1]

# app_name = "stress_app_ha_1"
# cookies = my_utils._get_cookie(ip)
# my_utils.create_app(ip,app_name)

# info('sleep 10 seconds')
# my_utils.bar_sleep(10)

obj_json = {"name":"test-hello-5","namespace":"default","stack":"stress_app_ha_1","stateful":"none","replicas":1,"cpu":125,"memory":64,"diskSize":20000,"containers":[{"name":"hello-test-4","image":"registry.ekos.local/library/hello:latest","command":"","envs":[],"logDir":"","healthCheck":None,"cpuPercent":100,"memPercent":100,"stdin":False,"tty":False,"cfgFileMounts":[],"secretMounts":[]}],"service":{"ports":[{"protocol":"TCP","containerPort":88,"servicePort":888}]},"volumes":[],"desc":""}
url = "http://" + ip + ":30000/service/stack/api/app"
rtn = my_utils.call_rest_api(url,"POST",json=json.dumps(obj_json))
info(rtn)