import os,sys,time,json
sys.path.insert(0, '/root/ekos_stress')
from log import *
import ekosUtils
my_utils = ekosUtils.Utils()
ip = sys.argv[1]
tenant_list = my_utils.get_all_tenant_name(ip)
tenant_list.remove('default')
print tenant_list
for tenant in tenant_list:
	service_list = my_utils.get_service_by_app(ip,tenant,namespace=tenant)
	rtn = my_utils.check_service_status(ip,service_list,namespace=tenant)