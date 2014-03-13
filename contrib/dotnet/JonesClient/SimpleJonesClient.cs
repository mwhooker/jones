using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Sodao.Zookeeper;
using Sodao.Zookeeper.Data;
using System.Web.Script.Serialization;

namespace JonesClient
{
    /// <summary>
    /// Our simple Jones Client.  Configuration strings are stored in a Dictionary
    /// </summary>
    public class SimpleJonesClient
    {
        /// <summary>
        /// The hostname 
        /// </summary>
        public string HostName { set; get; }

        /// <summary>
        /// Service name
        /// </summary>
        public string ServiceName { set; get; }

        /// <summary>
        /// The Dictionary that holds the configuration
        /// </summary>
        public Dictionary<string, string> Config { get; set; }

        /// <summary>
        /// Our ZooKeeper client connection object
        /// </summary>
        protected IZookClient _zkclient = Sodao.Zookeeper.ZookClientPool.Get("zk1");       
        protected string NodeMapPath;
        protected IWatcher ConfigViewNodeChangeWatcher;

        /// <summary>
        /// The Jones client constructor
        /// </summary>
        /// <param name="service">Service Name</param>
        /// <param name="hostname">Hostname</param>
        /// <param name="zkclient">Zookeeper Client connection object</param>
        /// <param name="callback">Callback function for any changes to the config tree</param>
        public SimpleJonesClient(string service, string hostname = null, IZookClient zkclient = null, Action<Dictionary<string, string>> callback = null)
        {
            // initialize the hostname
            if (String.IsNullOrEmpty(hostname))
            {
                // get FDQN
                // http://stackoverflow.com/questions/804700/how-to-find-fqdn-of-local-machine-in-c-net
                // http://support.microsoft.com/kb/303902
                HostName = System.Net.Dns.GetHostEntry("LocalHost").HostName.ToLower();

                int idx = HostName.IndexOf(".");
                if (idx > 0)
                {
                    HostName = HostName.Substring(0, idx);
                }
            }

            if (zkclient != null)
            {
                _zkclient = zkclient;
            }

            // initialize the dictionary to hold the configurations
            Config = new Dictionary<string, string>();

            // set the service name
            ServiceName = service;
            
            // this is our callback for Config View ZNode changes, to refresh our 
            // this.Config
            ConfigViewNodeChangeWatcher = new WatcherWrapper(e =>
                {
                    _zkclient.GetData(e.Path, ConfigViewNodeChangeWatcher).ContinueWith(d =>
                        {
                            string conf_data = Encoding.UTF8.GetString(d.Result.Data);

                            Config = DeserializeNodeMap(conf_data);

                            if (callback != null)
                            {
                                callback.Invoke(Config);
                            }
                        });
                });

            NodeMapPath = String.Format(@"/services/{0}/nodemaps", ServiceName);
            
            #region get the current Config from the view            
          
            string current_conf_path = "";
            var tnm = _zkclient.GetData(NodeMapPath, false).ContinueWith(c => 
                {
                    string conf_path_json = Encoding.UTF8.GetString(c.Result.Data);

                    try
                    {
                        current_conf_path = DeserializeNodeMap(conf_path_json)[HostName];
                    }
                    catch (Exception)
                    {
                        // fail-safe default configs when there's no machine-specific config is found
                        current_conf_path = String.Format(@"/services/{0}/conf", ServiceName);
                    }

                    var td = _zkclient.GetData(current_conf_path, ConfigViewNodeChangeWatcher).ContinueWith(d =>
                        {
                            // this part is important so this.Config will not be empty on constructor completion!
                            string conf_data = Encoding.UTF8.GetString(d.Result.Data);

                            Config = DeserializeNodeMap(conf_data);
                        });
                    
                    td.Wait(); // synchronous wait
                });

            tnm.Wait(); // synchronous wait

            #endregion
           
        }

        /// <summary>
        /// Helper function to deserialize string to a JSON object
        /// </summary>
        /// <param name="json_nodemap_data">JSON string (presumably from a node map)</param>
        /// <returns>Dictionary of keys and values</returns>
        public static Dictionary<string, string> DeserializeNodeMap(string json_nodemap_data)
        {
            JavaScriptSerializer jss = new JavaScriptSerializer();
            var d = jss.Deserialize<Dictionary<string, string>>(json_nodemap_data);

            return d;
        }
    }
}
