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
from collections import Mapping
import json


class JonesClient(Mapping):
    """An example client for accessing config stored by Jones."""

    def __init__(self, service, zk, cb=None, hostname=None):
        """
        service: name of the service to get config for.
        zk: KazooClient object.
        cb: optional method to be called with config when it changes.
        hostname: Node to get associated configuration data for.
        """

        self.service = service
        self.zk = zk
        self.cb = cb

        if not hostname:
            hostname = socket.getfqdn()
        self.hostname = hostname

        self.nodemap_path = "/services/%s/nodemaps" % service

        self._get_config()

    def _get_config(self, *args):

        def _deserialize(d):
            if not len(d):
                return {}
            return dict(l.split(' -> ') for l in d.split('\n'))

        nodemap, stat = self.zk.get(self.nodemap_path, self._get_config)

        try:
            conf_path = _deserialize(nodemap)[self.hostname]
        except KeyError:
            conf_path = '/services/%s/conf' % self.service

        config, stat = self.zk.get(conf_path, self._get_config)
        self.config = json.loads(config)

        if self.cb:
            self.cb(self.config)

    def __getitem__(self, key):
        return self.config[key]

    def __iter__(self):
        return iter(self.config)

    def __len__(self):
        return len(self.config)
