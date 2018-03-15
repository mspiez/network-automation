# Jinja2 templates p1

Let’s generate basic interface config for Nokia router. We need meta data file in yaml format with interface parameters, template written in jinja2 format and python script to feed the template. Could we store interface parameters in some other format? Yes, of course, however knowing yaml structure will become very useful in other network automation cases, so let’s stick to yaml format and create ifaces.yaml. Our file looks like this:
```
---
iface_names:
  - toR2
  - toR3
  - toR4

iface_parms:
  toR2:
    desc: 'test description2'
    address: '10.10.12.1/30'
    port: '1/1/1'
  toR3:
    desc: 'test description3'
    address: '10.10.13.1/30'
    port: '1/1/2'
  toR4:
    desc: 'test description4'
    address: '10.10.14.1/30'
    port: '1/1/3'  
```

There are two types of data structure in our example, iface_names and iface_parms. In python we would treat those ones as list and dictionary accordingly. Now, we want to use this data to generate config for our interfaces, so let’s create template called ifaces.j2. Save it in templates directory. Our template looks like:

```
{% for iface in iface_names -%}
/configure router interface "{{ iface }}" address {{ iface_parms[iface].address }}
/configure router interface "{{ iface }}" port {{ iface_parms[iface].port }}
/configure router interface "{{ iface }}" description "{{ iface_parms[iface].desc }}"
{% endfor %}
``` 

That is a plain template for interface configuration. You should have already noticed that we use the same var declarations as within our yaml file. There is a for loop through the list of interface names and next we get details about each interface thanks to dictionary in our meta data file. For now, details concerns interface address, port and description.


Most important piece though, will be our python script. How difficult can it be? Here goes example:

```
import jinja2
import os
import sys
import yaml


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')


def main(args):
	meta_file = args[1]
	template_file = args[2]
	loader = jinja2.FileSystemLoader(TEMPLATES_DIR)
	jenv = jinja2.Environment(loader=loader)
	template = jenv.get_template('{}'.format(template_file))
	try:
		with open('{}'.format(meta_file)) as f:
			iface_parms = yaml.load(f)
	except IOError as f:
		print f
		sys.exit()
	else:
		print template.render(iface_parms)

if __name__ == '__main__':
	main(sys.argv)
```

Let’s called it ifaces.py. The script expects meta data file as well as template file to be given as a arguments from cli. Meta data file should go first then template. After building some jinja environment we simply render the config and print it out.
Structure of our files and dirs looks like this:

```
~/network-automation/jinja2_01$ tree 
. 
├── ifaces.py 
├── ifaces.yaml 
└── templates 
   └── ifaces.j2 

1 directory, 3 files

```

To run our script, we just need to run:

```
~/network-automation/jinja2_01$ python ifaces.py ifaces.yaml ifaces.j2 
/configure router interface "toR2" address 10.10.12.1/30
/configure router interface "toR2" port 1/1/1
/configure router interface "toR2" description "test description2"
/configure router interface "toR3" address 10.10.13.1/30
/configure router interface "toR3" port 1/1/2
/configure router interface "toR3" description "test description3"
/configure router interface "toR4" address 10.10.14.1/30
/configure router interface "toR4" port 1/1/3
/configure router interface "toR4" description "test description4"
```

Note that script will find template directory and over there will search for file specified in cli. You don’t need to keep such directory structure but it is not recommended to give static paths and most probably as your project grows, you will need to keep templates separately from other files.

If you wish to save the generated config to file you can modify ifaces.py like so:

```
def main(args):
	meta_file = args[1]
	template_file = args[2]
	loader = jinja2.FileSystemLoader(TEMPLATES_DIR)
	jenv = jinja2.Environment(loader=loader)
	template = jenv.get_template('{}'.format(template_file))
	try:
		with open('{}'.format(meta_file)) as f:
			iface_parms = yaml.load(f)
	except IOError as f:
		print f
		sys.exit()
	else:
		try:
			cfg_file = '{}.cfg'.format(meta_file.split('.')[0])
			with open(cfg_file, 'w') as f:
				f.write(template.render(iface_parms))
		except Exception as f:
			print f
			sys.exit()
		else:
			print('File saved.')
``` 

and the result after running the script:

```
~/network-automation/jinja2_01$ python ifaces.py ifaces.yaml ifaces.j2 
File saved.
~/network-automation/jinja2_01$ tree 
. 
├── ifaces.cfg 
├── ifaces.py 
├── ifaces.yaml 
└── templates 
   └── ifaces.j2
~/network-automation/jinja2_01$ cat ifaces.cfg 
/configure router interface "toR2" address 10.10.12.1/30 
/configure router interface "toR2" port 1/1/1 
/configure router interface "toR2" description "test description2" 
/configure router interface "toR3" address 10.10.13.1/30
...
```

That is probably the most basic example, but it should give you a high-level view how you can use jinja2 templates with Python.

[Back to network-automation main page](/../../)