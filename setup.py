"""setup.py file."""

import uuid

from setuptools import setup, find_packages
from pip.req import parse_requirements

__author__ = 'Michal Spiez <mspiez@gmail.com>'

# install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())
# reqs = [str(ir.req) for ir in install_reqs]

setup(
    name="network-automation-sros",
    version="0.1",
    packages=find_packages(),
    author="Michal Spiez",
    author_email="mspiez@gmail.com",
    description="Examples of automation networking tasks for Nokia routers",
    classifiers=[
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],
    url="https://github.com/mspiez/network-automation",
    include_package_data=True,
    install_requires=reqs,
)