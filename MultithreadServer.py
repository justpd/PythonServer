import socket
import json
import threading
from Handler import HandleData, DisconnectUser

# Создаём класс, контролирующий закачку больших данных
class Storage():
    
    # Инициализируем хранилище для подкачки данных клиента
    def __init__(self):
        self.data = bytes()
        self.size = 0
    
    # Проверям завершилась ли подкачка
    def is_done(self):
        return len(self.data) == self.size
    

class Server():
    
    # Инизиализируем сервер
    def __init__(self, ip, port):
        # Инициализируем сокет
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        print('Server > running on {}:{}'.format(ip, port))
    
    # Отдельный поток обработки данных для клиента
    def data_thread(self, client_socket, client_address):
        try:
            storage = Storage()
            # Цикл считывания данных от клиента через его client_socket
            while True:
                # Получаем данные
                data = client_socket.recv(2048)

                # Проверка на целостность данных
                if not data:
                    break

                # Если сейчас не идет подгрузка файла от этого клиента, то обрабатываем новые запросы
                if (storage.size == 0):
                    # Данные, которые мы получаем состоят из трёх частей:
                    # > Ключ пакета (4 байта)
                    # > Размер чистых данных, не учитывая ключ и саму информацию о размере (4 байта)
                    # > Данные на обработку (с 8ого байта до конца)

                    # Ключ пакета, который хранится в NetworkPackets
                    index = int.from_bytes(bytes(data[0:4]), byteorder='little')
                    # Размер полученных данных в байтах (размер чистых данных + 8 байт информации о пакете)
                    size = 8 + int.from_bytes(bytes(data[4:8]), byteorder='little')

                    # Если размер не больше 2Кб - значит мы смогли получить все данные за раз, можем их обрабатывать
                    if (size <= 2048):
                        # Чистые данные, подлежащие обработке
                        data = bytes(data[8:]).decode("utf-8")
                        # Вызов главного "Хэндлера"
                        HandleData(client_socket, index, size, data)
                    # Иначе - начинаем подкачку данных
                    else:
                        storage.size = size
                        storage.data += bytes(data)
                # Иначе - получаем данные текущей подгрузки
                else:
                    storage.data += bytes(data)
                    # Если длинна полученных данных равна размеру подкачиваемого файла > файл успешно загружен
                    if (storage.is_done()):
                        print('Load finished..')

                        index = int.from_bytes(bytes(storage.data[0:4]), byteorder='little')
                        data = bytes(storage.data[8:]).decode("utf-8")
                        HandleData(client_socket, index, storage.size, data)

                        storage = Storage()
                    # Иначе - выводим состояние подкачки
                    else:
                        percent = len(storage.data) / storage.size
                        print('Loading ..... ({:.2f}%)'.format(percent * 100))
        except Exception as e:
            DisconnectUser(client_socket)
            client_socket.close()
            try:
                del self.clients[client_address]
            except KeyError:
                pass
            print('{}:{} disconnected.'.format(client_address[0], client_address[1]))

            print(e)
    # Запускаем шарманку
    def start(self):
        # Создаём пустой словарь для хранения списка клиентов key = (ip,port), value = socket
        self.clients = {}
        # Начинаем прослушивать входящие соединения
        self.server_socket.listen(10)

        # Основной цикл обработки соединений
        while True:
            try:
                # Получаем сокет и адресс (ip, port) клиента, который подключился
                client_socket, client_address = self.server_socket.accept()

                # Если клиента еще нет в списке онлайн клиентов - добавляем его
                if client_address not in self.clients:
                    self.clients[client_address] = client_socket
                    print(self.clients)
                    print('{}:{} connected.'.format(client_address[0], client_address[1]))

                # Запускаем новый поток для обработки данных клиента
                threading.Thread(target=self.data_thread, args=(client_socket, client_address)).start()

            # При разрыве соединения с сокетом клиента
            except Exception as e:
                client_socket.close()
                try:
                    del self.clients[client_address]
                except KeyError:
                    pass
                print('{}:{} disconnected.'.format(client_address[0], client_address[1]))

                print(e)
    
    # Сворачиваемся
    def close(self):
        self.server_socket.close()

def Main():
    print('Starting server on:')
    ip = input('ip: ')
    port = int(input('port: '))
    server = Server(ip, port)
    server.start()

if __name__ == '__main__':
    Main()
