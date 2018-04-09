import socket

# Инициализируем сокет
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Подключаемся к localhost'у
client_socket.connect(('127.0.0.1', 5555))

while True:
    # Ввод данных для отправки на сервер
    msg = str(input('> '))
    # Отправка данных на сервер
    client_socket.sendall(str.encode(msg))
