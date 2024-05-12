import socket

#ip = "192.168.178.55"
#host = "localhost"
host = "192.168.178.55"
port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host,port))

server_socket.listen(5)

print("Server listening on {}:{}".format(host,port))

i = 0

try:
	while True:
		client_socket, addr = server_socket.accept()
		print("Got connection from", addr)

		string = "Hello client! This is server!" + str(i)

		client_socket.send(str.encode(string))
		
		client_socket.close()
		
		i += 1

except KeyboardInterrupt:
	print('Script cancelled by user!')
	server_socket.close()
