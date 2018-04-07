import socket
import json
from Handler import HandleData

# Инициализируем сокет
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.1.8', 8867 ))
print('Server > 192.168.1.8:8867')

# Создаём пустой словарь для хранения списка клиентов key = (ip,port), value = socket
clients = {}

# Создаём переменные, контролирующие закачку больших данных
storage = bytes()
loadingSize = 0
loading = False

# Начинаем прослушивать входящие соединения
server_socket.listen(10)

# Основной цикл обработки соединений
while True:
    try:
        # Получаем сокет и адресс (ip, port) клиента, который подключился
        client_socket, addr = server_socket.accept()

        # Если клиента еще нет в списке онлайн клиентов - добавляем его
        if addr not in clients:
            clients[addr] = client_socket
            print(clients)
            print('{}:{} connected.'.format(addr[0], addr[1]))
        
        # Цикл считывания данных от клиента через его client_socket
        while True:
            # Получаем данные
            data = client_socket.recv(4096)
            
            # Проверка на целостность данных
            if not data:
                break

            # Если сейчас не идет подгрузка файла от этого клиента, то обрабатываем новые запросы
            if (not loading):
                # Данные, которые мы получаем состоят из трёх частей:
                # > Ключ пакета (4 байта)
                # > Размер чистых данных, не учитывая ключ и саму информацию о размере (4 байта)
                # > Данные на обработку (с 8ого байта до конца)

                # Ключ пакета, который хранится в NetworkPackets
                index = int.from_bytes(bytes(data[0:4]), byteorder='little')
                # Размер полученных данных в байтах (размер чистых данных + 8 байт информации о пакете)
                size = 8 + int.from_bytes(bytes(data[4:8]), byteorder='little')

                print('Size: ' + str(size))

                # Если размер не больше 2Кб - значит мы смогли получить все данные за раз, можем их обрабатывать
                if (size <= 2048):
                    # Чистые данные, подлежащие обработке
                    data = bytes(data[8:]).decode("utf-8")
                    # Вызов главного "Хэндлера"
                    HandleData(client_socket, index, size, data)
                # Иначе - начинаем подкачку данных
                else:
                    loading = True
                    loadingSize = size
                    storage += bytes(data)

            # Иначе - получаем данные текущей подгрузки
            else:
                storage += bytes(data)
                # Если длинна полученных данных равна размеру подкачиваемого файла > файл успешно загружен
                if (len(storage) == loadingSize):
                    print('Load finished..')

                    index = int.from_bytes(bytes(storage[0:4]), byteorder='little')
                    data = bytes(storage[8:]).decode("utf-8")
                    HandleData(client_socket, index, loadingSize, data)

                    storage = bytes()
                    loading = False
                    loadingSize = 0
                
                # Иначе - выводим состояние подкачки
                else:
                    percent = len(storage) / loadingSize
                    print('Loading ..... ({:.2f}%)'.format(percent * 100))
    
    # При разрыве соединения с сокетом клиента
    except Exception as e:
        client_socket.close()
        try:
            del clients[addr]
        except KeyError:
            pass
        print('{}:{} disconnected.'.format(addr[0], addr[1]))

        print(e)

# При сбое на сервере закрываем свой сокет
server_socket.close()
