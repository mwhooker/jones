jones
=====

[![travis][2]][1]

Jones is a configuration frontend for Zookeeper.

Goals
-----

   * Clients MUST only talk to zookeeper
   * Accessing configuration MUST be simple (i.e. no computation)
   * Unique views of the config must be available on a host-by-host basis

Glossary
--------

<dl>
  <dt>Config Tree</dt>
  <dd>The hierarchy of nodes.</dd>
  <dt>Node</dt>
  <dd>A node in the config tree. Nodes hold configuration for an environment. Implemented as a znode.</dd>
  <dt>Environment</dt>
  <dd>Also seen as _env_ in the code, an environment is a specific node config tree.</dd>
  <dt>Association</dt>
  <dd>The identifier a client will use to address a node. Any string will work, but the fqdn or ip address are common.</dd>
  <dt>View</dt>
  <dd>A view is a node which has has the following algorithm applied
    <pre>for node in root -> env
  update view with node.config</pre>
  </dd>
</dl>

Screenshot
----------
![Example](http://code.disqus.com/jones/docs/img/testservice.png)

  [1]: http://travis-ci.org/#!/disqus/jones
  [2]: https://secure.travis-ci.org/disqus/jones.png?branch=master