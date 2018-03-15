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







