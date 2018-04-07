using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Bindings;
using Newtonsoft.Json;
using ConsoleApp.Chars;

namespace ConsoleApp
{
    public class QuickPlaySession
    {
        public string roomName;
        public int roomId;
        public UserSession player_1;
        public UserSession player_2;
        public Dictionary<string, UserChar> PlayerChars = new Dictionary<string, UserChar>();
        public List<MoveLog> moveLogs = new List<MoveLog>();
        public string[] plyer_1_chars;
        public string[] plyer_2_chars;
        public int[] alive = {3, 3};
        public int readyToGoCount = 0;
        public bool waitingForMove = false;
        public bool gameOver = false;
        public string winner;

        Random random = new Random();

        public QuickPlaySession(UserSession player_1, UserSession player_2, int roomId)
        {
            this.player_1 = player_1;
            this.player_2 = player_2;
            this.roomId = roomId;
            this.roomName = player_1.login + "vs" + player_2.login;

            PlayerChars.Add(player_1.mainTeam[0].id, player_1.mainTeam[0]);
            SetClass(player_1.mainTeam[0].id);
            PlayerChars.Add(player_1.mainTeam[1].id, player_1.mainTeam[1]);
            SetClass(player_1.mainTeam[1].id);
            PlayerChars.Add(player_1.mainTeam[2].id, player_1.mainTeam[2]);
            SetClass(player_1.mainTeam[2].id);

            PlayerChars.Add(player_2.mainTeam[0].id, player_2.mainTeam[0]);
            SetClass(player_2.mainTeam[0].id);
            PlayerChars.Add(player_2.mainTeam[1].id, player_2.mainTeam[1]);
            SetClass(player_2.mainTeam[1].id);
            PlayerChars.Add(player_2.mainTeam[2].id, player_2.mainTeam[2]);
            SetClass(player_2.mainTeam[2].id);


            Start();
        }

        private void SetClass(string id)
        {
            switch (PlayerChars[id].name)
            {
                case "Paladin":
                    PlayerChars[id] = new Paladin(PlayerChars[id]);
                    break;
                case "Preacher":
                    PlayerChars[id] = new Preacher(PlayerChars[id]);
                    break;
                case "Priest":
                    PlayerChars[id] = new Priest(PlayerChars[id]);
                    break;
            }
        }

        public void Start()
        {
            Console.WriteLine("QuickPlay session started: " + roomName);

            UserImageData _image = JsonConvert.DeserializeObject<UserImageData>(SqlConnection.GetUserImage(player_2.login));

            QuickPlaySessionInfo _temp = new QuickPlaySessionInfo
            {
                roomName = roomName,
                roomId = roomId,
                firstPlayer = true,
                opponentName = player_2.login,
                opponentRating = player_2.rating,
                myCharNames = new string[] { player_1.mainTeamNames[0], player_1.mainTeamNames[1], player_1.mainTeamNames[2] },
                myCharIds = new string[] { player_1.mainTeam[0].id, player_1.mainTeam[1].id, player_1.mainTeam[2].id },
                opponentCharNames = new string[] { player_2.mainTeamNames[0], player_2.mainTeamNames[1], player_2.mainTeamNames[2] },
                opponentCharIds = new string[] { player_2.mainTeam[0].id, player_2.mainTeam[1].id, player_2.mainTeam[2].id },
                enemyImage = _image.b64str,
                enemyImageScale = _image.scale
            };

            ServerTCP.Send_QuickPlaySessionInfo(ServerTCP.OnlineClients[player_1.login], JsonConvert.SerializeObject(_temp));

            _image = JsonConvert.DeserializeObject<UserImageData>(SqlConnection.GetUserImage(player_1.login));

            _temp.firstPlayer = false;
            _temp.opponentName = player_1.login;
            _temp.opponentRating = player_1.rating;
            _temp.opponentCharNames = new string[] { player_1.mainTeamNames[0], player_1.mainTeamNames[1], player_1.mainTeamNames[2] };
            _temp.opponentCharIds = new string[] { player_1.mainTeam[0].id, player_1.mainTeam[1].id, player_1.mainTeam[2].id };
            _temp.myCharNames = new string[] { player_2.mainTeamNames[0], player_2.mainTeamNames[1], player_2.mainTeamNames[2] };
            _temp.myCharIds = new string[] { player_2.mainTeam[0].id, player_2.mainTeam[1].id, player_2.mainTeam[2].id };
            _temp.enemyImage = _image.b64str;
            _temp.enemyImageScale = _image.scale;

            ServerTCP.Send_QuickPlaySessionInfo(ServerTCP.OnlineClients[player_2.login], JsonConvert.SerializeObject(_temp));

            plyer_1_chars = new string[] { player_1.mainTeam[0].id, player_1.mainTeam[1].id, player_1.mainTeam[2].id };
            plyer_2_chars = new string[] { player_2.mainTeam[0].id, player_2.mainTeam[1].id, player_2.mainTeam[2].id };

            foreach (KeyValuePair<string, UserChar> playerChar in PlayerChars)
            {
                playerChar.Value.SetBaseValues();
                playerChar.Value.turnmeter = playerChar.Value.speed / 10;
            }
            CalculateTurns();
        }

