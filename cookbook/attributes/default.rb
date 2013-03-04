default[:jones][:version] = "0.5.3"
default[:jones][:user] = "jones"
default[:jones][:uid] = "61002"
default[:jones][:group] = "nogroup"
default[:jones][:zk_chroot] = "jones"
#default[:jones][:zk_connect] = "localhost:2181"

default[:jones][:mirror] = "https://github.com/mwhooker/jones/archive/#{default[:jones][:version]}.tar.gz"
default[:jones][:destination] = "/opt/www/jones"
default[:jones][:virtualenv] = "#{default[:jones][:destination]}/venv"

default[:jones][:config][:debug] = "False"
default[:jones][:config][:testing] = "False"
default[:jones][:config][:secret_key] = "dev key"
default[:jones][:config][:zk_digest_password] = "changeme"

default[:python][:distribute_install_py_version] = "2.7"
default[:python][:install_method] = "package"
