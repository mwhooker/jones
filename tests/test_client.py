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
import threading

from tests import fixture
from jones.jones import Jones
from jones.client import JonesClient
from kazoo.testing import KazooTestCase


"""
Because Kazoo's testing framework actually shells out to the local zookeeper
install, we've introduced real world uncertainty to our tests. A side-effect
of which we are attempting to work around by introduce wall-clock delays.
These are designed to allow time for zookeeper to invoke our callbacks before
testing for expected results.

The amount of wall-clock delay is reflected in the below magic number.
"""

MAGIC_NUMBER = 0.5

class TestJonesClient(KazooTestCase):

    def setUp(self):
        super(TestJonesClient, self).setUp()
        self.config = None
        self.service = 'testservice'
        self.hostname = '127.0.0.2'
        self.ev = threading.Event()

        self.jones = Jones(self.service, self.client)
        fixture.init_tree(self.jones)
        self.jones_client = JonesClient(self.client, self.service, self.default_cb,
                                        self.hostname)

    def default_cb(self, config):
        self.config = config
        self.ev.set()

    def test_gets_config(self):
        self.ev.wait(MAGIC_NUMBER)
        self.assertEquals(self.jones_client, fixture.CHILD1)
        self.assertEquals(self.config, fixture.CHILD1)

    def test_default_value(self):
        self.ev.wait(MAGIC_NUMBER)
        self.assertEquals(self.jones_client.get('a'), fixture.CHILD1['a'])
        self.assertEquals(self.jones_client.get('notinhere', 1), 1)

    def test_responds_to_remap(self):
        """test that changing the associations updates config properly."""

        self.ev.clear()
        self.jones.assoc_host(self.hostname, 'parent')
        self.ev.wait(MAGIC_NUMBER)
        self.assertEquals(self.config, fixture.PARENT)

    def test_defaults_to_root(self):
        """
        If a hostname doesn't map to anything,
        make sure to default to the root.
        That way we don't have to add every
        host under our control to zk.
        """

        ev = threading.Event()
        hostname = '0.0.0.0'
        self.assertTrue(hostname not in fixture.ASSOCIATIONS.keys())

        def cb(config):
            ev.set()

        client = JonesClient(self.client, self.service, cb, hostname)
        ev.wait(MAGIC_NUMBER)
        self.assertEquals(client.config, fixture.CONFIG['root'])
        self.assertTrue(ev.isSet())

        ev.clear()
        self.jones.assoc_host(hostname, 'parent')
        ev.wait(MAGIC_NUMBER)
        self.assertEquals(client.config, fixture.PARENT)
        self.assertTrue(ev.isSet())

    def test_works_if_zk_down(self):
        self.assertEquals(self.config, fixture.CHILD1)
        self.expire_session()
        self.assertEquals(self.config, fixture.CHILD1)

    def test_resets_watches(self):
        def test(fixt):
            self.ev.clear()
            self.jones.set_config('parent', {'k': fixt}, -1)
            self.ev.wait(MAGIC_NUMBER)
            self.assertEquals(self.config['k'], fixt)

        for fixt in ('a', 'b', 'c'):
            test(fixt)
