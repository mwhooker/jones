# Cookbook Name:: jones
# Recipe:: default
#
# Copyright 2012, Matthew Hooker
#
# All rights reserved - Do Not Redistribute
#

directory node[:jones][:gunicorn][:config_dir] do
  owner "root"
  mode "0755"
end

config_path = "#{node[:jones][:gunicorn][:config_dir]}/jones.py"

gunicorn_config config_path do
  worker_processes node[:cpu][:total] + 1
  backlog 2048
  worker_class "egg:gunicorn#gevent"
  action :create
end
