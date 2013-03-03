#
# Cookbook Name:: jones
# Recipe:: default
#
# Copyright 2012, Matthew Hooker
#
# All rights reserved - Do Not Redistribute
#


include_recipe "python"
# include_recipe "nginx"

user node[:jones][:user] do
  uid node[:jones][:uid]
  gid node[:jones][:group]
end

directory node[:jones][:destination] do
  owner node[:jones][:user]
  recursive true
  mode "0755"
end

tarball = "#{Chef::Config[:file_cache_path]}/jones-#{node[:jones][:version]}.tar.gz"

remote_file tarball do
  action :create_if_missing
  owner "root"
  source node[:jones][:mirror]
  mode "0644"
end

bash "untar jones" do
  user "root"
  cwd "#{Chef::Config[:file_cache_path]}"
  code %(tar zxf #{tarball})
  creates "#{Chef::Config[:file_cache_path]}/jones-#{node[:jones][:version]}"
end

install_path = "#{node[:jones][:destination]}/jones-#{node[:jones][:version]}"

bash "copy jones" do
  user node[:jones][:user]
  cwd "#{Chef::Config[:file_cache_path]}"
  code %(cp -r #{Chef::Config[:file_cache_path]}/jones-#{node[:jones][:version]} install_path})
  creates install_path
end

python_virtualenv node[:jones][:virtualenv] do
  owner "root"
  action :create
end

python_pip "jones[web]" do
  virtualenv node[:jones][:virtualenv]
  action :install
end

python_pip "gunicorn" do
  virtualenv node[:jones][:virtualenv]
  action :install
end


# TODO: there's got to be a better way of deciding if we should use zk_connect attribute or exhibitor
if not node[:jones][:].is_a? String
 zk_connect_str(discover_zookeepers(), node[:jones][:zk_chroot))
end