        private void CalculateTurns()
        {
            readyToGoCount = 0;

            foreach (KeyValuePair<string, UserChar> playerChar in PlayerChars)
            {
                playerChar.Value.CheckValues();

                playerChar.Value.isActive = (playerChar.Value.health != 0);

                if (playerChar.Value.turnmeter == 100.0F)
                {
                    readyToGoCount += 1;
                }

                if (!playerChar.Value.isActive)
                {
                    playerChar.Value.turnmeter = 0.01F;
                }
            }

            string maxId = PlayerChars.OrderByDescending(x => x.Value.turnmeter).FirstOrDefault().Key;

            if (readyToGoCount < 1)
            {
                float _tempTurnMeter = PlayerChars[maxId].turnmeter;
                foreach (KeyValuePair<string, UserChar> playerChar in PlayerChars)
                {
                    if (playerChar.Value.isActive)
                        playerChar.Value.turnmeter *= (100.0F / (float)_tempTurnMeter);
                }
            }

            CheckWinner();
            StartNewMove(maxId);
        }

        private void CloseSession(UserSession player, UserSession opponent)
        {
            gameOver = true;
            winner = player.login;
            Console.WriteLine(winner + " won!");
            player.rating += 15;
            player.exp += 75;
            player.gold += 105;
            opponent.rating += 5;
            opponent.exp += 15;
            opponent.gold += 35;
            SqlConnection.UpdateUserAccountData(player);
            SqlConnection.UpdateUserAccountData(opponent);

            //QuickPlayLobby.DestroySession(this);
        }

        private void CheckWinner()
        {
            foreach (KeyValuePair<string, UserChar> playerChar in PlayerChars)
            {
                if (plyer_1_chars.Contains(playerChar.Key))
                {
                    if (playerChar.Value.health == 0)
                    {
                        alive[0] -= 1;
                    }
                }
                else
                {
                    if (playerChar.Value.health == 0)
                    {
                        alive[1] -= 1;
                    }
                }
            }

            if (alive[0] == 0)
            {
                CloseSession(player_2, player_1);
            }
            else if (alive[1] == 0)
            {
                CloseSession(player_1, player_2);
            }
            else
            {
                alive[0] = 3;
                alive[1] = 3;
            }

        }

