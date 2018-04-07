using System;
using System.Net;
using System.Net.Sockets;
using Bindings;
using Newtonsoft.Json;
using System.Collections.Generic;

namespace ConsoleApp
{
    class ServerTCP
    {
        public static Dictionary<string, int> OnlineClients = new Dictionary<string, int>();

        private static Socket _servSock = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        private static byte[] _buffer = new byte[1024];
        public static Client[] clients = new Client[Constants.MAX_PLAYERS];
        public static int currentOnline = 0;

        public static void SetUp()
        {
            for (int i = 0; i < Constants.MAX_PLAYERS; i++)
            {
                clients[i] = new Client();
            }
            _servSock.Bind(new IPEndPoint(IPAddress.Any, Constants.PORT));
            _servSock.Listen(10);
            // accept connection
            _servSock.BeginAccept(new AsyncCallback(AcceptCallback), null);
        }

        private static void AcceptCallback(IAsyncResult asyncResult)
        {
            // accepting player connection
            Socket socket = _servSock.EndAccept(asyncResult);
            // statring accepting another players
            _servSock.BeginAccept(new AsyncCallback(AcceptCallback), null);

            for(int i = 0; i < Constants.MAX_PLAYERS; i++)
            {
                // Среди созданных ячеек для игроков ищем пустые
                if(clients[i].socket == null)
                {
                    // В пустую ячейку помещяем данные о новом клиенте
                    clients[i].socket = socket;
                    clients[i].index = i;
                    clients[i].ip = socket.RemoteEndPoint.ToString();
                    // Запускаем функцию получения информации от сервера
                    clients[i].StartClient();
                    Console.WriteLine("{0} connected", clients[i].ip);
                    Send_ConfirmConnection(i);
                    currentOnline += 1;
                    return;
                }
            }
        }

        public static void SendDataTo(int index, byte[] data)
        {
            byte[] sizeinfo = new byte[4];
            sizeinfo[0] = (byte)data.Length;
            sizeinfo[1] = (byte)(data.Length >> 8);
            sizeinfo[2] = (byte)(data.Length >> 16);
            sizeinfo[3] = (byte)(data.Length >> 24);

            clients[index].socket.Send(sizeinfo);
            clients[index].socket.Send(data);
        }

        public static void SendDataToAll(byte[] data)
        {
            for (int i = 0; i < Constants.MAX_PLAYERS; i++)
            {
                if (clients[i].socket != null)
                {
                    SendDataTo(i, data);
                }
            }
        }
        
        // Main Senders

        public static void Send_ConfirmConnection(int index)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteInt((int)ServerPackets.S_ConfirmConnection);
            buffer.WriteString("Succesfully connected to a server.");
            SendDataTo(index, buffer.ToArray());
            buffer.Dispose();
        }

        public static void Send_ConfirmUserLogin(int index, string json)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteInt((int)ServerPackets.S_ConfirmUserLogin);
            Console.WriteLine(json);
            buffer.WriteString(json);
            SendDataTo(index, buffer.ToArray());
            buffer.Dispose();
        }

        public static void Send_UpdateUserSessionData(int index, string json)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteInt((int)ServerPackets.S_UpdateUserSessionData);
            buffer.WriteString(json);
            SendDataTo(index, buffer.ToArray());
            buffer.Dispose();
        }

        public static void Send_UpdateUserImage(int index, string json)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteInt((int)ServerPackets.S_UpdateUserImage);
            buffer.WriteString(json);
            SendDataTo(index, buffer.ToArray());
            buffer.Dispose();
            
        }

        public static void Send_AbortUserLogin(int index)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteInt((int)ServerPackets.S_AbortUserLogin);
            buffer.WriteString("Login error.");
            SendDataTo(index, buffer.ToArray());
            buffer.Dispose();
        }

        public static void Send_ConfirmUserRegistration(int index)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteInt((int)ServerPackets.S_ConfirmUserRegistration);
            buffer.WriteString("Succesfully registered.");
            SendDataTo(index, buffer.ToArray());
            buffer.Dispose();
        }

        public static void Send_AbortUserRegistration(int index)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteInt((int)ServerPackets.S_AbortUserRegistration);
            buffer.WriteString("Registration error.");
            SendDataTo(index, buffer.ToArray());
            buffer.Dispose();
        }

        public static void Send_QuickPlaySessionInfo(int index, string json)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteInt((int)ServerPackets.S_SendQuickPlaySessionInfo);
            buffer.WriteString(json);
            Console.WriteLine(index);
            Console.WriteLine(json);

            SendDataTo(index, buffer.ToArray());
            buffer.Dispose();
        }

        public static void Send_QuickPlaySessionData(int index, string json)
        {
            PacketBuffer buffer = new PacketBuffer();
            buffer.WriteInt((int)ServerPackets.S_SendQuickPlaySessionData);
            buffer.WriteString(json);
            SendDataTo(index, buffer.ToArray());
            buffer.Dispose();
        }

    }

    // when player connects server creates a Client instance
    class Client
    {
        public int index;
        public string ip;
        public Socket socket;
        public bool closing = false;
        private byte[] _buffer = new byte[1024];

        // once the client is connectied we starting the client
        public void StartClient()
        {
            socket.BeginReceive(_buffer, 0, _buffer.Length, SocketFlags.None, new AsyncCallback(RecieveCallBack), socket);
            closing = false;
        }

        private void CloseClient(int index)
        {
            closing = true;
            Console.WriteLine("Connection from {0} has been terminated.", ip);
            // Player Left Game
            socket.Close();
            ServerTCP.clients[index].socket = null;
        }

        // It's where client Recieves data from the server
        private void RecieveCallBack(IAsyncResult asyncResult)
        {
            Socket socket = (Socket)asyncResult.AsyncState;

            try
            {
                int recieved = socket.EndReceive(asyncResult);
                if (recieved <= 0)
                {
                    CloseClient(index);
                }
                else
                {
                    byte[] databuffer = new byte[recieved];
                    Array.Copy(_buffer, databuffer, recieved);
                    ServerHandleNetworkData.HandleNetworkInfo(index, databuffer);
                    socket.BeginReceive(_buffer, 0, _buffer.Length, SocketFlags.None, new AsyncCallback(RecieveCallBack), socket);
                }
            }
            catch
            {
                CloseClient(index);
            }
        }
    }
}
