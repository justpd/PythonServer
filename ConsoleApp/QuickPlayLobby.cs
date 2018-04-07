using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Bindings;
using Newtonsoft.Json;

namespace ConsoleApp
{
    class QuickPlayLobby
    {
        public static List<UserSession> Clients = new List<UserSession>();
        public static Dictionary<int, QuickPlaySession> Sessions = new Dictionary<int, QuickPlaySession>();
        static int roomId = 0;

        private static int SortByRating(UserSession a, UserSession b)
        {
            return a.rating.CompareTo(b.rating);
        }

        public static void Initialize()
        {
            while(true)
            {
                if (Clients.Count > 1)
                {
                    Clients.Sort(SortByRating);
                    QuickPlaySession session = new QuickPlaySession(Clients[0], Clients[1], roomId++);
                    Sessions.Add(session.roomId, session);
                    Clients.RemoveRange(0, 2);
                }
            }
        }

        public static void EnterQuery(UserSession userSession)
        {
            Clients.Add(userSession);
        }

        public static void DestroySession(QuickPlaySession session)
        {
            Sessions.Remove(session.roomId);
        }
        
    }
}
