using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace ConsoleApp
{
    class Program
    {
        static void Main(string[] args)
        {
            ServerHandleNetworkData.InitializeNetworkPackages();
            SqlConnection.Initialize();
            ServerTCP.SetUp();
            QuickPlayLobby.Initialize();
            Console.ReadLine();
        }
    }
}
