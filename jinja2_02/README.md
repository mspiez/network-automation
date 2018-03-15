# Jinja2 templates p2

One more example with additional parameters in R1.yaml file:

```
---
ports:
  - '1/1/1'
  - '1/1/2'
  - '1/1/3'
  - '1/1/4'

iface_names:
  - system
  - toR2
  - toR3
  - toR4

iface_parms:
  system:
    address: '10.10.10.1/32'
  toR2:
    desc: 'test description2'
    address: '10.10.12.1/24'
    port: '1/1/1:10'
  toR3:
    desc: 'test description3'
    address: '10.10.13.1/24'
    port: '1/1/2:10'
  toR4:
    desc: 'test description4'
    address: '10.10.14.1/24'
    port: '1/1/3:10'

lsp_names:
  - toR2
  - toR3
  - toR4

lsps:
  toR2:
    farend: '10.10.10.2'
  toR3:
    farend: '10.10.10.3'
  toR4:
    farend: '10.10.10.4'

sdp_ids:
  - 12
  - 13
  - 14

sdps:
  12:
    farend: '10.10.10.2'
    mpls: ldp
  13:
    farend: '10.10.10.3'
    mpls: ldp
  14:
    farend: '10.10.10.4'
    mpls: ldp
```

Some additional tmeplates are needed:

```
└─── templates
   ├── ifaces.j2
   ├── ldp.j2
   ├── mpls.j2
   ├── ospf.j2
   ├── ports.j2
   └── sdp.j2
```

Some refactoring in our python script, now called router.py:

```
import jinja2
import os
import sys
import yaml


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

def main():
    list_yamls = [x for x in os.listdir(os.getcwd()) if '.yaml' in x]
    for meta_file in list_yamls:
        cfg_file = '{}.cfg'.format(meta_file.split('.')[0])
        with open(meta_file) as f:
            router_parms = yaml.load(f)
        ports_temp = import_template('ports.j2')
        iface_temp = import_template('ifaces.j2')
        ospf_temp = import_template('ospf.j2')
        ldp_temp = import_template('ldp.j2')
        mpls_temp = import_template('mpls.j2')
        sdp_temp = import_template('sdp.j2')
        with open(cfg_file, 'a') as f:
            f.write(ports_temp.render(router_parms))
            f.write(iface_temp.render(router_parms))
            f.write(ospf_temp.render(router_parms))
            f.write(ldp_temp.render(router_parms))
            f.write(mpls_temp.render(router_parms))
            f.write(sdp_temp.render(router_parms))

def import_template(template_name):
    loader = jinja2.FileSystemLoader(TEMPLATES_DIR)
    jenv = jinja2.Environment(loader=loader)
    try:
        template = jenv.get_template('{}'.format(template_name))
    except Exception as f:
        print f
        sys.exit()
    else:
        return template


if __name__ == '__main__':
    main()
```

And we should be ready to generate more sophisticated config. Note that python script will grab all the ‘.yaml’ files in your current dir and will process it one by one. This means you can add multiple meta data files for different routers and still separate config files should be generated. You do not need to pass template name, because this step is now defined inside the python script. 
Let's run it against R1.yaml, as currently that is our only yaml in the directory:

```
python router.py
```

When script is completed without errors, new file should be created in the directory - R1.cfg. And the config should look like:

```
/configure port 1/1/1 ethernet mode hybrid
/configure port 1/1/1 ethernet encap-type dot1q
/configure port 1/1/1 ethernet mtu 9212
/configure port 1/1/1 no shutdown/configure port 1/1/2 ethernet mode hybrid
/configure port 1/1/2 ethernet encap-type dot1q
/configure port 1/1/2 ethernet mtu 9212
/configure port 1/1/2 no shutdown/configure port 1/1/3 ethernet mode hybrid
/configure port 1/1/3 ethernet encap-type dot1q
/configure port 1/1/3 ethernet mtu 9212
/configure port 1/1/3 no shutdown/configure port 1/1/4 ethernet mode hybrid
/configure port 1/1/4 ethernet encap-type dot1q
/configure port 1/1/4 ethernet mtu 9212
/configure port 1/1/4 no shutdown
/configure router interface "system" address 10.10.10.1/32
/configure router interface "toR2" address 10.10.12.1/24
/configure router interface "toR2" port 1/1/1:10
/configure router interface "toR2" description "test description2"
/configure router interface "toR3" address 10.10.13.1/24
/configure router interface "toR3" port 1/1/2:10
/configure router interface "toR3" description "test description3"
/configure router interface "toR4" address 10.10.14.1/24
/configure router interface "toR4" port 1/1/3:10
/configure router interface "toR4" description "test description4"
/configure router ospf traffic-engineering
/configure router ospf area 0 interface "system" interface-type point-to-point
/configure router ospf area 0 interface "system" no shutdown
/configure router ospf area 0 interface "toR2" interface-type point-to-point
/configure router ospf area 0 interface "toR2" no shutdown
/configure router ospf area 0 interface "toR3" interface-type point-to-point
/configure router ospf area 0 interface "toR3" no shutdown
/configure router ospf area 0 interface "toR4" interface-type point-to-point
/configure router ospf area 0 interface "toR4" no shutdown
/configure router ldp no shutdown
/configure router ldp interface-parameters interface "toR2"
/configure router ldp interface-parameters interface "toR3"
/configure router ldp interface-parameters interface "toR4"
/configure router mpls no shutdown
/configure router mpls path igp no shutdown
/configure router mpls interface "system" no shutdown
/configure router mpls interface "toR2" no shutdown
/configure router mpls interface "toR3" no shutdown
/configure router mpls interface "toR4" no shutdown
/configure router mpls lsp "toR4" no shutdown
/configure router mpls lsp "toR4" to 10.10.10.4
/configure router mpls lsp "toR4" primary "igp"
/configure router mpls lsp "toR3" no shutdown
/configure router mpls lsp "toR3" to 10.10.10.3
/configure router mpls lsp "toR3" primary "igp"
/configure router mpls lsp "toR2" no shutdown
/configure router mpls lsp "toR2" to 10.10.10.2
/configure router mpls lsp "toR2" primary "igp"
/configure service sdp 12 mpls create
/configure service sdp 12 ldp
/configure service sdp 12 farend 10.10.10.2
/configure service sdp 12 no shutdown
/configure service sdp 13 mpls create
/configure service sdp 13 ldp
/configure service sdp 13 farend 10.10.10.3
/configure service sdp 13 no shutdown
/configure service sdp 14 mpls create
/configure service sdp 14 ldp
/configure service sdp 14 farend 10.10.10.4
/configure service sdp 14 no shutdown
```

This example uses multiple templates to generate single config for R1, but you could combine templates into one file and still generate similar config based on parameters given in R1.yaml. 

When writing jinja2 templates take note of the 'dash' signs, like:

```
{% for port in ports -%}
.
..
{%- endfor %}
```

The purpose of those signs in templates is to remove blank lines, either before or after the section when config is generated. This way you will get 'clean' config without blank lines, but you may need to test the template several times, as it does not always work as expected.

[Back to network-automation main page](..)