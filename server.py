#SERVER CODE

import socket
import sys
import time
import select
import sqlite3

LIST_SOCKETS = []
HOST = "localhost"
PORT = 8000
BUFF = 1024

user_list = []
global_ID = 0

help_menu = "MAKE HELP MENU"

class User:
	def __init__(self, username, ID, socket):
		self.username = username
		self.ID = ID
		self.socket = socket


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
						data_list = data.strip().split()
						#help menu
						if data.strip() == "help":
							sock.send(help_menu)
						elif data_list[0] == "login":
							if len(data_list) < 2:
								sock.send(help_menu)
							else:
								global global_ID #access global variables
								user = User(data_list[1], 0, sock)
								global_ID = global_ID + 1
								user_list.append(user)
								print(data_list[1] + " has logged in")
								sock.send(data_list[1] + " has logged in")
						elif data.strip() == "logout":
							sock.send("Bye")
							LIST_SOCKETS.remove(sock)
							for i in user_list:
								if i.socket == sock:
									user_list.remove(i)
					else:
						#remove socket
						if sock in LIST_SOCKETS:
							LIST_SOCKETS.remove(sock)
				except Exception as e: 
					#send out
					print("DAVE YOU IDIOT")
					print str(e)
					continue

	server_socket.close()			


if __name__ == "__main__":
	sys.exit(server())