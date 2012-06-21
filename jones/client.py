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

import socket
import zookeeper
from collections import Mapping


class JonesClient(Mapping):
    """An example client for accessing config stored by Jones."""

    def __init__(self, service, zk, cb=None, hostname=None):
        """ 
        service: name of the service to get config for.
        zk: zc.zk object.
        cb: method to be called with config when it changes.
        hostname: Node to get associated configuration data for.
        """

        self.service = service
        self.zk = zk
        self.cb = cb

        if not hostname:
            hostname = socket.getfqdn()
        self.hostname = hostname

        root = "/services/%s/nodemaps" % service
        self.lookup_key = root + '/' + hostname

        self.nodemap = self.zk.properties(root)
        self.nodemap(self._on_nodemap_change)

    def _config_cb(self, node):
        self.config = node.data
        if self.cb:
            self.cb(node.data)

    def _on_nodemap_change(self, _):
        try:
            self.config_key = self.zk.resolve(self.lookup_key)
        except zookeeper.NoNodeException:
            self.config_key = '/services/%s/conf' % self.service

        self.node = self.zk.properties(self.config_key)
        self.node(self._config_cb)

    def __getitem__(self, key):
        return self.config[key]

    def __iter__(self):
        return iter(self.config)

    def __len__(self):
        return len(self.config)
