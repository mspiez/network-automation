# Ansible part 1

### First Custom Playbook

Straight to the point...
Below ours playbook called exec.yaml:

```
---
-  
  hosts: inventory_test
  gather_facts: False
  connection: local
  tasks:
  - name: Send config to Target node
    scp_file_put:
      host_ip: "{{ ansible_host }}"
      username: "{{ ansible_user }}"
      password: "{{ ansible_pass }}"
      source_file: "/path/to/files/network-automation/Ansible_03/configs/{{ inventory_hostname }}.cfg"
      dest_file: "cf3:/{{ inventory_hostname }}.cfg"

  - name: Verify if file with config exists on target node after uploading
    check_file_exists_after_scp_put:
      host_ip: "{{ ansible_host }}"
      username: "{{ ansible_user }}"
      password: "{{ ansible_pass }}"
      dest_file: "cf3:/{{ inventory_hostname }}.cfg"
    register: result

  - name: Execute file on target node
    exec_file:
      host_ip: "{{ ansible_host }}"
      username: "{{ ansible_user }}"
      password: "{{ ansible_pass }}"
      dest_file: "cf3:/{{ inventory_hostname }}.cfg"
    when:
      - result|succeeded
```

The goal of this playbook is to send config file to the node and execute it. Some basic check is also performed and if the check fails, then config execution on the node is not triggered - thanks to 'when' statement.

There are 3 tasks within the playbook and scp_file_put as well as exec_file corresponds to methods available in SROSDriver class seen in Ansible intro. The logic is hidden in python scripts however orchestration/management of the tasks sits in playbooks. Now we need to point, which task should talk to which method.

When you run above playbook, Ansible will try to find python script that corresponds to first task. The python script name is... 'scp_file_put' and it is kept in './library/' directory. So, there is a very clear relation between the Ansible task and proper python script.

scp_file_put.py 

```
cat library/scp_file_put.py

#!/usr/bin/python

import os
import platform
from ansible.module_utils.basic import AnsibleModule

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
    except Exception as f:
        module.fail_json(msg="cannot connect to device:{}".format(f))

    # send config to device
    try:
        scp_file_put = device.scp_file_put(source_file, dest_file)
    except Exception as f:
        scp_file_put = None
        module.fail_json(msg="Errors during file execution:{}".format(f))

    try:
        device.close()
    except Exception as f:
        module.fail_json(msg="cannot close device connection:{}".format(f))
        
    module.exit_json(msg='File sent to node')


if __name__ == '__main__':
    main()

```

Some short explanation what is happening here. Within our python script, we import Ansible module as well as SROSDriver. AnsibleModule is used to pass playbook vars from the task to the python script. In above example we need to pass host IP, username, password as well as source file and destination file names. We also create device object so that all SROSDriver methods are available to us.
When the playbook is run, variables (like host_ip) are passed to the python script and then we can perform different actions with our scripts - open connection to the router, get facts from router, send config file to the router, get config file from the router and any other logic we are willing to code in the script.

With above scp_file_put.py file, we have managed to glue together external python method (scp_file_put from SROSDriver) with playbook task. Same should be done for 2 other tasks in our playbook, but you can start with single task in playbook and see how it works.

As we have now created playbook and scripts, it's time to run it! Well not yet...
One last step is missing. We need to define the hosts that we want our playbook to be run against. The missing part is called inventory...

[Back to network-automation main page](./..)