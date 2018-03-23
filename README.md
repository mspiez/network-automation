# Network Automation for Nokia SROS

There are many tutorials on the web dedicated to network automation, therefore I decided to write another one.
Ok, not really... This is not a tutorial, as I don't want to go into the details about installation of some missing python libs or similar basics. I would like to show you though, the basics of network automation in relation to Nokia SROS. Both config generation as well as pushing the config to the router with Ansible. For network engineers it is difficult to get familiar with topics like Python, Ansible, Jinja2 and some others. Unfortunately, network automation requires conquering those aspects all together and that is main reason of presenting this combine knowledge.

If you don't know where to start or you are missing some pieces of the puzzle called network automation, you may find resources below really useful.


### [Jinja2 templates p1](./jinja2_01)

Basic interface config generation for Nokia SROS router with Jinja2, Python script and meta data file with router variables stored in YAML format.


### [Jinja2 templates p2](./jinja2_02)

Config generation for Nokia SROS router with Jinja2, Python script and meta data file with router variables stored in YAML format. (or multiple files to generated multiple router configs)


### [Ansible 00](./Ansible_00)

Intro. 
Before starting with Ansible, short explanation how to use Python to connect to the devices, get some info from the devices or push config to the devices. Napalm SROSDriver usage.


### [Ansible 01](./Ansible_01)

How to write Ansible playbooks that use custom modules.


### [Ansible 02](./Ansible_02)

Basics about inventory file.


### [Ansible 03](./Ansible_03)

Running playbook against Nokia routers.


### [Ansible 04](./Ansible_04)

Template module in Ansible. 
How to generate Nokia router config based on YAML file, Jinja2 template and Ansible.


### [Ansible 05](./Ansible_05)

Generating config files on localhost and sending it to the routers in single Ansible playbook. 


### [Nokia router's card auto-provisioning](./Stackstorm01)

Card auto-provisioning for Nokia SROS based on SYSLOG messages, Napalm-logs and Stackstorm. 