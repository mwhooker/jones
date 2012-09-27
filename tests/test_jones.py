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

from kazoo.exceptions import BadVersionException, NoNodeException
from kazoo.testing.harness import KazooTestCase
from tests import fixture

from jones.jones import Jones


class TestJones(KazooTestCase):

    def setUp(self):
        super(TestJones, self).setUp()

        self.jones = Jones('testservice', self.client)

    def test_creates_root(self):

        fixt = {'xy': 'z'}
        self.jones.create_config(None, fixt)
        self.assertEquals(
            json.loads(self.client.get(self.jones.view_path)[0]),
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
        #self.client.print_tree('/services')

        for i in ('127.0.0.1', '127.0.0.2'):
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
            BadVersionException,
            self.jones.set_config,
            None, {"foo": "bag"}, 4,
        )

    def test_delete_config(self):
        fixture.init_tree(self.jones)
        env = 'parent/child1'
        self.jones.delete_config(env, -1)

        self.assertRaises(
            NoNodeException,
            self.jones.get_config,
            '127.0.0.2'
        )

        self.assertRaises(
            NoNodeException,
            self.jones.get_config_by_env,
            env
        )

        self.assertRaises(
            NoNodeException,
            self.jones.get_view_by_env,
            env
        )

    def test_conf_is_mapping(self):
        """Make sure create_config only allows collections.Mapping types"""

        self.assertRaises(
            ValueError,
            self.jones.create_config,
            None, 'hello'
        )

    def test_get_associations(self):
        fixture.init_tree(self.jones)
        assocs = self.jones.associations.get_all()
        for host in fixture.ASSOCIATIONS:
            self.assertEquals(
                assocs[host],
                self.jones._get_view_path(fixture.ASSOCIATIONS[host])
            )

    def test_delete_association(self):
        fixture.init_tree(self.jones)
        self.jones.delete_association('127.0.0.3')
        self.assertRaises(
            KeyError,
            self.jones.get_config,
            '127.0.0.3'
        )
        self.assertTrue(len(self.jones.associations.get_all()) > 0)

    def test_create_service(self):
        """Test that creating a service creates stub conf/view/nodemaps."""

        env = None
        self.jones.create_config(env, {})
        self.assertEquals(self.jones.get_associations(env), None)
        self.assertEquals(self.jones.get_view_by_env(env), {})
        self.assertEquals(self.jones.get_config_by_env(env)[1], {})
        self.assertEquals(self.jones.get_child_envs(env), [''])

    def test_exists_reflectes_creation(self):
        self.assertFalse(self.jones.exists())
        self.jones.create_config(None, {})
        self.assertTrue(self.jones.exists())

    def test_delete_service(self):
        """Test that deleting a service removes all sub-nodes."""

        env = None
        self.jones.create_config(env, {})

        self.jones.delete_all()
        self.assertRaises(
            NoNodeException,
            self.client.get,
            self.jones.root
        )
