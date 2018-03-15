# Ansible part 5

### Config generation and sending it to the routers


Until now, we have sent configs to Nokia routers in parallel, but configs were generated in separate playbooks. Let's try to write playbook that based on our inventory file will generate config for proper node and then will send config and execute it on the router.

Within our playbook we will need separate play responsible for generating configs on localhost and separate play to send configs to the nodes. Sending configs is already covered in one of the previous playbooks(exec.yaml), but config generation with ‘template’ module requires some re-design, therefore in this case let's create a new play responsible for config generation. This time, for all routers available in the inventory file.

We need to loop through every host from inventory and perform common set of tasks. Import vars adequate for proper router (ex: R1.yaml), create config folder for proper router (ex: ../R1/), generate config for proper router (ex: R1.cfg). In our example we have only R1 and R2 in the inventory file, but in real production environments there will be many more. That is why we need to write playbook in a way that we can run it independently from number of our routers.

Ok, look at the playbook below:

```
---
-
  hosts: localhost
  gather_facts: False
  tasks:
    - name: Generates config for all hosts
      include_tasks: config_generator.yaml
      with_inventory_hostnames:
        - all
      loop_control:
        loop_var: outer_item

```

Above playbook will run on localhost, but look what happens during first task execution. The real tasks for the execution are included or we could say imported from separate file called config_generator.yaml. You can specify single task or multiple tasks over there. The important part to notice here is that the tasks written in config_generator.yaml will be executed against each host from our inventory file, even that playbook itself is run against localhost. Loop control allows us to pass variable - which is inventory_hostname - to the tasks included in the config_generation.yaml. This is important, as we will use hostname to create adequate directory for each host and save proper config to this directory. 

The tasks within config_generator.yaml:

```
---
- name: "Start of config generation for {{ outer_item }}"
  debug: 
    msg: "{{ outer_item }}"

- name: include vars
  include_vars: 
    file: "{{ outer_item }}.yaml"

- name: Creates directory
  file:
    path: "/path/to/files/network-automation/Ansible_05/tmp/{{ outer_item }}"
    state: directory
    
- name: Generate ospf configuration
  template: 
    src: "/path/to/files/network-automation/Ansible_05/templates/ospf.j2"
    dest: "/path/to/files/network-automation/Ansible_05/tmp/{{ outer_item }}/ospf.cfg"
  register: r3

- name: Generate file
  template: 
    src: "/path/to/files/network-automation/Ansible_05/templates/blank_file.j2"
    dest: "/path/to/files/network-automation/Ansible_05/configs/{{ outer_item }}.cfg"
  when:
    - r3|succeeded
  register: r7

- name: Merge config files
  assemble: 
    src: "/path/to/files/network-automation/Ansible_05/tmp/{{ outer_item }}/"
    dest: "/path/to/files/network-automation/Ansible_05/configs/{{ outer_item }}.cfg"
  when:
    - r7|succeeded
```

Variable {{ outer_item }} comes from our main playbook and it is passed here thanks to loop_var. It will be simply a hostname that will be used within the tasks. 
Let's start with R1 which is our first router in the inventory file and see what happens for each task:
- task 1 prints message "msg: R1"
- task 2 imports vars file: R1.yaml
- task 3 creates directory: "/path/to/files/network-automation/Ansible_05/tmp/R1/"
- task 4 generates ospf config to path: "/path/to/files/network-automation/Ansible_05/tmp/R1/ospf.cfg"
- task 5 generates blank file where all the configs can be merged (ports, ifaces, mpls, sdp... etc)
- task 6 assembles configs from path: "/path/to/files/network-automation/Ansible_05/tmp/R1/" to ../configs/R1.cfg

This set of tasks will be repeated for R2 adequately. 

All those tasks will guarantee config generation for each router that is defined in the inventory. 
If we want to send config straight a way to the nodes, we just need to copy exec.yaml functionality that you have seen before and paste in into our main playbook.

Now our playbook full_cfg_gen.yaml  has 2 plays and looks like this:

```
---
-
  hosts: localhost
  gather_facts: False
  tasks:
    - name: Generates config for all hosts
      include_tasks: config_generator.yaml
      with_inventory_hostnames:
        - all
      loop_control:
        loop_var: outer_item

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
      source_file: "/path/to/files/network-automation/Ansible_05/configs/{{ inventory_hostname }}.cfg"
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

The first play generates config, the second play sends and executes the config on the routers.
Note that first play runs against localhost only and second play runs against inventory hosts which is R1 and R2.

Result:

```
~/network-automation/Ansible_05$ ansible-playbook -i inventory full_cfg_gen.yaml 
                                                                                                                                                                 
PLAY [localhost] ******************************************************************************************************************************************************************************************************
                                                                                                                                                                 
TASK [Generates config for all hosts] ****************************************************************************************************************************************************************************
included: /path/to/files/network-automation/Ansible_05/config_generator.yaml for localhost                                                                         
included: /path/to/files/network-automation/Ansible_05/config_generator.yaml for localhost                                                                                                
                                                                                                                                                                                        
TASK [Start of config genration for "R1"] *****************************************************************************************************************************************************************************
ok: [localhost] => {                                                                                                                                                                    
    "msg": "R1"                                                                                                                                                                         
}                                                                                                                                                                                                                      
                                                                                                                                                                                                                       
TASK [include vars] ***************************************************************************************************************************************************************************************************
ok: [localhost]                                                                                                                                                                                                        
                                                                                                                                                                                                                       
TASK [Creates directory] **********************************************************************************************************************************************************************************************
ok: [localhost]                                                                                                                                                                                                        

TASK [Generate ospf configuration] ************************************************************************************************************************************************************************************
changed: [localhost]

TASK [Generate file] **************************************************************************************************************************************************************************************************
changed: [localhost]

TASK [Merge config files] *********************************************************************************************************************************************************************************************
changed: [localhost]

TASK [Start of config genration for "R2"] *****************************************************************************************************************************************************************************
ok: [localhost] => {
    "msg": "R2"
}

TASK [include vars] ***************************************************************************************************************************************************************************************************
ok: [localhost]

TASK [Creates directory] **********************************************************************************************************************************************************************************************
ok: [localhost]

TASK [Generate ospf configuration] ************************************************************************************************************************************************************************************
changed: [localhost]

TASK [Generate file] **************************************************************************************************************************************************************************************************
changed: [localhost]

TASK [Merge config files] *********************************************************************************************************************************************************************************************
changed: [localhost]

PLAY [inventory_test] *************************************************************************************************************************************************************************************************

TASK [Send config to Target node] *************************************************************************************************************************************************************************************
ok: [R1]
ok: [R2]

TASK [Verify if file with config exists on target node after uploading] ***********************************************************************************************************************************************
ok: [R1]
ok: [R2]

TASK [Execute file on target node] ************************************************************************************************************************************************************************************
changed: [R1]
changed: [R2]

PLAY RECAP ************************************************************************************************************************************************************************************************************
R1                         : ok=3    changed=1    unreachable=0    failed=0   
R2                         : ok=3    changed=1    unreachable=0    failed=0   
localhost                  : ok=14   changed=6    unreachable=0    failed=0 
```

This was nice! One playbook, 2 plays, many tasks and job done. If you need to introduce new router in the network just create new meta data file, add new router to the inventory and you are ready for deployment.

[Back to network-automation main page](/../../)