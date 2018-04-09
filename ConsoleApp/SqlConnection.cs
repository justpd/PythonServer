using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using Bindings;
using MySql.Data.MySqlClient;
using Newtonsoft.Json;

namespace ConsoleApp {
    class SqlConnection {
        private static string SQLSERVER = "127.0.0.1";
        private static string DATABASE = "gamedatasw";
        private static string UID = "root";
        private static string PASS = "";

        private static Dictionary<string, string> settings = new Dictionary<string, string> ();

        private static MySqlConnection sqlConnection;

        public static void Initialize () {
            MySqlConnectionStringBuilder builder = new MySqlConnectionStringBuilder {
                Server = SQLSERVER,
                UserID = UID,
                Password = PASS,
                Database = DATABASE
            };

            string conncetionString = builder.ToString ();
            builder = null;
            Console.WriteLine (conncetionString);
            sqlConnection = new MySqlConnection (conncetionString);
            settings.Add ("subIndex", "");
            settings.Add ("userIndex", "");
            GetServerSetting ("subIndex");
            GetServerSetting ("userIndex");
        }

        // json
        private static void GetServerSetting (string setting) {
            string query = string.Format ("SELECT * FROM serverdata WHERE id = '{0}'", setting);
            try {
                MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                sqlConnection.Open ();
                MySqlDataReader reader = cmd.ExecuteReader ();
                while (reader.Read ()) {
                    settings[setting] = (string) reader["value"];
                    break;
                }
                sqlConnection.Close ();
            } catch (System.Exception ex) {
                Console.WriteLine (ex);
            }
        }

        // json
        private static void UpdateServerSetting (string id, string value) {
            string query = string.Format ("UPDATE serverdata SET value = '{1}' WHERE id = '{0}'", id, value);
            Console.WriteLine (query);
            try {
                MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                sqlConnection.Open ();
                cmd.ExecuteNonQuery ();
                sqlConnection.Close ();
            } catch (System.Exception ex) {
                Console.WriteLine (ex);
            }

            GetServerSetting (id);
        }

        public static string GenerateUserId () {
            int userIndex = Int32.Parse (settings["userIndex"]);
            userIndex += 1;

            UpdateServerSetting ("userIndex", userIndex.ToString ());

            if (userIndex < 10)
                return "00" + userIndex;
            else if (userIndex < 100)
                return "0" + userIndex;
            else
                return userIndex.ToString ();
        }

        public static bool LoginUser (string login, string password) {
            string query = string.Format ("SELECT * FROM gamedata WHERE login = '{0}'", login);
            Console.WriteLine (query);
            try {
                MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                sqlConnection.Open ();
                MySqlDataReader reader = cmd.ExecuteReader ();
                bool valid = false;
                while (reader.Read ()) {
                    //Console.WriteLine("id: " + reader["id"] + " login: " + reader["login"] + " password: " + reader["password"] + " email: " + reader["email"]);
                    if ((string) reader["login"] == login && (string) reader["password"] == password) {
                        valid = true;
                    } else {
                        Console.WriteLine ("Authentification error.");
                    }
                }
                sqlConnection.Close ();
                return valid;
            } catch (System.Exception ex) {
                Console.WriteLine (ex);
                return false;
            }
        }

        public static bool RegisterUser (UserRegistrationData userData) {
            if (ValidLogin (userData.login) && ValidEmail (userData.email)) {
                string query = string.Format ("INSERT INTO gamedata(login, password, email) VALUES('{0}','{1}','{2}')", userData.login, userData.password, userData.email);
                Console.WriteLine (query);
                try {
                    MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                    sqlConnection.Open ();
                    cmd.ExecuteNonQuery ();
                    sqlConnection.Close ();
                    Console.WriteLine ("New user joined: " + userData.login);

                    string[] newChars;
                    switch (userData.faction) {
                        case "Faith":
                            newChars = new string[] { "Preacher", "Paladin", "Priest" };
                            break;
                        default:
                            newChars = new string[] { "Preacher", "Paladin", "Priest" };
                            break;
                    }

                    string newUserId = settings["subIndex"] + "-" + GenerateUserId ();

                    InitializeUserAccountData (userData.login, newUserId, newChars);

                    InitializeUserChar (newChars[0], newUserId);
                    InitializeUserChar (newChars[1], newUserId);
                    InitializeUserChar (newChars[2], newUserId);

                    return true;
                } catch (System.Exception ex) {
                    Console.WriteLine (ex);
                    return false;
                }
            } else {
                Console.WriteLine ("Login or Email are already registered.");
                return false;
            }
        }

        public static bool InitializeUserAccountData (string login, string id, string[] mainTeamNames) {
            string query = string.Format ("INSERT INTO useraccountdata(id, login, gold, experience, energy, rating, mainTeam) VALUES('{0}','{1}',{2},{3},{4},{5},'{6}')", id, login, 0, 0, 100, 0, JsonConvert.SerializeObject (mainTeamNames));
            Console.WriteLine (query);
            try {
                MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                sqlConnection.Open ();
                cmd.ExecuteNonQuery ();
                sqlConnection.Close ();
                return true;
            } catch (System.Exception ex) {
                Console.WriteLine (ex);
                return false;
            }
        }

