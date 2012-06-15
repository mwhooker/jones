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
