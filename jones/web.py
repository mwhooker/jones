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


from flask import Flask, redirect, render_template, request, url_for
from raven.contrib.flask import Sentry
from werkzeug.contrib.fixers import ProxyFix
from jinja2 import Markup
import json
import zc.zk
import zookeeper

from jones import Jones
import jonesconfig


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config.from_object(jonesconfig)
app.config.from_envvar('JONES_SETTINGS', silent=True)

if 'SENTRY_DSN' in app.config:
    sentry = Sentry(app)

zk = zc.zk.ZooKeeper(app.config['ZK_CONNECTION_STRING'])


@app.template_filter()
def as_json(d, indent=None):
    return Markup(json.dumps(d, indent=indent))


@app.route('/service')
def index():
    services = zk.get_children('/services')
    return render_template('index.html', services=services)

def service_create(env, jones):
    jones.create_config(env, {})
    return env, 201

def service_update(env, jones):
    jones.set_config(
        env,
        json.loads(request.form['data']),
        int(request.form['version'])
    )
    return env

def service_delete(env, jones):
    jones.delete_config(env, -1)
    return redirect(url_for('service', service=jones.service))

def service_get(env, jones):
    children = list(jones.get_child_envs())
    is_leaf = lambda child: not any(
        [c.find(child + '/') >= 0 for c in children])

    try:
        version, config = jones.get_config_by_env(env)
    except zookeeper.NoNodeException:
        return redirect(url_for('service', service=jones.service))

    view = jones.get_view_by_env(env)[1]
    return render_template('service.html',
                           env=env,
                           version=version,
                           children=zip(children, map(is_leaf, children)),
                           config=config,
                           view=view,
                           service=jones.service,
                           associations=jones.get_associations()
                          )

SERVICE = {
    'get': service_get,
    'put': service_update,
    'post': service_create,
    'delete': service_delete
}

ALL_METHODS = ['GET', 'PUT', 'POST', 'DELETE']

@app.route('/service/<string:service>', defaults={'env': None},
           methods=ALL_METHODS)
@app.route('/service/<string:service>/<path:env>', methods=ALL_METHODS)
def service(service, env):
    jones = Jones(service, zk)

    print request.method
    return SERVICE[request.method.lower()](env, jones)


@app.route('/association/<string:assoc>/<string:service>',
           defaults={'env': None}, methods=['POST', 'DELETE'])
@app.route('/association/<string:assoc>/<string:service>/<path:env>',
           methods=['POST', 'DELETE'])
def association(assoc, service, env):
    jones = Jones(service, zk)

    if request.method == 'POST':
        jones.assoc_host(assoc, env)
        return service, 201
    elif request.method == 'DELETE':
        jones.delete_association(assoc)
        return service, 200



if __name__ == '__main__':
    app.run()
