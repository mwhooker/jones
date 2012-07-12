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
import time

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

MAGIC_NUMBER = 0.2

class TestJonesClient(KazooTestCase):

    def setUp(self):
        super(TestJonesClient, self).setUp()
        self.config = None
        self.service = 'testservice'
        self.hostname = '127.0.0.2'

        self.jones = Jones(self.service, self.client)
        fixture.init_tree(self.jones)
        self.jones_client = JonesClient(self.service, self.client, self.default_cb,
                                        self.hostname)
        time.sleep(MAGIC_NUMBER)

    def default_cb(self, config):
        self.config = config

    def test_gets_config(self):

        self.assertEquals(self.config, fixture.CHILD1)
        fixt = "I changed"
        self.jones.set_config('parent', {'k': fixt}, -1)
        time.sleep(MAGIC_NUMBER)
        self.assertEquals(self.config['k'], fixt)

    def test_isa_dict(self):

        self.assertEquals(self.jones_client, fixture.CHILD1)

    def test_responds_to_remap(self):
        """test that changing the associations updates config properly."""

        self.jones.assoc_host(self.hostname, 'parent')
        time.sleep(MAGIC_NUMBER)
        self.assertEquals(self.config, fixture.PARENT)

    def test_defaults_to_root(self):
        """
        If a hostname doesn't map to anything,
        make sure to default to the root.
        That way we don't have to add every
        host under our control to zk.
        """

        hostname = '0.0.0.0'
        client = JonesClient(self.service, self.client,
                             hostname=hostname)
        self.assertTrue(hostname not in fixture.ASSOCIATIONS.keys())
        self.assertEquals(client.config, fixture.CONFIG['root'])
        self.jones.assoc_host(hostname, 'parent')
        time.sleep(MAGIC_NUMBER)
        self.assertEquals(client.config, fixture.PARENT)
