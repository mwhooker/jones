
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
    jones.create_config('parent' , CONFIG['parent'])
    jones.create_config('parent/child1', CONFIG['child1'])
    jones.create_config('parent/child2', CONFIG['child2'])
    jones.create_config('parent/child1/subchild1', CONFIG['subchild1'])
    jones.assoc_host('127.0.0.1', 'parent')
    jones.assoc_host('127.0.0.2', 'parent/child1')

HOSTS = ('127.0.0.1', '127.0.0.2')
