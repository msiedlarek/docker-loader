# -*- coding: utf-8 -*-

import os
import codecs

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as readme:
    long_description = readme.read()


setup(
    name='docker-loader',
    version='0.1.0',
    description='Restriction-free, programmable Dockerfile alternative.',
    long_description=long_description,
    url='https://github.com/msiedlarek/docker-loader',
    author='Mikołaj Siedlarek',
    author_email='mikolaj@siedlarek.pl',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='docker-loader loader docker container image',
    install_requires=[
        'docker-py>=0.6.0',
        'six>=1.8.0',
    ],
    extras_require={
        'ansible': ['ansible >=1.9.0, <1.10.0'],
    },
    tests_require=[
        'nose',
    ],
    test_suite='nose.collector',
    packages=find_packages(exclude=['tests']),
    package_data={
        '': ['LICENSE'],
    },
    include_package_data=True
)