        public static void UpdateUserAccountData (UserSession userSession) {
            string query = string.Format ("UPDATE useraccountdata SET gold = {1}, experience = {2}, energy = {3}, rating = {4} WHERE login = '{0}'", userSession.login, userSession.gold, userSession.exp, userSession.energy, userSession.rating);
            Console.WriteLine (query);
            try {
                MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                sqlConnection.Open ();
                cmd.ExecuteNonQuery ();
                sqlConnection.Close ();
            } catch (System.Exception ex) {
                Console.WriteLine (ex);
            }
        }

        public static bool ValidLogin (string login) {
            string query = string.Format ("SELECT * FROM gamedata WHERE login = '{0}'", login);
            try {
                MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                sqlConnection.Open ();
                MySqlDataReader reader = cmd.ExecuteReader ();
                bool valid = true;
                while (reader.Read ()) {
                    valid = false;
                }
                sqlConnection.Close ();
                return valid;
            } catch (System.Exception ex) {
                Console.WriteLine (ex);
                return false;
            }
        }

        public static bool ValidEmail (string email) {
            string query = string.Format ("SELECT * FROM gamedata WHERE email = '{0}'", email);
            try {
                MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                sqlConnection.Open ();
                MySqlDataReader reader = cmd.ExecuteReader ();
                bool valid = true;
                while (reader.Read ()) {
                    valid = false;
                }
                sqlConnection.Close ();
                return valid;
            } catch (System.Exception ex) {
                Console.WriteLine (ex);
                return false;
            }
        }

        public static void DeleteUser (string login) {
            string query = string.Format ("DELETE FROM gamedata WHERE login = '{0}'", login);
            Console.WriteLine (query);
            try {
                MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                sqlConnection.Open ();
                cmd.ExecuteNonQuery ();
                sqlConnection.Close ();
            } catch (System.Exception ex) {
                Console.WriteLine (ex);
            }
        }

        public static UserSession InitialazeUserSession (string login) {
            string query = string.Format ("SELECT * FROM useraccountdata WHERE login = '{0}'", login);
            Console.WriteLine (query);
            try {
                MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                sqlConnection.Open ();
                MySqlDataReader reader = cmd.ExecuteReader ();
                UserSession userSession = new UserSession ();
                while (reader.Read ()) {
                    userSession.id = (string) reader["id"];
                    userSession.login = (string) reader["login"];
                    userSession.gold = (int) reader["gold"];
                    userSession.exp = (int) reader["experience"];
                    userSession.rating = (int) reader["rating"];
                    userSession.energy = (int) reader["energy"];
                    userSession.mainTeamNames = JsonConvert.DeserializeObject<string[]> ((string) reader["mainTeam"]);
                    break;
                }
                sqlConnection.Close ();
                return userSession;
            } catch (System.Exception ex) {
                Console.WriteLine (ex);
                return null;
            }
        }
        
        // json
        public static UserChar LoadUserChar (string name, UserSession userSession) {
            string userCharId = UserChar.GetIdByName (name);
            string query = String.Format ("SELECT * FROM userchardata WHERE id REGEXP '{0}-{1}'", userSession.id, userCharId);
            Console.WriteLine (query);
            try {
                MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                sqlConnection.Open ();
                MySqlDataReader reader = cmd.ExecuteReader ();
                UserChar uChar = new UserChar ();
                while (reader.Read ()) {
                    uChar.name = (string) reader["name"];
                    uChar.id = (string) reader["id"];
                    uChar.lvl = (int) reader["lvl"];
                    uChar.power = (int) reader["power"];

                    uChar.Health = (int) reader["health"];
                    uChar.Agility = (int) reader["agility"];
                    uChar.Strength = (int) reader["strength"];
                    uChar.Intelligence = (int) reader["intelligence"];
                    uChar.Potency = (float) reader["potency"];
                    uChar.Tenacity = (float) reader["tenacity"];
                    uChar.CriticalChance = (float) reader["criticalChance"];
                    uChar.HealthSteal = (float) reader["healthSteal"];
                    uChar.Armor = (float) reader["armor"];
                    uChar.MagicResistance = (float) reader["magicResistance"];
                    uChar.ArmorPenetration = (float) reader["armorPenetration"];
                    uChar.EvadeChance = (float) reader["evadeChance"];
                    uChar.Speed = (int) reader["speed"];

                    uChar.HealForce = (float) reader["healForce"];
                    uChar.CriticalDamage = (float) reader["criticalDamage"];
                    uChar.PhysicalDamage = (float) reader["physicalDamage"];
                    uChar.MagicalDamage = (float) reader["magicalDamage"];
                    break;
                }
                sqlConnection.Close ();
                return uChar;
            } catch (System.Exception ex) {
                Console.WriteLine (ex);
                return null;
            }
        }

