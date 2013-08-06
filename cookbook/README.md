Description
===========
Installs and configures Jones with nginx and gunicorn

Requirements
============
python
nginx\_conf
zookeeper
application
application\_python

Attributes
==========

`node[:jones][:config][:zk_digest_password]` is one you may want to change. By default jones is write-protected and this is how it accomplishes that.
