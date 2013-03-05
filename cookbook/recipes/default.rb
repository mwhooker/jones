#
# Cookbook Name:: jones
# Recipe:: default
#
# Copyright 2012, Matthew Hooker
#
# All rights reserved - Do Not Redistribute
#

# include_recipe "python"
include_recipe "gunicorn"
include_recipe "jones::gunicorn"

user node[:jones][:user] do
  uid node[:jones][:uid]
  gid node[:jones][:group]
end

directory node[:jones][:destination] do
  owner node[:jones][:user]
  recursive true
  mode "0755"
end

config_path = "#{node[:jones][:config_dir]}/jonesconfig.py"

template config_path do
  source "config.py.erb"
  owner "root"
  group "root"
  mode "0644"
  # notifies :restart, "service[jones]"
  variables(:config => node[:jones][:config])
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
  end

  nginx_load_balancer do
    application_port 8080
  end

end

# template "gunicorn.upstart.conf" do
#   path "/etc/init/gunicorn.conf"
#   source "gunicorn.upstart.conf.erb"
#   owner "root"
#   group "root"
#   mode "0644"
#   notifies :stop, "service[exhibitor]" # :restart doesn't reload upstart conf
#   notifies :start, "service[exhibitor]"
#   variables(
#       :user => node[:jones][:user],
#       :bind_address => node[:jones][:gunicorn][:port],
#       :config_path => "#{node[:jones][:gunicorn][:config_dir]}/jones.py"
#   )
# end


# python_virtualenv node[:jones][:virtualenv] do
#   owner "root"
#   action :create
# end
# 
# service "gunicorn" do
#   provider Chef::Provider::Service::Upstart
#   supports :start => true, :status => true, :restart => true
#   action :start
# end

