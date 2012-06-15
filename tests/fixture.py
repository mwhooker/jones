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


def init_tree(jones):
    jones.create_config(None, CONFIG['root'])
    jones.create_config('parent', CONFIG['parent'])
    jones.create_config('parent/child1', CONFIG['child1'])
    jones.create_config('parent/child2', CONFIG['child2'])
    jones.create_config('parent/child1/subchild1', CONFIG['subchild1'])
    jones.assoc_host('127.0.0.1', 'parent')
    jones.assoc_host('127.0.0.2', 'parent/child1')


HOSTS = ('127.0.0.1', '127.0.0.2')