        private void StartNewMove(string currentChar)
        {
            QuickPlaySessionData moveData = new QuickPlaySessionData
            {
                roomName = roomName,
                roomId = roomId,
                gameOver = gameOver,
                winner = winner
            };
            moveData.moveInfo = new MoveInfo
            {
                skillCount = PlayerChars[currentChar].skillCount,
                classID = currentChar.Substring(8)
            };

            Console.WriteLine("Starting Move: " + currentChar);
            foreach (KeyValuePair<string, UserChar> playerChar in PlayerChars)
            {
                Console.WriteLine(string.Format("({0}): {1} | health: {2}, speed: {3}, turnmeter: {4}", playerChar.Value.id, playerChar.Value.name, playerChar.Value.health, playerChar.Value.speed, playerChar.Value.turnmeter));
                float scaler = ((float)playerChar.Value.health / (float)playerChar.Value.Health) * 100.0F;
                
                Console.Write("|");
                Console.ForegroundColor = ConsoleColor.Green;
                for (int i = 100; i > 0; i--)
                {
                    if ((int) scaler > 0)
                        Console.Write('\u25A0');
                    else
                        Console.Write('_');
                    scaler--;
                }
                Console.ResetColor();
                Console.Write("|\n");
                Console.Write("|");
                Console.ForegroundColor = ConsoleColor.Blue;
                scaler = playerChar.Value.turnmeter;
                for (int i = 100; i > 0; i--)
                {
                    if ((int)scaler > 0)
                        Console.Write('\u25A0');
                    else
                        Console.Write('_');
                    scaler--;
                }
                Console.ResetColor();
                Console.Write("|\n");

                moveData.HealthData.Add(((float)playerChar.Value.health / (float)playerChar.Value.Health) * 100.0F);
                moveData.TurnMeterData.Add(playerChar.Value.turnmeter);

                waitingForMove = true;
            }

            moveData.currentCharId = currentChar;
            moveData.moveLogs = moveLogs;
            moveLogs.Clear();
            ServerTCP.Send_QuickPlaySessionData(ServerTCP.OnlineClients[player_1.login], JsonConvert.SerializeObject(moveData));
            ServerTCP.Send_QuickPlaySessionData(ServerTCP.OnlineClients[player_2.login], JsonConvert.SerializeObject(moveData));
        }

        private void SimulateMove(string current, string target, int skill)
        {
            Console.WriteLine(string.Format("SIMULATING: {0} performs {1} skill on {2}", current, skill, target));
            PlayerChars[current].Perform(skill, PlayerChars[target], this);
            PlayerChars[current].turnmeter = PlayerChars[current].speed / 10;
            CalculateTurns();
        }

        public void OnDataRecieve(string current, string target, int skill)
        {
            if (waitingForMove)
            {
                PlayerChars[current].Perform(skill, PlayerChars[target], this);
                PlayerChars[current].turnmeter = PlayerChars[current].speed / 10;
                CalculateTurns();
            }
        }

        public UserChar PickRandomTeamMate(UserChar current)
        {
            if (current.id.Substring(0, 7) == player_1.id)
            {
                UserChar randomTeamMate = PlayerChars[player_1.mainTeam[random.Next(0, 3)].id];
                while (randomTeamMate.health == 0)
                {

                }
                return randomTeamMate;
            }
            else
            {
                return PlayerChars[player_2.mainTeam[random.Next(0, 3)].id];
            }
        }

        public List<UserChar> PickAllTeamMates(UserChar current)
        {
            if (current.id.Substring(0, 7) == player_1.id)
            {
                return new List<UserChar> { PlayerChars[player_1.mainTeam[0].id], PlayerChars[player_1.mainTeam[1].id], PlayerChars[player_1.mainTeam[2].id] };
            }
            else
            {
                return new List<UserChar> { PlayerChars[player_2.mainTeam[0].id], PlayerChars[player_2.mainTeam[1].id], PlayerChars[player_2.mainTeam[2].id] };
            }
        }

        public List<UserChar> PickAllEnemies(UserChar current)
        {
            if (current.id.Substring(0, 7) == player_2.id)
            {
                return new List<UserChar> { PlayerChars[player_1.mainTeam[0].id], PlayerChars[player_1.mainTeam[1].id], PlayerChars[player_1.mainTeam[2].id] };
            }
            else
            {
                return new List<UserChar> { PlayerChars[player_2.mainTeam[0].id], PlayerChars[player_2.mainTeam[1].id], PlayerChars[player_2.mainTeam[2].id] };
            }
        }

        public UserChar PickRandomEnemy(UserChar current)
        {
            if (current.id.Substring(0, 7) == player_1.id)
            {
                return PlayerChars[player_2.mainTeam[random.Next(0, 3)].id];
            }
            else
            {
                return PlayerChars[player_1.mainTeam[random.Next(0, 3)].id];
            }
        }

    }
}
