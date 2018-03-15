# Ansible intro

We will be developing custom modules in Ansible, so that you are not limited to functionality that sits in core modules only. Although Nokia SROS is not heavily supported, currently there are 3 modules you can use. However, let's focus on developing our own custom module. You should already get through jinja2 templating intro and that's good, as it may help you understand Ansible operational model. Ansible is a set of python libs that together with yaml files(playbooks) provides great way to execute tasks, that you would normally performed from CLI. 

Before starting with Ansible, let's have a quick look on prerequisites. Whether you plan to use NETCONF or SSH, reachability from your localhost to your devices needs to be set up - assuming localhost is the place where you have your ansible installed and this is the place you will run your playbooks from. Be sure you can ssh to your router before going further.

I will be using some of the functions/methods from SROSDriver, NAPALM project, so let's see how it works from python level.

As soon as I import SROSDriver within my python interpreter, I have access to methods delivered together with SROSDriver.
 
```
>>>
>>> from SROSDriver import SROSDriver
>>>
>>> my_functions = [x for x in dir(SROSDriver) if '__' not in x]
>>> for i in my_functions:
...     print i
...
_get_bgp_group_parms
_get_bgp_group_section
_get_bgp_neigh_detail
_get_bgp_neighbors_parms
_get_bgp_neighbors_section
_get_bgp_summary_section
_policy_search
_search_func
check_file_exists
check_free_space
close
command
delete_file
exec_file
get_arp_table
get_bgp_config
get_bgp_config_detail
get_bgp_neighbors
get_facts
get_interfaces
open
rollback_compare
rollback_save
rollback_view
scp_file_get
scp_file_put
```

If you want to use get_facts() method which simply gets some facts from Nokia router you can do:

```
>>> from SROSDriver import SROSDriver
>>> device = SROSDriver('10.10.10.1', 'admin', 'admin')
>>> device.open()
>>> get_facts = device.get_facts()
>>> print json.dumps(get_facts, indent=4)
{
    "os_version": "B-12.0.R10", 
    "uptime": "0 days, 00:08:45.05", 
    "vendor": "Nokia", 
    "interface": [
        "toR5", 
        "toR4", 
        "toR6", 
        "toR3", 
        "toR2", 
        "Gateway", 
        "system"
    ], 
    "serial_number": "vRR", 
    "model": "7750 SR-12", 
    "hostname": "R1", 
    "fqdn": "R1"
}
>>>
```

What about scp_file_put() method? Let's check our node first:

```
A:R1# file dir | match README
A:R1#
```

After that, let's run the method with proper source and destination:

```
>>> device.open()
>>> device.scp_file_put('README.md', 'README.md')
>>>

```

The result is:

```
A:R1# file dir | match README
03/07/2018  03:03p                  28 README.md
A:R1#
```

I will delete this file quickly as I really don't need README.md on my router.
The point here is, that I have just moved file README.md from my localhost to the node thanks to SCP/SSH, Paramiko and couple of lines written in Python. 
Our goal with Ansible, will be to move config files to the nodes (in parallel) and execute them on the node.


[Back to network-automation main page](/../../)