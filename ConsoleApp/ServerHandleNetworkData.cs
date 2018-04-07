using System;
using System.Collections.Generic;
using Bindings;
using Newtonsoft.Json;

namespace ConsoleApp
{
    class ServerHandleNetworkData
    {
        private delegate void Packet_(int index, byte[] data);
        private static Dictionary<int, Packet_> Packets;

        public static void InitializeNetworkPackages()
        {
            Packets = new Dictionary<int, Packet_>
            {
                {(int)ClientPackets.C_ConfirmConnection, Handle_ConfirmConnection },
                {(int)ClientPackets.C_RequestUserLogin, Handle_RequestUserLogin },
                {(int)ClientPackets.C_RequestUserRegistration, Handle_RequestUserRegistration },
                {(int)ClientPackets.C_RequestUserAccountDataUpdate, Handle_RequestUserAccountDataUpdate },
                {(int)ClientPackets.C_RequestEnterQuickPlay, Handle_RequestEnterQuickPlay },
                {(int)ClientPackets.C_QuickPlayMoveData, Handle_QuickPlayMoveData },
                {(int)ClientPackets.C_RequestUserLogout, Handle_UserLogout },
                {(int)ClientPackets.C_RequestUpdateImage, Handle_ImageUpdate },

            };
            Console.WriteLine("Server launched on " + Constants.IP_ADRESS + ":" + Constants.PORT);
        }

        public static void HandleNetworkInfo(int index, byte[] data)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteBytes(data);
            int packetNum = buffer.ReadInteger();
            buffer.Dispose();

            if (Packets.TryGetValue(packetNum, out Packet_ Packet))
            {
                Packet.Invoke(index, data);
            }
        }

        // Main Handlers

        private static void Handle_ConfirmConnection(int index, byte[] data)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteBytes(data);
            int packetNum = buffer.ReadInteger();
            string msg = buffer.ReadString();
            buffer.Dispose();

            //add your code you want to execute here;
            Console.WriteLine(index + " : " + msg);
        }

        private static void Handle_RequestUserLogin(int index, byte[] data)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteBytes(data);
            int packetNum = buffer.ReadInteger();
            string msg = buffer.ReadString();
            buffer.Dispose();

            //Json parse
            UserLoginData userData = JsonConvert.DeserializeObject<UserLoginData>(msg);

            //add your code you want to execute here;
            Console.WriteLine(index + " : Requested login ({0}, {1})", userData.login, userData.password);

            UserSession userSession = SqlConnection.InitialazeUserSession(userData.login);

            if (SqlConnection.LoginUser(userData.login, userData.password))
            {
                Console.WriteLine(index + ": Logined in as " + userData.login);

                userSession.mainTeam[0] = SqlConnection.LoadUserChar(userSession.mainTeamNames[0], userSession);
                userSession.mainTeam[1] = SqlConnection.LoadUserChar(userSession.mainTeamNames[1], userSession);
                userSession.mainTeam[2] = SqlConnection.LoadUserChar(userSession.mainTeamNames[2], userSession);

                string json = JsonConvert.SerializeObject(userSession);
                try
                {
                    ServerTCP.OnlineClients.Add(userSession.login, index);
                }
                catch
                {
                    ServerTCP.OnlineClients.Remove(userSession.login);
                    ServerTCP.OnlineClients.Add(userSession.login, index);
                }
                ServerTCP.Send_ConfirmUserLogin(index, json);
                ServerTCP.Send_UpdateUserImage(index, SqlConnection.GetUserImage(userSession.login));
            }
            else
            {
                Console.WriteLine(index + ": Login was aborted");
                ServerTCP.Send_AbortUserLogin(index);
            }

        }

        private static void Handle_UserLogout(int index, byte[] data)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteBytes(data);
            int packetNum = buffer.ReadInteger();
            string msg = buffer.ReadString();
            buffer.Dispose();

            Console.WriteLine(msg + "logged out.");
            ServerTCP.OnlineClients.Remove(msg);
        }


        private static void Handle_RequestUserRegistration(int index, byte[] data)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteBytes(data);
            int packetNum = buffer.ReadInteger();
            string msg = buffer.ReadString();
            buffer.Dispose();

            //Json parse
            UserRegistrationData userData = JsonConvert.DeserializeObject<UserRegistrationData>(msg);

            //add your code you want to execute here;
            Console.WriteLine(index + " : Requested registration ({0}, {1}, {2})", userData.login, userData.password, userData.email);
            if (SqlConnection.RegisterUser(userData))
            {
                Console.WriteLine(index + ": Succesfully registered as " + userData.login);
                ServerTCP.Send_ConfirmUserRegistration(index);
                SqlConnection.SetDefaultUserImage(userData.login);
            }
            else
            {
                Console.WriteLine(index + ": Registration was aborted");
                ServerTCP.Send_AbortUserRegistration(index);
            }
        }

        private static void Handle_RequestUserAccountDataUpdate(int index, byte[] data)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteBytes(data);
            int packetNum = buffer.ReadInteger();
            string msg = buffer.ReadString();
            buffer.Dispose();

            //Json parse
            UserSession userSession = SqlConnection.InitialazeUserSession(msg);
            userSession.mainTeam[0] = SqlConnection.LoadUserChar(userSession.mainTeamNames[0], userSession);
            userSession.mainTeam[1] = SqlConnection.LoadUserChar(userSession.mainTeamNames[1], userSession);
            userSession.mainTeam[2] = SqlConnection.LoadUserChar(userSession.mainTeamNames[2], userSession);
            ServerTCP.Send_UpdateUserSessionData(index, JsonConvert.SerializeObject(userSession));

            ServerTCP.Send_UpdateUserImage(index, SqlConnection.GetUserImage(userSession.login));
        }

        private static void Handle_RequestEnterQuickPlay(int index, byte[] data)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteBytes(data);
            int packetNum = buffer.ReadInteger();
            string msg = buffer.ReadString();
            buffer.Dispose();

            //Json parse
            UserSession userSession = SqlConnection.InitialazeUserSession(msg);
            userSession.mainTeam[0] = SqlConnection.LoadUserChar(userSession.mainTeamNames[0], userSession);
            userSession.mainTeam[1] = SqlConnection.LoadUserChar(userSession.mainTeamNames[1], userSession);
            userSession.mainTeam[2] = SqlConnection.LoadUserChar(userSession.mainTeamNames[2], userSession);
            Console.WriteLine(index + string.Format(" : Entered 'QuickPlay' mode. (Rating = {0}, teamPower = {1})", userSession.rating, userSession.mainTeam[0].power + userSession.mainTeam[1].power + userSession.mainTeam[2].power));
            QuickPlayLobby.EnterQuery(userSession);
        }

        private static void Handle_QuickPlayMoveData(int index, byte[] data)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteBytes(data);
            int packetNum = buffer.ReadInteger();
            string msg = buffer.ReadString();
            buffer.Dispose();

            //Json parse
            QuickPlayMoveData moveData = JsonConvert.DeserializeObject<QuickPlayMoveData>(msg);

            //add your code you want to execute here;
            QuickPlayLobby.Sessions[moveData.roomId].OnDataRecieve(moveData.currentId, moveData.targetId, moveData.skill);
        }

        private static void Handle_ImageUpdate(int index, byte[] data)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteBytes(data);
            int packetNum = buffer.ReadInteger();
            string msg = buffer.ReadString();
            buffer.Dispose();

            //Json parse
            UserImageData imageData = JsonConvert.DeserializeObject<UserImageData>(msg);

            SqlConnection.UpdateUserImage(imageData);

            //add your code you want to execute here;
        }

    }
}
