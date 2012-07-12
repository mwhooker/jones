from kazoo.testing import KazooTestCase

from jones.jones import ZNodeMap


class TestZNodeMap(KazooTestCase):

    def setUp(self):
        super(TestZNodeMap, self).setUp()
        self.links = ZNodeMap(self.client, "/nodemaps")

    def test_set(self):
        self.links.set('src', 'dest')
        self.assertEquals(self.links.get('src'), 'dest')
