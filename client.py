#CLIENT CODE

import socket
import select
import sys

usage = "Usage: python client.py hostname port"
MODE = "DEFAULT"
exitModeNext = False

modeDic = {
	'ag' : 'All Groups',
	'sg'  : 'Subscribed Groups',
	'rg' : 'Read Group',
	'rgp'  : 'Read Group Post',
};

def client():
	if len(sys.argv) < 3:
		print(usage)
		sys.exit()

	host = sys.argv[1]
	port = int(sys.argv[2])
	ps = False
	writePost = False
	post = ""

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
            #receive from server
			if sock == s:
				data = sock.recv(4096)
				if not data:
					print("Not connected to Server")
					sys.exit()
				else:
					dataList = data.split("\a.\a.") 
					if(dataList[0] == "Enter Post Subject: "):
						ps = True
					if(dataList[0] == "Post: "):
						writePost = True
					sys.stdout.write(dataList[0] +'\n')
					sys.stdout.flush()		
					if(len(dataList) > 1):
						if(dataList[1] == "end"):
							set_exit_next(True)
			else:
				#send message to server
				msg = sys.stdin.readline()

				msg_parse = msg.strip().split()
				if(msg == "User is not logged in\n"):
					print("Log in")
					set_mode("DEFAULT")

				if(len(msg_parse) > 0):
					if msg.strip() == "logout":
						s.send(msg)
						sys.exit()
					elif msg_parse[0] == "login":
						s.send(msg)
					#command mode AG	
					elif(msg_parse[0]=="ag"):
						if(MODE == "DEFAULT"):						
							set_mode("ag") 
							s.send(msg)
						else:
							print("Invalid sub-command for mode " + MODE)											
					#command mode SG                
					elif(msg_parse[0]=="sg" and MODE == "DEFAULT"):
						if(MODE == "DEFAULT"):	
							set_mode("sg")
							s.send(msg)
						else:
							print("Invalid sub-command for mode " + MODE)	
					#command mode RG        
					elif(msg_parse[0]=="rg" and MODE == "DEFAULT" and len(msg_parse) > 1):
						if(MODE == "DEFAULT"):	
							set_mode("rg")
							s.send(msg)        
						else:
							print("Invalid sub-command for mode " + MODE)	
					elif(msg_parse[0]=="s"):
						if(MODE=="sg"):
							arg_str = "sg " + msg
							s.send(arg_str)							
						elif(MODE=="ag"):
							arg_str = "ag " + msg
							s.send(arg_str)
						else:
							print("Invalid sub-command for mode " + MODE)  
					elif(msg_parse[0]=="u"):
						if(MODE=="sg"):
							arg_str = "sg " + msg
							s.send(arg_str)
						elif(MODE=="ag"):
							arg_str = "ag " + msg
							s.send(arg_str)
						else:
							print("Invalid sub-command, no mode was specified")
					elif(ps):
						s.send(msg)	
						ps = False	
					elif(writePost):
						if(msg_parse[0] == "$"):
							s.send(post)
							post = ""
							writePost = False
						else:
							post = post + "\n" + msg
					elif(msg_parse[0]=="p" or msg_parse[0]=="r" or msg_parse[0][0] == "["):
						if(MODE=="rg"):
							arg_str = "rg " + msg
							s.send(arg_str)
						else:
							print("Invalid sub-command for mode " + MODE)
					elif(msg_parse[0]=="q"):
						if(MODE != "rgp"):
							set_mode("DEFAULT")
						else:
							set_mode("rg")
					elif(msg_parse[0]=="n"):
						if(exitModeNext):
							set_mode("DEFAULT")
							set_exit_next(False)
						else:
							if(MODE=="sg"):
								arg_str = "sg " + msg
								s.send(arg_str)
							elif(MODE=="ag"):
								arg_str = "ag " + msg
								s.send(arg_str)
							elif(MODE=="rg"):
								arg_str = "rg " + msg
								s.send(arg_str)
							elif(MODE=="rgp"):
								arg_str = "rgp " + msg
							elif(MODE=="DEFAULT"):
								print(msg_parse)
								print(MODE)
								print("Invalid sub-command, no mode was specified")            
					elif(msg.strip() == "help"):
						s.send("help")
					else:
						print("HEREEE")
						print("Invalid sub-command for mode " + MODE)
                


#set the current mode
def set_mode(string):
	global MODE	
	if(string == "DEFAULT"):
		print("Exited " + modeDic[MODE] + " mode")
	MODE = string
        
def set_exit_next(b):
	global exitModeNext
	exitModeNext = b
if __name__ == "__main__":
	sys.exit(client())
