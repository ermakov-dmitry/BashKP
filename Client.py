import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создаем сокет
sock.connect(('localhost', 55000))  # подключемся к серверному сокету
sock.send(bytes('Hello, world', encoding='UTF-8'))  # отправляем сообщение
data = sock.recv(1024)  # читаем ответ от серверного сокета
data.decode('utf-8')
sock.close()  # закрываем соединение
print(data)
