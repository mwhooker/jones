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
from unittest import TestCase
import zc.zk
from zc.zk import testing

from tests import fixture
from jones import Jones
from jones.client import JonesClient


class TestJonesClient(TestCase):

    def setUp(self):
        self.config = None
        self.service = 'testservice'
        self.hostname = '127.0.0.2'

        cs = 'zookeeper.example.com:2181'
        testing.setUp(self, connection_string=cs)
        self.zk = zc.zk.ZooKeeper(cs)
        self.jones = Jones(self.service, self.zk)
        fixture.init_tree(self.jones)
        self.client = JonesClient(self.service, self.zk, self.default_cb,
                                  self.hostname)

    def default_cb(self, config):
        self.config = config

    def tearDown(self):
        testing.tearDown(self)

    def test_gets_config(self):

        self.assertEquals(self.config, fixture.CHILD1)
        fixt = "I changed"
        self.jones.set_config('parent', {'k': fixt}, -1)
        self.assertEquals(self.config['k'], fixt)

    def test_responds_to_remap(self):
        """test that changing the associations updates config properly."""

        self.jones.assoc_host(self.hostname, 'parent')
        self.assertEquals(self.config, fixture.PARENT)

    def test_defaults_to_root(self):
        """
        If a hostname doesn't map to anything,
        make sure to default to the root.
        That way we don't have to add every
        host under our control to zk.
        """

        hostname = '0.0.0.0'
        self.client = JonesClient(self.service, self.zk,
                             self.default_cb, hostname)
        self.assertTrue(hostname not in fixture.HOST_TO_VIEW)
        self.assertEquals(self.config, fixture.CONFIG['root'])
        self.jones.assoc_host(hostname, 'parent')
        self.assertEquals(self.config, fixture.PARENT)
