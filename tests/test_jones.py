from __future__ import unicode_literals
from unittest import TestCase
import zc.zk
from zc.zk import testing

from jones import Jones


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


class TestJones(TestCase):

    def setUp(self):
        cs = 'zookeeper.example.com:2181'
        testing.setUp(self, connection_string=cs)
        self.zk = zc.zk.ZooKeeper(cs)

        self.jones = Jones('testservice', self.zk)

    def tearDown(self):
        testing.tearDown(self)

    def test_jones(self):

        self.jones.create_config(None, CONFIG['root'])
        self.jones.create_config('parent' , CONFIG['parent'])
        self.jones.create_config('parent/child1', CONFIG['child1'])
        self.jones.create_config('parent/child2', CONFIG['child2'])
        self.jones.create_config('parent/child1/subchild1', CONFIG['subchild1'])
        self.jones.assoc_ip('127.0.0.1', 'parent')
        self.jones.assoc_ip('127.0.0.2', 'parent/child1')
        #self.zk.print_tree('/services')

        child1 = {}
        for k in ('root', 'parent', 'child1'):
            child1.update(**CONFIG[k])
        self.assertEquals(child1, self.jones.get_config('127.0.0.2'))

    def test_overwrites(self):
        self.jones.create_config(None, {"foo": "bar"})
        self.jones.set_config(None, {"foo": "baz"}, -1)

        self.assertEquals(
            self.jones._get(self.jones.conf_path)['foo'],
            'baz'
        )

    """
    def test_conflicts(self):
        jones2 = Jones('testservice', self.zk)

        self.jones.set_config(None, {"foo": "bar"})
        jones2.set_config(None, {"foo": "baz"})
        print self.jones._get(self.jones.conf_path)['foo']
        print jones2._get(self.jones.conf_path)['foo']
    """



# TODO:
#   Test for MVCC
#
# Two race conditions
#   2 ppl access a node
#       one and then the other updates
#       The second to update clobbers the first update