        // json
        public static void AddUserChar (string name, UserChar userChar) {
            string query = string.Format (new CultureInfo ("en-US"), "INSERT INTO userchardata(id, name, lvl, power, health, agility, strength, intelligence, potency, tenacity, criticalChance, healthSteal, armor, magicResistance, armorPenetration, evadeChance, speed, healForce, criticalDamage, physicalDamage, magicalDamage) VALUES('{0}','{1}',{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18},{19},{20})", userChar.id, userChar.name, userChar.lvl, userChar.power, userChar.Health, userChar.Agility, userChar.Strength, userChar.Intelligence, userChar.Potency, userChar.Tenacity, userChar.CriticalChance, userChar.HealthSteal, userChar.Armor, userChar.MagicResistance, userChar.ArmorPenetration, userChar.EvadeChance, userChar.Speed, userChar.HealForce, userChar.CriticalDamage, userChar.PhysicalDamage, userChar.MagicalDamage);
            Console.WriteLine (query);
            try {
                MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                sqlConnection.Open ();
                cmd.ExecuteNonQuery ();
                sqlConnection.Close ();
            } catch (System.Exception ex) {
                Console.WriteLine (ex);
            }
        }

        public static UserChar InitializeUserChar (string name, string newUserId) {
            string query = String.Format ("SELECT * FROM basechardata WHERE name = '{0}'", name);
            Console.WriteLine (query);
            try {
                MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                sqlConnection.Open ();
                MySqlDataReader reader = cmd.ExecuteReader ();
                UserChar uChar = new UserChar ();
                while (reader.Read ()) {
                    uChar.name = (string) reader["name"];
                    uChar.id = newUserId + "-" + (string) reader["id"];
                    uChar.lvl = (int) reader["lvl"];
                    uChar.power = (int) reader["power"];

                    uChar.Health = (int) reader["health"];
                    uChar.Agility = (int) reader["agility"];
                    uChar.Strength = (int) reader["strength"];
                    uChar.Intelligence = (int) reader["intelligence"];
                    uChar.Potency = (float) reader["potency"];
                    uChar.Tenacity = (float) reader["tenacity"];
                    uChar.CriticalChance = (float) reader["criticalChance"];
                    uChar.HealthSteal = (float) reader["healthSteal"];
                    uChar.Armor = (float) reader["armor"];
                    uChar.MagicResistance = (float) reader["magicResistance"];
                    uChar.ArmorPenetration = (float) reader["armorPenetration"];
                    uChar.EvadeChance = (float) reader["evadeChance"];
                    uChar.Speed = (int) reader["speed"];

                    uChar.HealForce = (float) reader["healForce"];
                    uChar.CriticalDamage = (float) reader["criticalDamage"];
                    uChar.PhysicalDamage = (float) reader["physicalDamage"];
                    uChar.MagicalDamage = (float) reader["magicalDamage"];
                    break;
                }
                sqlConnection.Close ();
                AddUserChar (name, uChar);
                return uChar;
            } catch (System.Exception ex) {
                Console.WriteLine (ex);
                return null;
            }
        }

        public static void UpdateUserImage (UserImageData userImageData) {
            string query = string.Format ("UPDATE userimages SET b64str = '{1}', scale = {2} WHERE login = '{0}'", userImageData.login, userImageData.b64str, userImageData.scale);
            Console.WriteLine (query);
            try {
                MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                sqlConnection.Open ();
                cmd.ExecuteNonQuery ();
                sqlConnection.Close ();
            } catch (System.Exception ex) {
                Console.WriteLine (ex);
            }
        }

        // json
        public static string GetUserImage (string login) {
            string query = string.Format ("SELECT * FROM userimages WHERE login = '{0}'", login);
            Console.WriteLine (query);
            try {
                MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                sqlConnection.Open ();
                MySqlDataReader reader = cmd.ExecuteReader ();
                UserImageData userImageData = new UserImageData ();
                while (reader.Read ()) {
                    userImageData.b64str = (string) reader["b64str"];
                    userImageData.login = (string) reader["login"];
                    userImageData.scale = (int) reader["scale"];
                    break;
                }
                sqlConnection.Close ();
                return JsonConvert.SerializeObject (userImageData);
            } catch (System.Exception ex) {
                Console.WriteLine (ex);
                return null;
            }
        }
        // json
        public static void SetDefaultUserImage (string login) {
            string query = string.Format ("INSERT INTO userimages(login, b64str, scale) VALUES('{0}','{1}', {2})", login, "iVBORw0KGgoAAAANSUhEUgAAAAQAAAAECAYAAACp8Z5+AAAAHUlEQVQIHWNkWP3/PwMSYEJig5ksV+RMUMQwVAAA040D2a+7GAgAAAAASUVORK5CYII=", 4);
            Console.WriteLine (query);
            try {
                MySqlCommand cmd = new MySqlCommand (query, sqlConnection);
                sqlConnection.Open ();
                cmd.ExecuteNonQuery ();
                sqlConnection.Close ();
            } catch (System.Exception ex) {
                Console.WriteLine (ex);
            }
        }
    }
}