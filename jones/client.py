import socket


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
