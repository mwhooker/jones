using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using JonesClient;

namespace JonesClientTestConsoleApp
{
    class Program
    {
        static void Main(string[] args)
        {
            var jc = new SimpleJonesClient(service: "yoda", callback: (d => {
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.WriteLine("config has changed: we now have {0} config items", d.Keys.Count);
                Console.ForegroundColor = ConsoleColor.Gray;

                foreach (var k in d.Keys)
                {
                    Console.WriteLine("{0} = {1}", k, d[k]);
                }

                Console.WriteLine("-");

            }));

            Console.WriteLine("hello, world!");
            Console.WriteLine("service {0} has {1} config items", jc.ServiceName, jc.Config.Keys.Count);
            foreach (var key in jc.Config.Keys)
            {
                Console.WriteLine("{0} = {1}", key, jc.Config[key]);
            }

            Console.WriteLine("-");
            Console.ReadKey(false);
        }
    }
}
