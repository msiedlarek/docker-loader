Docker Loader
*************

**Docker Loader is a Dockerfile alternative with arbitrary restrictions removed
and plenty of features added.**

Quick peek
==========

.. code-block:: python

   from docker_loader import *
   from docker_loader.provisioners import apt

   class Image(ImageDefinition):
       base = 'ubuntu:14.04'
       user = 'redis'
       command = ['/usr/bin/redis-server']
       exposed_ports = [
           (6379, 'tcp')
       ]
       provisioners = [
           apt.AptUpdate(),
           apt.AptInstall(['redis-server']),
       ]

   build(Image).tag('msiedlarek/redis').save('image.tar.gz', compress=True)

Development
===========

You can install package for development and testing with::

   virtualenv environment
   . environment/bin/activate
   pip install tox flake8 wheel
   pip install -e .

To run the test suite on supported Python versions use::

   tox

To only validate PEP8 compliance and run code static checking::

   tox -e flake8

To release::

   git tag -s -u gpgkey@example.com v0.1.0
   python setup.py register
   python setup.py sdist upload -s -i gpgkey@example.com
   python setup.py bdist_wheel upload -s -i gpgkey@example.com
   git push origin v0.1.0

License
=======

Copyright 2014 Mikołaj Siedlarek <mikolaj@siedlarek.pl>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this software except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
