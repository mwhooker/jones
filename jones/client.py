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

from collections import Mapping
from kazoo.recipe.watchers import DataWatch

import socket
import json


class EnvironmentNotFoundException(Exception):
    pass


class JonesClient(Mapping):
    """An example client for accessing config stored by Jones.

    :param zk: zookeeper connection.
    :type zk: :class:`kazoo.client.KazooClient`
    :param service: name of the service to get config for.
    :type service: string.
    :param cb: optional method to be called with config when it changes.
    :type param: function.
    :param hostname: Node to get associated configuration data for.
    :type hostname: string.

    """

    def __init__(self, zk, service, cb=None, hostname=None):
        self.service = service
        self.zk = zk
        self.cb = cb

        if not hostname:
            hostname = socket.getfqdn()
        self.hostname = hostname

        self.nodemap_path = "/services/%s/nodemaps" % service

        self.nodemap_watcher = DataWatch(
            self.zk, self.nodemap_path,
            self._nodemap_changed
        )

    def _nodemap_changed(self, data, stat):
        """Called when the nodemap changes."""

        if not stat:
            raise EnvironmentNotFoundException(self.nodemap_path)

        try:
            conf_path = self._deserialize_nodemap(data)[self.hostname]
        except KeyError:
            conf_path = '/services/%s/conf' % self.service

        self.config_watcher = DataWatch(
            self.zk, conf_path,
            self._config_changed
        )

    def _config_changed(self, data, stat):
        """Called when config changes."""

        self.config = json.loads(data)

        if self.cb:
            self.cb(self.config)

    @staticmethod
    def _deserialize_nodemap(d):
        if not len(d):
            return {}
        return dict(l.split(' -> ') for l in d.split('\n'))

    def __getitem__(self, key):
        return self.config[key]

    def __iter__(self):
        return iter(self.config)

    def __len__(self):
        return len(self.config)
