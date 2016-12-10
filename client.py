#CLIENT CODE

import socket
import select
import sys

usage = "Usage: python client.py hostname port"


def client():
	if len(sys.argv) < 3:
		print(usage)
		sys.exit()

	host = sys.argv[1]
	port = int(sys.argv[2])

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)

	#connect to host
	try:
		s.connect((host,port))
	except:
		print("Cannot connect")
		sys.exit()

	print("Connected to Server")

	while True:
		socket_list = [sys.stdin, s]

		#select on sockets
		read, write, error = select.select(socket_list, [], [])
		
		for sock in read:
			#message from server
			if sock == s:
				data = sock.recv(4096)
				if not data:
					print("Not connected to Server")
					sys.exit()
				else:
					#print server message
					sys.stdout.write(data +'\n')

					sys.stdout.flush()
			else:
				#send message to server
				msg = sys.stdin.readline()
				s.send(msg)
				if msg.strip() == "logout":
					sys.exit()

if __name__ == "__main__":
	sys.exit(client())