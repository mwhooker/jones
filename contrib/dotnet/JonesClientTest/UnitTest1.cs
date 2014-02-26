using System;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using JonesClient;
using Sodao.Zookeeper;

namespace JonesClientTest
{
    [TestClass]
    public class UnitTest1
    {
        [TestMethod]
        public void TestCreateSimpleJonesClient()
        {
            var jc = new SimpleJonesClient(service: "yoda");

            //while (true)
            {
                System.Threading.Thread.Sleep(1000);

                foreach (var key in jc.Config.Keys)
                {
                    Console.WriteLine("{0} = {1}", key, jc.Config[key]);
                }
            }
            System.Console.ReadLine();
        }
    }
}
