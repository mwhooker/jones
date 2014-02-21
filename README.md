jones
=====

[![travis][2]][1]

Jones is a configuration frontend for Zookeeper.

Goals
-----

   * Clients MUST only talk to zookeeper
   * Accessing configuration MUST be simple (i.e. no computation)
   * Unique views of the config must be available on a host-by-host basis

Introduction
------------

At their root, most configuration systems are a hierarchy of dictionaries. The
root has config common to all environments, with config specific to say,
developers or a staging area, inheriting and overriding values. Jones takes
this idea and maps it to Zookeeper.

Zookeeper is the ideal place for configuration. Besides it's availability
guarantees, it's also able to update observers when data changes. Now we can
change config at runtime, making possible a whole category of use-cases like
switches, a/b tests, and knob and lever you can imagine.

For more information, see my
[talk](http://pyvideo.org/video/1567/configuration-management-with-zookeeper)
and [presentation](https://speakerdeck.com/mwhooker/jones) at Pycon Canada.

Running the Server
-----------------

Jones uses the [Flask](http://flask.pocoo.org/) web framework. For development,
running the server is as simple as `python jones/web.py`.

For running in production, I recommend using [Gunicorn](http://gunicorn.org/)
with an http frontend like nginx or apache. Gunicorn can run Jones with
`gunicorn jones.web:app`. For more information on running gunicorn see [Running
Gunicorn](http://docs.gunicorn.org/en/latest/run.html). For help on deploying
gunicorn with nginx, see [Deploying
Gunicorn](http://docs.gunicorn.org/en/latest/deploy.html)

Using the client
----------------

Jones comes with an example client, which we hope will serve the most general
case.  It's also incredibly simple (only 30 lines), so it should be easy to
customize. Using it is just as straight-forward.

**Install:**

    pip install jones

**Use:**

    from jones.client import JonesClient

    # Initialize jones client with kazoo connection, and service.
    jones = JonesClient(zk, 'da')
    client['key']
    'value'
    client.get('missingkey', 'default')
    'default'

<dl>
  <dt>zk</dt>
  <dd>An instance of kazoo.client.KazooClient.</dd>
  <dt>service</dt>
  <dd>The name of the service you want config for.</dd>
</dl>

The JonesClient object also takes an optional callback and association.

<dl>
  <dt>cb</dt>
  <dd>A method to be called with a config dict every time it changes.</dd>
  <dt>association</dt>
  <dd>A key in the _associations_ map. By default JonesClient uses socket.getfqdn().</dd>
</dl>

Design
------

Environments are stored under their parent znodes on the zookeeper data tree.
On write, the view algorithm is used to materialize the "inherited" config in
a view node.

Jones takes advantage of zookeeper's mvcc capabilities where possible. An
environment will never have its data clobbered by a concurrent write. When
updating a view, however, the last write wins. This may cause view data to be
clobbered if concurrent writes are made to two nodes in the same path and Jones
happens to lose its session in between (see issue #1).

Associations are a simple key to env map, stored under /nodemaps.

Example data tree dump. This shows data for an example service:

```
/
/services
 /services/test
    /services/test/nodemaps
      {"example": "/services/test/views/child1/sib"}
    /services/test/conf
      {"foo": "bar", "fiesasld": "value31"}
      /services/test/conf/child1
        {"field": "HAILSATAN"}
        /services/test/conf/child1/sib
          {"foo": "big"}
        /services/test/conf/child1/baby
          {"foo": "baz"}
    /services/test/views
      {"foo": "bar", "fiesasld": "value31"}
      /services/test/views/child1
        {"field": "HAILSATAN", "foo": "bar", "fiesasld": "value31"}
        /services/test/views/child1/sib
          {"field": "HAILSATAN", "foo": "big", "fiesasld": "value31"}
        /services/test/views/child1/baby
          {"field": "HAILSATAN", "foo": "baz", "fiesasld": "value31"}
  /services/test2
    /services/test2/nodemaps
    /services/test2/conf
      {}
    /services/test2/views
      {}
```

Glossary
--------

<dl>
  <dt>Config Tree</dt>
  <dd>The hierarchy of nodes.</dd>
  <dt>Node</dt>
  <dd>A node in the config tree. Nodes hold configuration for an environment. Implemented as a znode.</dd>
  <dt>Environment</dt>
  <dd>Also seen as <em>env</em> in the code, an environment is the path to a specific node in the config tree
  (i.e. parent/child).</dd>
  <dt>Association</dt>
  <dd>The identifier a client will use to address a node. Any string will work, but the fqdn or ip address are common.</dd>
  <dt>View</dt>
  <dd>A view is a node which has has the following algorithm applied
    <pre>for node in root -> env
  update view with node.config</pre>
  </dd>
</dl>

Changelog
---------

Jones uses [Semantic Versioning](http://semver.org/).

> Given a version number MAJOR.MINOR.PATCH, increment the:

> MAJOR version when you make incompatible API changes,
MINOR version when you add functionality in a backwards-compatible manner, and
PATCH version when you make backwards-compatible bug fixes.  Additional labels
for pre-release and build metadata are available as extensions to the
MAJOR.MINOR.PATCH format.

### 0.7.0
   * Upgraded to Bootstrap 3.0rc1
   * Turned the loosely defined `env` into a type
   * Fixed numerous bugs and style issues

### 1.0.0
   * Updated Kazoo to 1.12.1
   * Rewrote the ZKNodeMap class to serialize to json instead of the legacy format.
      * the code is smart enough to update the map format on the fly, but I advise you to test on your set up, first.

Screenshot
----------
![Example](http://mwhooker.github.com/jones/docs/img/testservice.png)

  [1]: https://travis-ci.org/mwhooker/jones
  [2]: https://travis-ci.org/mwhooker/jones.png?branch=master
