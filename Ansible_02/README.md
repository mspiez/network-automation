# Ansible part 2

### Inventory file

First of all, inventory file does not have to be a file... :)
It can be a python script, which is very cool option but in our example, we will use a flat file. In the inventory you can define not only host information, but also variables that will be used within playbook. 

Step by step...

First, we need to have list of our nodes that we will be pushing the config to. For now, it's R1 and R2. If you look at our playbook exec.yaml, you should notice that we have some variables over there that we need to pass. Variables are specified like so: '{{ item }}'. Then those parameters are used by python scripts, for example to open connection to the node or get facts from the node.

Let's put some of the variables from our playbook into our inventory file called... inventory:

```
[inventory_test]
R1 ansible_host=10.10.10.1 ansible_user=admin ansible_pass=admin
R2 ansible_host=10.10.10.2 ansible_user=admin ansible_pass=admin
```

If you are worried about password kept in our flat file you maybe interested in Ansible Vault.
According to the Ansible docs:
'New in Ansible 1.5, “Vault” is a feature of ansible that allows keeping sensitive data such as passwords or keys in encrypted files, rather than as plaintext in your playbooks or roles.'

In our inventory there is one group called inventory_test and at the beginning of our playbook exec.yaml, we have also defined hosts as:

```
-
 hosts: inventory_test
```

Those two names must match, as playbook will be run only against hosts matching the group. You can split your hosts into different groups and run playbooks against only particular group. For example, you may want to split routers into the groups based on function (core, aggregation, access), type, software version, or geographical location.

We will keep things simple though - one group inventory_test.

We haven't defined source/destination file variables that we will be sending to our nodes. But do we really need to do that? Not really... We just need to be sure, that all config we want to send to the node is saved in R1.cfg file (for R1) and is placed in proper path according to the playbook:

```
source_file: /path/to/your/config/file/{{ inventory_hostname }}.cfg
```

The inventory_hostname var used in the tasks, allows Ansible not only find the config on the local disk but also to send R1.cfg to R1, R2.cfg to R2 and so on... 

Now, we have our last piece that was missing and we can run our playbook.

[Back to network-automation main page](/../../)
