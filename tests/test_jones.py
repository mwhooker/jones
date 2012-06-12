from unittest import TestCase
import zc.zk
from zc.zk import zookeeper

from jones import Jones

TREE = """/config
    /testservice
    127.0.0.1 -> /configtestservice//parent
    127.0.0.2 -> /config/testservice/parent/child
    /parent
        /child"""


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
}


class TestJones(TestCase):

    def setUp(self):
        self.zk = zc.zk.ZooKeeper('localhost:2181')

        try:
            self.zk.delete_recursive('/services')
        except zookeeper.NoNodeException:
            pass

        self.jones = Jones('testservice', self.zk)

    def test_x(self):

        self.jones.set_config('/', {'foo': 'bar'})
        self.jones.set_config('/parent' , CONFIG['parent'])
        self.jones.set_config('/parent/child1', CONFIG['child1'])
        self.jones.set_config('/parent/child2', CONFIG['child2'])
        self.jones.set_config('/parent/child1/subchild1', CONFIG['subchild1'])
        self.jones.assoc_ip('127.0.0.1', '/parent')
        self.jones.assoc_ip('127.0.0.2', '/parent/child')
        self.zk.print_tree('/services')
