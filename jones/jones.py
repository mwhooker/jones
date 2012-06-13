import json
import zc.zk
from functools import partial

class Jones(object):
    """

    "view" refers to a node which has has the following algorithm applied
        for node in root -> env
            update view with node.config
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


    def set_config(self, env, conf):
        """Set conf to env under service.
        
        "/" is the root of the config tree.
        """

        self._set(self._get_env_path(env), conf)

        if env:
            self._flatten_to_view(env)


    def get_config(self, ip):
        return self._get(
            self.zk.resolve(self._get_nodemap_path(ip))
        )


    def assoc_ip(self, ip, env):
        """Associate ip with env under service."""

        self.zk.ln(
            self._get_view_path(env),
            self._get_nodemap_path(ip)
        )


    def _get_nodemap_path(self, ip):
        return "%s/%s" % (self.nodemap_path, ip)


    def _get_path(self, prefix, env):
        if not env:
            return prefix
        return '/'.join((prefix, env))


    def _flatten_to_view(self, env):
        """Roll up from root to env. Store in env view."""

        dest = self._get_view_path(env)
        nodes = env.split('/')

        # Path through the znode graph from root ('') to env
        path = [nodes[:n] for n in xrange(len(nodes)+1)]

        # Expand path and map it to the root
        path = map(
            self._get_env_path,
            ['/'.join(p) for p in path]
        )

        data = {}
        for n in path:
            config = self._get(n) 
            data.update(config)

        self._set(dest, data)

    def _set(self, path, data):
        self.zk.create(path, '', zc.zk.OPEN_ACL_UNSAFE)
        self.zk.properties(path).set(config=json.dumps(data))

    def _get(self, path):
        return json.loads(self.zk.properties(path).get('config'))
