"""
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


from flask import Flask, jsonify, redirect, render_template, request, url_for
from raven.contrib.flask import Sentry
from werkzeug.contrib.fixers import ProxyFix
from jinja2 import Markup
from kazoo.security import make_acl, make_digest_acl_credential
from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeException
from itertools import repeat, izip, imap
import json

from jones import Jones
import zkutil
import jonesconfig


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config.from_object(jonesconfig)
app.config.from_envvar('JONES_SETTINGS', silent=True)

if 'SENTRY_DSN' in app.config:
    sentry = Sentry(app)

jones_credential = make_digest_acl_credential(
    'Jones', app.config['ZK_DIGEST_PASSWORD']
)
zk = KazooClient(
    app.config['ZK_CONNECTION_STRING'],
    default_acl=(
        # grants read permissions to anyone.
        make_acl('world', 'anyone', read=True),
        # grants all permissions to the creator of the node.
        make_acl('auth', '', all=True)
    )
)
zk.start()
zk.add_auth('digest', jones_credential)
zk.ensure_path('/services')


def request_wants(t):
    types = ['text/plain', 'text/html', 'application/json']
    assert t in types
    best = request.accept_mimetypes \
        .best_match(types)
    return best == t


@app.template_filter()
def as_json(d, indent=None):
    return Markup(json.dumps(d, indent=indent))


@app.context_processor
def inject_services():
    return dict(services=[child for child in zk.get_children('/services') if
                          Jones(child, zk).exists()])


@app.route('/')
def index():
    return render_template('index.j2')


def service_create(env, jones):

    jones.create_config(env, {})
    if request_wants('application/json') or request_wants('text/plain'):
        r = jsonify(service=jones.service)
        r.status_code = 201
        return r
    else:
        return redirect(url_for('service', service=jones.service, env=env))


def service_update(env, jones):
    jones.set_config(
        env,
        json.loads(request.form['data']),
        int(request.form['version'])
    )
    return env or ''


def service_delete(env, jones):
    if not env:
        # deleting whole service
        jones.delete_all()
        #return redirect(url_for('index'))
    else:
        jones.delete_config(env, -1)
    return env, 200


def service_get(env, jones):
    if not jones.exists():
        return redirect(url_for('index'))

    children = jones.get_child_envs()
    is_leaf = lambda child: not any(
        [c.find(child + '/') >= 0 for c in children])

    try:
        version, config = jones.get_config_by_env(env)
    except NoNodeException:
        return redirect(url_for('service', service=jones.service))

    childs = imap(dict, izip(
        izip(repeat('env'),
            imap(lambda env: env if len(env) else "/",
                children)),
        izip(repeat('is_leaf'), imap(is_leaf, children))))

    vals = {
        "env": env or '',
        "version": version,
        "children": list(childs),
        "config": config,
        "view": jones.get_view_by_env(env),
        "service": jones.service,
        "associations": jones.get_associations(env)
    }
    if request_wants('application/json'):
        return jsonify(vals)
    else:
        return render_template('service.j2', **vals)


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

    return SERVICE[request.method.lower()](env, jones)


# TODO: what if we have a path called association?
@app.route('/service/<string:service>/association/<string:assoc>',
           methods=['GET', 'PUT', 'DELETE'])
def association(service, assoc):
    jones = Jones(service, zk)

    if request.method == 'GET':
        if request_wants('application/json'):
            return jsonify(jones.get_config(assoc))
    if request.method == 'PUT':
        jones.assoc_host(assoc, request.form['env'])
        return service, 201
    elif request.method == 'DELETE':
        jones.delete_association(assoc)
        return service, 200


@app.route('/export')
def export():
    return zkutil.export_tree(zk, '/')


if __name__ == '__main__':
    app.run()
