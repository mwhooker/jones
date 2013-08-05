require 'json'
require 'zk'
require 'socket'



class JonesClient
  def initialize(options = {})
    yield self if block_given?

    @callbacks = []
    @conf_subscription = nil
    @conf_path = nil

    parse_options(options)
    setup_zk
  end

  def register_callback(&block)
    @callbacks += [block]
  end

  private

  def nodemap_changed(event)
    if event.node_changed?
      read_nodemap
    else
      logger.error("Unknown ZK node event: #{event.inspect}")
    end
  end

  def read_nodemap
    data = @zk.get(nodemap_path, :watch => true).first
    if data.nil?
      conf_path = conf_root
    else
      mapping = Hash[data.split("\n").map {|s| s.split(' -> ') }]
      conf_path = mapping.fetch(@host, conf_root)
    end
    if conf_path != @conf_path
      @conf_path = conf_path
      if not @conf_subscription.nil?
        @conf_subscription.unsubscribe
      end
      @conf_subscription = @zk.register(@conf_path) { |event| read_conf(event) }
    end
    
    read_conf(nil)
  end

  def read_conf(event)
    @data = JSON.load(@zk.get(@conf_path, :watch => true).first)
  end

  def setup_zk
    @zk = ZK.new(@zkservers) if @zkservers
    @zk.on_expired_session { setup_zk }
    @zk.register(nodemap_path, :only => :changed) { |event| nodemap_changed(event) }
    @zk.on_connected { read_nodemap }
    read_nodemap
  end

  def parse_options(options)
    @zk, @zkservers = options.values_at(:zk, :zkservers)
    if [@zk, @zkservers].all? || [@zk, @zkservers].none?
      raise ArgumentError, 'must specify :zk or :zkservers'
    end

    @service = options[:service]
    @host = options.fetch(:host, Socket.gethostname)
    @zkroot = "/services/#{options[:service]}"
  end


  def nodemap_path
    "#{@zkroot}/nodemaps"
  end

  def conf_root
    "#{@zkroot}/conf"
  end


end


#zk = ZK.new('localhost:2181')

jc = JonesClient.new(:zkservers => 'localhost:2181', :service => 'test')
puts "hi"
