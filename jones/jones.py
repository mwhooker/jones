import json
import zc.zk


class Jones(object):
    """

    "view" refers to a node which has has the following algorithm applied
        for node in root -> env
            update config with node.config
    """

    def __init__(self, service, zk):
        self.zk = zk
        self.service = service
        self.root = "/services/%s" % service
        self.conf_path = "%s/conf" % self.root
        self.view_path = "%s/views" % self.root
        self.nodemap_path = "%s/nodemaps" % self.root

        for k in (self.conf_path, self.view_path, self.nodemap_path):
            self.zk.create_recursive(k, '', zc.zk.OPEN_ACL_UNSAFE)


    def set_config(self, env, conf):
        """Set conf to env under service.
        
        "/" is the root of the config tree.
        """

        path = self._get_env_path(env)
        self._set(path, conf)

        self._flatten_to_view(env)


    def get_config(self, ip):
        return self._get(self._get_nodemap_path(ip))


    def assoc_ip(self, ip, env):
        """Associate ip with env under service."""

        path = self._get_nodemap_path(ip)

        self.zk.ln(self._get_view_path(env), path)


    def _get_nodemap_path(self, ip):
        return "%s/%s" % (self.nodemap_path, ip)


    def _get_env_path(self, env):
        """Path for env-specific config."""

        assert env[0] == '/'
        return '%s%s' % (self.conf_path, env)


    def _get_view_path(self, env):
        """Path for env view."""

        assert env[0] == '/'
        return "%s%s" % (self.view_path, env)


    def _flatten_to_view(self, env):
        """Roll up from root to env. Store in env view."""

        dest = self._get_view_path(env)

        paths = env.split('/')
        node_tree = ["%s/%s" % (self.conf_path, '/'.join(p))
                     for p in 
                     [paths[:n+1] for n in xrange(len(paths))]]

        data = {}
        for n in node_tree:
            config = self._get(n) 
            data.update(config)

        self._set(dest, data)

    def _set(self, path, data):
        #self.zk.create_recursive(path, '', zc.zk.OPEN_ACL_UNSAFE)
        self.zk.properties(path).set(config=json.dumps(data))

    def _get(self, path):
        return json.loads(self.zk.properties(path).get('config'))
