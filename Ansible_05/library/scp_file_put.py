#!/usr/bin/python

import os
import platform
from ansible.module_utils.basic import *

try:
    from SROSDriver import SROSDriver
except ImportError:
    module.fail_json(msg="Problem importing driver")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            host_ip=dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            source_file=dict(required=True,),
            dest_file=dict(required=True)
        )
    )

    host_ip = module.params['host_ip']
    username = module.params['username']
    password = module.params['password']
    source_file = module.params['source_file']
    dest_file = module.params['dest_file']
    # open device connection
    try:
        device = SROSDriver(hostname=host_ip,
                            username=username,
                            password=password
                            )
        device.open()
    except Exception, e:
        module.fail_json(msg="cannot connect to device: " + str(e))

    # send config to device
    try:
        scp_file_put = device.scp_file_put(source_file, dest_file)
    except Exception, e:
        scp_file_put = None
        module.fail_json(msg="Errors during file execution: " + str(e))

    try:
        device.close()
    except Exception, e:
        module.fail_json(msg="cannot close device connection: " + str(e))
        
    module.exit_json(msg='File sent to node')


if __name__ == '__main__':
    main()
