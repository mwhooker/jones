Gem::Specification.new do |s|
  s.name        = 'jones'
  s.version     = '0.1.0'
  s.date        = '2013-08-05'
  s.summary     = "Client for Jones configuration management server"
  s.authors     = ["Matthew Hooker"]
  s.email       = 'mwhooker@gmail.com'
  s.files       = ["lib/client.rb"]
  s.homepage    = 'https://github.com/mwhooker/jones'
  s.license     = 'Apache 2.0'
  s.add_runtime_dependency "zk", ["= 1.8.0"]
end
