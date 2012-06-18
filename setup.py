#!/usr/bin/env python

from distutils.core import setup

setup(name='bu-xmlgateway',
      version='1.0.2',
      description='Bu XmlGateway Python version',
      author='Michael Shulman',
      packages=['bu-xmlgateway',],
      package_dir={'bu-xmlgateway': 'bu-xmlgateway'},
      package_data={'bu-xmlgateway': ['request.xmt']}
     )
