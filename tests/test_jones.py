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
import json
import zc.zk
import zookeeper

from tests import fixture
from unittest import TestCase
from zc.zk import testing

from jones import Jones


class TestJones(TestCase):

    def setUp(self):
        cs = 'zookeeper.example.com:2181'
        testing.setUp(self, connection_string=cs)
        self.zk = zc.zk.ZooKeeper(cs)

        self.jones = Jones('testservice', self.zk)

    def tearDown(self):
        testing.tearDown(self)

    def test_creates_root(self):

        fixt = {'xy': 'z'}
        self.jones.create_config(None, fixt)
        self.assertEquals(
            json.loads(self.zk.get(self.jones.view_path)[0]),
            fixt
        )

    def test_jones(self):

        fixture.init_tree(self.jones)
        self.assertEquals(
            fixture.CHILD1,
            self.jones.get_config('127.0.0.2')[1]
        )

    def test_overwrites(self):
        self.jones.create_config(None, {"foo": "bar"})
        self.jones.set_config(None, {"foo": "baz"}, -1)

        self.assertEquals(
            self.jones._get(self.jones.conf_path)[1]['foo'],
            'baz'
        )

    def test_parent_changed(self):
        fixture.init_tree(self.jones)
        parent = dict(fixture.CONFIG['parent'])
        parent['new'] = 'key'
        self.jones.set_config('parent', parent, 0)
        #self.zk.print_tree('/services')

        for i in fixture.HOSTS:
            _, config = self.jones.get_config(i)
            self.assertEquals(config.get('b'), [1, 2, 3],
                             "Host %s didn't inherit properly." % i)
            self.assertEquals(config.get('new'), 'key',
                              "Host %s not updated." % i)

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
