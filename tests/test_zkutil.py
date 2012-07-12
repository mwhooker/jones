from jones import zkutil
from kazoo.testing import KazooTestCase


class TestZKUtil(KazooTestCase):

    def test_walk(self):
        expected = ['/test', '/test/a', '/test/a/b', '/test/z']
        for i in expected:
            self.client.create(i, '')

        self.assertEquals(
            sorted(zkutil.walk(self.client, '/test')),
            sorted(expected)
        )

