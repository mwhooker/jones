"""
Copyright 2012 DISQUS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from setuptools import setup

VERSION = '0.5.1'
NAME = 'jones'

install_requires = [
    'kazoo>=0.6'
]

web_requires = install_requires + [
    'flask',
    'raven'
]

tests_require = web_requires + [
    'nose',
    'unittest2',
    'mock',
]

if __name__ == '__main__':
    setup(
        name=NAME,
        version=VERSION,
        author='Matthew Hooker',
        author_email='mwhooker@gmail.com',
        url='https://github.com/disqus/jones',
        description='Configuration frontend for Zookeeper.',
        license='Apache License 2.0',
        py_modules=['jones.client'],
        zip_safe=False,
        install_requires=install_requires,
        tests_require=tests_require,
        extras_require={
            'test': tests_require,
            'web': web_requires
        },
        test_suite='nose.collector',
        include_package_data=True,
    )
