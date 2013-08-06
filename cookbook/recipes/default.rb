#
# Cookbook Name:: jones
# Recipe:: default
#
# Copyright 2013, Matthew Hooker
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

include_recipe "gunicorn"
include_recipe "nginx"
include_recipe "supervisor"
package "libevent-dev"

user node[:jones][:user] do
  uid node[:jones][:uid]
  gid node[:jones][:group]
end

directory node[:jones][:destination] do
  owner node[:jones][:user]
  recursive true
  mode "0755"
end

config_path = "#{node[:jones][:destination]}/shared/jonesconfig.py"
venv = "#{node[:jones][:destination]}/shared/env"

python_virtualenv venv do
  owner "root"
  action :create
end

application "jones" do
  path node[:jones][:destination]
  packages ["git-core"]

  repository node[:jones][:repo]
  revision node[:jones][:tag]
  owner node[:jones][:user]
  group node[:jones][:group]

  # TODO: environment not being set.
  gunicorn do
    environment :JONES_SETTINGS => config_path
    packages ["gevent", "jones[web]"]
    port 8000
    workers node[:cpu][:total] + 1
    backlog 2048
    worker_class "egg:gunicorn#gevent"
    app_module "jones.web:app"
    virtualenv venv
  end
end

template config_path do
  source "config.py.erb"
  owner "root"
  group "root"
  mode "0644"
  variables(
    :config => node[:jones][:config],
    :zk_connect_str => zk_connect_str(
      discover_zookeepers(node[:exhibitor][:hostname]),
      node[:jones][:zk_chroot])
  )
end

supervisor_service "jones" do
  subscribes :before_deploy, "application[jones]"
  action :start
end

nginx_conf_file "jones" do
  socket "127.0.0.1:8000"
  server_name "_"
end
