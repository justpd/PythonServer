import socket
import threading

class Server():

    # Инициализируем сервер
    def __init__(self, ip, port):
        # Инициализируем сокет
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Привязываем его к нашему ip
        self.server_socket.bind((ip, port))

        print('Running on {}:{}'.format(ip,port))

    # Поток обработки данных клиента
    def data_thread(self, client_socket, client_addres):
        try:
            # Получаем данные от клиента
            while True:
                data = client_socket.recv(2048)

                # Если данные пустые - прекращаем получение данных
                if not data:
                    break

                # Выводим полученные данные на экран
                print(data)
        # Если произошла ошибка - закрываем соединение с клиентом
        except:
            print('Client gone offline.')
            client_socket.close()

            try:
                # Удаляем его из словаря клиентов
                del self.online_clients[client_addres]
            except:
                pass
    
    # Запуск сервера
    def start(self):
        # Начинаем слушать входящие соединения
        self.server_socket.listen(4)
        # Создаём словарь для хранения сокетов клиента (key, value = address, socket)
        self.online_clients = {}

        while True:
            # Получаем сокет и аддрес клиента
            client_socket, client_addres = self.server_socket.accept()

            # Если клиента нет в списке известных клиентов, добавляем его
            if client_addres not in self.online_clients:
                self.online_clients[client_addres] = client_socket

            # Запускаем поток для обработки данных клиента
            threading.Thread(target=self.data_thread, args=(client_socket, client_addres)).start()

def Main():
    # Инициализируем сервер на localhost'е
    server = Server('127.0.0.1', 5555)
    # Запускаем шарманку
    server.start()

if __name__ == '__main__':
    Main()
