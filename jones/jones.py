import collections
import json
import zc.zk
from functools import partial


class Jones(object):
    """

    Glossary:
        view
            refers to a node which has has the following algorithm applied
            for node in root -> env
                update view with node.config
        environment
            a node in the service graph
            as passed to get/set config, it should identify
                the node within the service
                i.e. "production" or "dev/mwhooker"
    """

    def __init__(self, service, zk):
        self.zk = zk
        self.service = service
        self.root = "/services/%s" % service
        self.conf_path = "%s/conf" % self.root
        self.view_path = "%s/views" % self.root
        self.nodemap_path = "%s/nodemaps" % self.root

        self._get_env_path = partial(self._get_path, self.conf_path)
        self._get_view_path = partial(self._get_path, self.view_path)

        for k in (self.view_path, self.nodemap_path):
            self.zk.create_recursive(k, '', zc.zk.OPEN_ACL_UNSAFE)

    def create_config(self, env, conf):
        """
        Set conf to env under service.

        pass None to env for root.
        """

        if not isinstance(conf, collections.Mapping):
            raise ValueError("conf must be a collections.Mapping")

        self.zk.create(
            self._get_env_path(env),
            json.dumps(conf),
            zc.zk.OPEN_ACL_UNSAFE
        )

        self._update_view(env)

    def set_config(self, env, conf, version):
        """
        Set conf to env under service.

        pass None to env for root.
        """

        if not isinstance(conf, collections.Mapping):
            raise ValueError("conf must be a collections.Mapping")

        self._set(
            self._get_env_path(env),
            conf,
            version
        )

        def propogate(src):
            """Update env's children with new config."""

            self._update_view(src)
            path = self._get_env_path(src)
            for child in self.zk.get_children(path):
                if src:
                    child = "%s/%s" % (src, child)
                propogate(child)

        propogate(env)

    def get_config(self, hostname):
        """
        Returns a 2-tuple like (version, data).

        Version must be used with future calls to set_config.
        """
        return self._get(
            self.zk.resolve(self._get_nodemap_path(hostname))
        )

    def assoc_host(self, hostname, env):
        """
        Associate a host with an environment.

        hostname is opaque to Jones.
        Any string which uniquely identifies a host is acceptable.
        """

        self.zk.ln(
            self._get_view_path(env),
            self._get_nodemap_path(hostname)
        )

    def _flatten_to_root(self, env):
        """
        Flatten values from root down in to new view.
        """

        nodes = env.split('/')

        # Path through the znode graph from root ('') to env
        path = [nodes[:n] for n in xrange(len(nodes) + 1)]

        # Expand path and map it to the root
        path = map(
            self._get_env_path,
            ['/'.join(p) for p in path]
        )

        data = {}
        for n in path:
            _, config = self._get(n)
            data.update(config)

        return data

    def _update_view(self, env):
        if not env:
            env = ''

        dest = self._get_view_path(env)
        if not self.zk.exists(dest):
            self.zk.create(dest, '', zc.zk.OPEN_ACL_UNSAFE)

        self._set(dest, self._flatten_to_root(env))

    def _get_nodemap_path(self, hostname):
        return "%s/%s" % (self.nodemap_path, hostname)

    def _get_path(self, prefix, env):
        if not env:
            return prefix
        assert env[0] != '/'
        return '/'.join((prefix, env))

    def _get(self, path):
        data, metadata = self.zk.get(path)
        return metadata['version'], json.loads(data)

    def _set(self, path, data, *args, **kwargs):
        return self.zk.set(path, json.dumps(data), *args, **kwargs)
