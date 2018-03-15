import jinja2
import os
import sys
import yaml


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')


# def main(args):
# 	meta_file = args[1]
# 	template_file = args[2]
# 	loader = jinja2.FileSystemLoader(TEMPLATES_DIR)
# 	jenv = jinja2.Environment(loader=loader)
# 	template = jenv.get_template('{}'.format(template_file))
# 	try:
# 		with open('{}'.format(meta_file)) as f:
# 			iface_parms = yaml.load(f)
# 	except IOError as f:
# 		print f
# 		sys.exit()
# 	else:
# 		print template.render(iface_parms)

# if __name__ == '__main__':
# 	main(sys.argv)




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

if __name__ == '__main__':
	main(sys.argv)







