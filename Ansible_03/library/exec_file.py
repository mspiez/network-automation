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
            dest_file=dict(required=True)
        )
    )

    host_ip = module.params['host_ip']
    username = module.params['username']
    password = module.params['password']
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

    # retreive data from device
    try:
        file_exec = device.exec_file(dest_file)
    except Exception, e:
        file_exec = None
        module.fail_json(msg="Errors during file execution: " + str(e))

    try:
        device.close()
    except Exception, e:
        module.fail_json(msg="cannot close device connection: " + str(e))
    if file_exec != None:
        if 'Error' in file_exec or 'failed' in file_exec:
            module.fail_json(msg="Errors during file execution")
        elif 'Executed' in file_exec:
            module.exit_json(msg='File executed', changed=True)
        else:
            module.exit_json(msg='Not sure what has happened')


if __name__ == '__main__':
    main()
