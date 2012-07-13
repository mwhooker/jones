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
from __future__ import unicode_literals


# TODO: rewrite tests so we test everything
CONFIG = {
    'parent': {
        'a': 1,
        'b': [1, 2, 3],
        'c': {'x': 0}
    },
    'child1': {
        'a': 2
    },
    'child2': {
        'a': 3
    },
    'subchild1': {
        'b': "abc"
    },
    'root': {
        'foo': 'bar'
    }
}

CHILD1 = {}
for k in ('root', 'parent', 'child1'):
    CHILD1.update(**CONFIG[k])
PARENT = {}

for k in ('root', 'parent'):
    PARENT.update(**CONFIG[k])


ASSOCIATIONS = {
    '127.0.0.3' : '',
    '127.0.0.1' : 'parent',
    '127.0.0.2' : 'parent/child1'
}

def init_tree(jones):
    jones.create_config(None, CONFIG['root'])
    jones.create_config('parent', CONFIG['parent'])
    jones.create_config('parent/child1', CONFIG['child1'])
    jones.create_config('parent/child2', CONFIG['child2'])
    jones.create_config('parent/child2/subchild1', CONFIG['subchild1'])
    for host in ASSOCIATIONS:
        jones.assoc_host(host, ASSOCIATIONS[host])
