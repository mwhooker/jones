from __future__ import unicode_literals
from unittest import TestCase
import zc.zk
import zookeeper
import os.path
from zc.zk import testing

from tests import fixture
from jones import Jones
from jones.client import JonesClient


class TestJonesClient(TestCase):

    def setUp(self):
        self.config = None
        self.service = 'testservice'

        cs = 'zookeeper.example.com:2181'
        testing.setUp(self, connection_string=cs)
        self.zk = zc.zk.ZooKeeper(cs)

        """
        fixture_path = os.path.join(os.path.dirname(__file__), 'zktree.fixture')

        with open(fixture_path) as zkt:
            self.zk.import_tree(zkt.read())
        """

    def default_cb(self, config):
        self.config = config

    def tearDown(self):
        testing.tearDown(self)

    def test_gets_config(self):
        return
        jones = Jones(self.service, self.zk)
        fixture.init_tree(jones)
        
        c = JonesClient(self.service, self.zk, self.default_cb, '127.0.0.2')
        self.assertEquals(self.config, fixture.CHILD1)
        jones.set_config('parent', {'k': "I changed"}, -1)
        print self.config
