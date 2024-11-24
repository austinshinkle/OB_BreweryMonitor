import socket

#Addi is awesome!
#ip = "192.168.178.55"
server_ip = "ashinkl-rpi4"
server_port = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip,server_port))

data = client_socket.recv(1024)
print("Received from server:", data.decode())

#client_socket.sendall(b'Hello Server!')

client_socket.close()
