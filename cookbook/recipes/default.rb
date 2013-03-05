#
# Cookbook Name:: jones
# Recipe:: default
#
# Copyright 2012, Matthew Hooker
#
# All rights reserved - Do Not Redistribute
#

include_recipe "gunicorn"

package "git-core"

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

template config_path do
  source "config.py.erb"
  owner "root"
  group "root"
  mode "0644"
  # notifies :restart, "service[jones]"
  variables(
    :config => node[:jones][:config],
    :zk_connect_str => zk_connect_str
  )
end

venv = "#{node[:jones][:destination]}/shared/env"

python_virtualenv venv do
  owner "root"
  action :create
end

application "jones" do
  path node[:jones][:destination]
  # packages ["libpq-dev", "git-core", "mercurial"]

  repository node[:jones][:repo]
  revision node[:jones][:tag]
  owner node[:jones][:user]
  group node[:jones][:group]
  # action :deploy # or :rollback
  # notifies :restart, "service[jones]"

  gunicorn do
    port 8080
    workers node[:cpu][:total] + 1
    backlog 2048
    worker_class "egg:gunicorn#gevent"
    environment "JONES_SETTINGS" => config_path
    app_module "jones.web:app"
    virtualenv venv
  end

  nginx_load_balancer do
    application_port 8080
  end

end
