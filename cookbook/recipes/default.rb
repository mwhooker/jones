#
# Cookbook Name:: jones
# Recipe:: default
#
# Copyright 2012, Matthew Hooker
#
# All rights reserved - Do Not Redistribute
#

include_recipe "gunicorn"
include_recipe "nginx"
chef_gem "zookeeper"
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

if node[:exhibitor][:hostname].is_a? String
  zk_connect_str = zk_connect_str(
    discover_zookeepers(node[:exhibitor][:hostname]),
    node[:jones][:zk_chroot])
elsif node[:jones][:zk_connect].is_a? String
  zk_connect_str = node[:jones][:zk_connect]
else
  raise "please either specify exhibitor hostname or zk connection string."
end

zookeeper_node '/' do
  action :create_if_missing
  connect_str zk_connect_str
end

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
  # TODO
  # notifies :restart, "supervisor_service[jones]"
  variables(
    :config => node[:jones][:config],
    :zk_connect_str => zk_connect_str
  )
end

nginx_conf_file "jones" do
  socket "127.0.0.1:8000"
  server_name "_"
end
