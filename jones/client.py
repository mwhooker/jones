import socket
import zc.zk


"""
/services
  /testservice
    /conf
      config = u'{"foo": "bar"}'
      /parent
        config = u'{"a": 1, "c": {"x": 0}, "b": [1, 2, 3]}'
        /child1
          config = u'{"a": 2}'
          /subchild1
            config = u'{"b": "abc"}'
        /child2
          config = u'{"a": 3}'
    /nodemaps
      127.0.0.1 -> /services/testservice/views/parent
      127.0.0.2 -> /services/testservice/views/parent/child1
    /views
      /parent
        config = u'{"a": 1, "c": {"x": 0}, "foo": "bar", "b": [1, 2, 3]}'
        /child1
          config = u'{"a": 2, "c": {"x": 0}, "foo": "bar", "b": [1, 2, 3]}'
          /subchild1
            config = u'{"a": 2, "c": {"x": 0}, "foo": "bar", "b": "abc"}'
        /child2
          config = u'{"a": 3, "c": {"x": 0}, "foo": "bar", "b": [1, 2, 3]}'
"""


class JonesClient(object):
    """An example client for accessing config stored by Jones."""

    def __init__(self, service, zk, cb, hostname=None):
        self.zk = zk
        self.cb = cb

        if not hostname:
            hostname = socket.getfqdn()
        self.hostname = hostname

        root = "/services/%s/nodemaps" % service
        self.lookup_key = root + '/' + hostname

        self.nodemap = self.zk.properties(root)
        self.nodemap(self._on_nodemap_change)

    def _on_nodemap_change(self, _):
        self.config_key = self.zk.resolve(self.lookup_key)

        self.node = self.zk.properties(self.config_key)
        self.node(lambda node: self.cb(node.data))
