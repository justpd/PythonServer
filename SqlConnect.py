import mysql.connector
import json
# self.config = {
#     'user': 'root',
#     'password': 'Y6o2d7DdM277s3q',
#     'host': '127.0.0.1',
#     'database': 'gamedatasw',
#     'raise_on_warnings': True,
#     'use_pure': False,
# }

class SqlConnection:
    def __init__(self):
        self.settingspath = 'settings.json'
        self.configpath = 'config.json'
        with open(self.configpath, 'r') as json_file:
            self.config = json.load(json_file)
            self.config.update({'raise_on_warnings':True, 'use_pure':False,})
            print(self.config)
        self.getServerSettings()

    def getServerSettings(self):
        with open(self.settingspath, 'r') as json_file:
            self.settings = json.load(json_file)
    
    def setServerSetting(self, inputKey, value):
        
        with open(self.settingspath, 'r') as json_file:
            self.settings = json.load(json_file)

        if self.settings.get(inputKey, False):
            self.settings[inputKey] = value
        with open(self.settingspath, 'w') as json_file:
            json.dump(self.settings, json_file, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True)
                

    # def getServerSetting(self, setting):
        
    #     query = "SELECT * FROM serverdata WHERE id = '{}'".format(setting)
    #     print(query)

    #     try:
    #         conn = mysql.connector.connect(**self.config)
    #         cursor = conn.cursor(buffered=True)
    #         cursor.execute(query)
    #         for (id,value) in cursor:
    #             self.settings[setting] = value        
    #             print(self.settings)

    #         cursor.close()
    #         conn.close()
    #     except mysql.connector.Error as err:
    #         print("Something went wrong: {}".format(err))

    # def updateServerSetting(self, id, value):
    #     query = "UPDATE serverdata SET value = '{}' WHERE id = '{}'".format(value, id)
    #     print(query)

    #     try:
    #         conn = mysql.connector.connect(**self.config)
    #         cursor = conn.cursor(buffered=True)

    #         try:
    #             cursor.execute(query)
    #         except mysql.connector.Error as err:
    #             print("Something went wrong: {}".format(err))
    #         else:
    #             conn.commit()            

    #         cursor.close()
    #         conn.close()
    #     except mysql.connector.Error as err:
    #         print("Something went wrong: {}".format(err))
    #     self.getServerSetting(id)
    
    def generateUserId(self):
        userIndex = int(self.settings.get("userIndex"))
        userIndex += 1

        self.setServerSetting("userIndex", userIndex)

        if (userIndex < 10):
            return "00" + str(userIndex)
        elif (userIndex < 100):
            return "0" + str(userIndex)
        else:
            return str(userIndex)

    def loginUser(self, login, password):
        query = "SELECT * FROM gamedata WHERE login = '{}'".format(login)
        print(query)

        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True, buffered=True)
            
            valid = False
            cursor.execute(query)
            for value in cursor:
                if (str(value["login"]) == login and str(value["password"]) == password):
                    valid = True;
                    print("User connected: " + str(value["login"]))
                else:
                    print("Authentification error.")

            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        return valid

    def registerUser (self, login, password, email, faction):
        if self.is_valid("login", login) and self.is_valid("email", email):
            
            query = "INSERT INTO gamedata(login, password, email) VALUES('{}','{}','{}')".format(login, password, email)
            print(query)

            try:
                conn = mysql.connector.connect(**self.config)
                cursor = conn.cursor(buffered=True)

                try:
                    cursor.execute(query)
                except mysql.connector.Error as err:
                    print("Something went wrong: {}".format(err))
                else:
                    conn.commit()            
                    print("New user joined: " + login)

                    if faction.lower() == "faith":
                        newChars = ["Preacher", "Paladin", "Priest"]
                    else:
                        newChars = ["Preacher", "Paladin", "Priest"]
                cursor.close()
                conn.close()

                newUserId = self.settings['subIndex'] + "-" + self.generateUserId()
                self.InitializeUserAccountData(login, newUserId, newChars)

                for i in range(0, 3):
                    self.InitializeUserChar(newChars[i], newUserId)
                return True

            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))
                return False
        else:
            print("Login or Email are already registered.")
            return False
        

    def is_valid(self, data, value ):
        query = "SELECT * FROM gamedata WHERE `{}` = '{}'".format(data.lower(),value.lower())
        print(query)
        
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(buffered=True)
            
            valid = True
            cursor.execute(query)
            for value in cursor: 
                valid = False

            cursor.close()
            conn.close()
            print (valid)
            return valid
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            return False;

    # JSON
    # def InitializeUserAccountData(self, login, id, mainTeamNames):
    #     temp_buf = {"id":id, "login":login, "gold":0, "experience":0, "energy":100, "rating":0}
    #     temp_buf.update(json.JSONEncoder(mainTeamNames, skipkeys=True, ensure_ascii=True, check_circular=False, allow_nan=False))
    #     with open("\userdata\user_" + str(id) + ".json" , 'w') as json_file:
    #         json.dump(temp_buf, json_file, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True)

    # def UpdateUserAccountData(self, id, inputKey, value):
    #     try:
    #          with open("\userdata\user_" + str(id) + ".json", 'r') as json_file:
    #             temp_buf = json.load(json_file)
    #     except FileNotFoundError:
    #         print("file \userdata\user_" + str(id) + ".json not found")

    #     if temp_buf.get(inputKey, False):
    #         temp_buf[inputKey] = value
    #     try:
    #         with open("\userdata\user_" + str(id) + ".json", 'w') as json_file:
    #             json.dump(temp_buf, json_file, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True)
    #     except FileNotFoundError:
    #         print("file \userdata\user_" + str(id) + ".json not found")

    def DeleteUser (id):
        query = "DELETE FROM gamedata WHERE login = '{0}'".format(id)
        print(query)

        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(buffered=True)

            try:
                cursor.execute(query)
            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))
            else:
                conn.commit()            

            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

    def InitializeUserAccountData (self, login, id, mainTeamNames):
        buf = json.JSONEncoder().encode (mainTeamNames)
        query = "INSERT INTO useraccountdata(id, login, gold, experience, energy, rating, mainTeam) VALUES({id},{login},{gold},{exp},{energy},{rating},{team})".format(id= id, login= login, gold= 0, exp= 0, energy= 100, rating= 0, team= buf )
        print(query)

        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(buffered=True)

            try:
                cursor.execute(query)
            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))
            else:
                conn.commit()            

            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
    
    def InitialazeUserSession(self, login):
        query = "SELECT * FROM useraccountdata WHERE login = '{}'".format(login)
        print(query)
        
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True, buffered=True)
            
            cursor.execute(query)
            userSession = cursor.fetchall()

            cursor.close()
            conn.close()
            return userSession

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))


    # def UpdateUserAccountData (self, userSession):

    def InitializeUserChar(self, name, id ):
        query = "SELECT * FROM basechardata WHERE name = '{0}'".format(name)
        print(query)
        
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True, buffered=True)
            
            cursor.execute(query)
            uChar = cursor.fetchall()

            cursor.close()
            conn.close()
            return uChar
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

if __name__ == '__main__':
    db = SqlConnection()
    db.registerUser('root', 'toor', 'none', '')