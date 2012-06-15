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


from flask import Flask, render_template
from raven.contrib.flask import Sentry
from werkzeug.contrib.fixers import ProxyFix
import zc.zk

from jones import Jones
import jonesconfig


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config.from_object(jonesconfig)
app.config.from_envvar('JONES_SETTINGS', silent=True)

if 'SENTRY_DSN' in app.config:
    sentry = Sentry(app)

zk = zc.zk.ZooKeeper(app.config['ZK_CONNECTION_STRING'])


@app.route('/')
def index():
    services = zk.get_children('/services')
    return render_template('index.html', services=services)

@app.route('/service/<string:service>', defaults={'env': None})
@app.route('/service/<string:service>/<path:env>')
def service(service, env):
    j = Jones(service, zk)
    """
    prefix = '/services/%s/conf' % service
    if len(env):
        prefix += "/%s" % env
    """
    children = j.get_child_envs('')
    config = j.get_config_by_env(env)[1]
    view = j.get_view_by_env(env)[1]
    return render_template('service.html',
                           env=env,
                           children=children,
                           config=config,
                           view=view,
                           service=service)

if __name__ == '__main__':
    app.run()
