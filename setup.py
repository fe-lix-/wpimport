# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='wpimport',
    version='0.1',
    description='wpimport',
    classifiers=[],
    author='Félix Delval',
    author_email='felix@ravelsoft.com',
    url='',
    packages='wpimport',
    scripts=[
        'src/wpimport'
    ],
    install_requires=[
        'beautifulsoup',
    ],
    dependency_links=[
        'https://github.com/maxcutler/python-wordpress-xmlrpc/tarball/master#egg=wordpress_xmlrpc',
    ]
)
