from __future__ import unicode_literals
from unittest import TestCase
import zc.zk
import zookeeper
from zc.zk import testing
from tests import fixture

from jones import Jones



class TestJones(TestCase):

    def setUp(self):
        cs = 'zookeeper.example.com:2181'
        testing.setUp(self, connection_string=cs)
        self.zk = zc.zk.ZooKeeper(cs)

        self.jones = Jones('testservice', self.zk)

    def tearDown(self):
        testing.tearDown(self)

    def test_jones(self):

        #self.zk.print_tree('/services')

        fixture.init_tree(self.jones)
        self.assertEquals(fixture.CHILD1, self.jones.get_config('127.0.0.2')[1])

    def test_overwrites(self):
        self.jones.create_config(None, {"foo": "bar"})
        self.jones.set_config(None, {"foo": "baz"}, -1)

        self.assertEquals(
            self.jones._get(self.jones.conf_path)[1]['foo'],
            'baz'
        )

    def test_parent_changed(self):
        fixture.init_tree(self.jones)
        self.jones.set_config('parent', {"new": "key"}, 0)
        _, config = self.jones.get_config('127.0.0.2')
        self.assertEquals(config['new'], 'key')

    def test_conflicts(self):

        self.jones.create_config(None, {"foo": "bar"})
        self.jones.set_config(None, {"foo": "baz"}, 0)

        self.assertEquals(
            self.jones._get(self.jones.conf_path)[1]['foo'],
            'baz'
        )

        self.assertRaises(
            zookeeper.BadVersionException,
            self.jones.set_config,
            None, {"foo": "bag"}, 4,
        )

    def test_conf_is_mapping(self):
        self.assertRaises(
            ValueError,
            self.jones.create_config,
            None, 'hello'
        )
