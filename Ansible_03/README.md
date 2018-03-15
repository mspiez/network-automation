# Ansible part 3

### Running our custom playbook

Finally, we can configure our nodes with Ansible. We have built our custom playbook exec.yaml, custom Ansible modules and inventory file. Let's add some simple config to R1.cfg and R2.cfg so that we can easily verify that configs are really pushed to the nodes.

R1.cfg:
```
/configure router interface "system" description "desc_R1"
```

R2.cfg:
```
/configure router interface "system" description "desc_R2"
```

Later on, we will try something more sophisticated. For now, this is just it.

You should download, clone or copy SROSDriver.py from my github page and make it available to your system. It means that when you open your python interpreter and do ...

```
from SROSDriver import SROSDriver
```

... you will import it without any errors and all the methods under SROSDriver will be available.

Other files required to run our custom playbook:
```
~/network-automation/Ansible_03$ tree
.
├── configs
│   ├── R1.cfg
│   └── R2.cfg
├── exec.yaml
├── inventory
├── library
│   ├── check_file_exists_after_scp_put.py
│   ├── exec_file.py
│   └── scp_file_put.py
└── README.md

2 directories, 8 files
```

Ok, time to run our playbook:

```
~/network-automation/Ansible_03$ ansible-playbook -i inventory exec.yaml
```

and the result:

```

PLAY [inventory_test] *******************************************************************************************************************************************

TASK [Send config to Target node] *******************************************************************************************************************************
ok: [R2]
ok: [R1]

TASK [Verify if file with config exists on target node after uploading] *****************************************************************************************
ok: [R1]
ok: [R2]

TASK [Execute file on target node] ******************************************************************************************************************************
changed: [R1]
changed: [R2]

PLAY RECAP ******************************************************************************************************************************************************
R1                         : ok=3    changed=1    unreachable=0    failed=0   
R2                         : ok=3    changed=1    unreachable=0    failed=0 
```

Let's verify from CLI:

```
*A:R1# show router interface "system" detail | match desc ignore-case 
Description      : desc_R1
*A:R1# logout

*A:R2# show router interface "system" detail | match desc ignore-case 
Description      : desc_R2
*A:R2#
```

Firstly, note that when running our playbook command, we have changed the default inventory by pointing Ansible towards our custom-made inventory file. Secondly, take a look how tasks were executed - one by one for the whole group of hosts, meaning, each task is executed in parallel.
Ok, that was nice, but let's try something else, even more interesting.

[Back to network-automation main page](/../../)