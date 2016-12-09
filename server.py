#SERVER CODE

import socket
import sys
import time
import select

LIST_SOCKETS = []
HOST = "localhost"
PORT = 5539
BUFF = 1024

def server():
	#establish server socket
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((HOST, PORT))
	server_socket.listen(10)

	LIST_SOCKETS.append(server_socket)
	print("Server started on port " + str(PORT))

	while True:
		#look at sockets
		read, write, error = select.select(LIST_SOCKETS, [], [], 0)

		for sock in read:
			#connection received
			if sock == server_socket:
				sockfd, addr = server_socket.accept()
				LIST_SOCKETS.append(sockfd)
				print("Client (%s,%s) connected" % addr)

				#broadcast
			#received from client
		else:
			#process client data
			try:
				#data from socket
				data = sock.recv(BUFF)
				if data:
					#deal with data
					print(str(data))
				else:
					#remove socket
					if sock in LIST_SOCKETS:
						LIST_SOCKETS.remove(sock)
			except:
				#send out
				continue

	server_socket.close()			


if __name__ == "__main__":
	sys.exit(server())