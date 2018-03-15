# Ansible part 4

### Ansible and template module. 

We have already used jinja2 templates, python scripts and meta data files written in yaml to generate config, but what if we could use Ansible to do the dirty work for us... There is a core module 'template', that serves such purpose. What is more when meta data file is included into the play, Ansible shall find all proper parameters from vars file and will join them with the correct parameters in the template.

Files structure required:
```
~/network-automation/Ansible_04$ tree
.
├── config_gen.yaml
├── configs
├── templates
│   └── ports.j2
└── vars
    └── R1.yaml
```
Obviously you may have different structure or much more files in your dirs, but that is the minimum you should have on your localhost to run the playbook.

We will use port.j2 template:

```
{% for port in ports %}
/configure port {{ port }} ethernet mode hybrid
/configure port {{ port }} ethernet encap-type dot1q
/configure port {{ port }} ethernet mtu 9212
/configure port {{ port }} no shutdown
{% endfor %}
```

... and the playbook itself looks like this:

```
#config_gen.yaml
---
-  
  hosts: localhost
  gather_facts: False
  connection: local
  tasks:
    - name: include vars
      include_vars: 
        file: R1.yaml

    - name: Generate port configuration
      template: 
        src: "/path/to/files/network-automation/Ansible_04/templates/ports.j2"
        dest: "/path/to/files/network-automation/Ansible_04/configs/ports.cfg"
```

This playbook does just 2 tasks:
1. import R1.yaml file where our vars are defined
2. generate config from template

! Don’t forget to change the path to your files - '/path/to/files/'!

Note that in our R1.yaml file, in addition to ports, there are also different parameters defined, but Ansible know how to join proper vars imported from file, with vars defined in jinja template.

When you run our playbook (without specifying inventory):

```
:~/network-automation/Ansible_04$ ansible-playbook config_gen.yaml 
 [WARNING]: Could not match supplied host pattern, ignoring: all

 [WARNING]: provided hosts list is empty, only localhost is available


PLAY [localhost] ***********************************************************************************************************************************************************************

TASK [include vars] ********************************************************************************************************************************************************************
ok: [localhost]

TASK [Generate port configuration] *****************************************************************************************************************************************************
changed: [localhost]

PLAY RECAP *****************************************************************************************************************************************************************************
localhost                  : ok=2    changed=1    unreachable=0    failed=0
```

You should see generated config in path specified in 'template' task:

```
~/network-automation/Ansible_04$ cat configs/ports.cfg 
/configure port 1/1/1 ethernet mode hybrid
/configure port 1/1/1 ethernet encap-type dot1q
/configure port 1/1/1 ethernet mtu 9212
/configure port 1/1/1 no shutdown
/configure port 1/1/2 ethernet mode hybrid
/configure port 1/1/2 ethernet encap-type dot1q
/configure port 1/1/2 ethernet mtu 9212
/configure port 1/1/2 no shutdown
/configure port 1/1/3 ethernet mode hybrid
/configure port 1/1/3 ethernet encap-type dot1q
/configure port 1/1/3 ethernet mtu 9212
/configure port 1/1/3 no shutdown
/configure port 1/1/4 ethernet mode hybrid
/configure port 1/1/4 ethernet encap-type dot1q
/configure port 1/1/4 ethernet mtu 9212
/configure port 1/1/4 no shutdown
```

We have generated port config only, but you can easily extend playbook with additional tasks pointing to different templates and then direct generated configs to separate files or to the same 'dest' file. You could also create one template and run full router config generation. There are couple of options to play with and I encourage you to do so.

For the basic cases, with Ansible, we don't need to create custom python scripts anymore. All we need to do is prepare routers meta data file and template. Ansible will do the rest for us.

[Back to network-automation main page](/../../)