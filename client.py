#CLIENT CODE

import socket
import select
import sys

usage = "Usage: python client.py hostname port"
MODE = "DEFAULT"
exitModeNext = False

#The different groups 
modeDic = {
	'ag' : 'All Groups',
	'sg'  : 'Subscribed Groups',
	'rg' : 'Read Group',
	'rgp'  : 'Read Group Post',

};

def client():
	#check arguments
	if len(sys.argv) < 3:
		print(usage)
		sys.exit()
	#assign the args
	host = sys.argv[1]
	port = int(sys.argv[2])
	#variables
	ps = False
	writePost = False
	post = ""
	#create socket
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
		try:
			socket_list = [sys.stdin, s]

			#select on sockets
			read, write, error = select.select(socket_list, [], [])
			
			for sock in read:
				#message from server
				#receive from server
				if sock == s:
					data = sock.recv(4096)
					if not data:
						print("Disconnected from the Server")
						sys.exit()
					else:
						#split data from server
						dataList = data.split("\a.\a.") 
						#boolean for post subject
						if(dataList[0] == "Enter Post Subject: "):
							ps = True
							dataList[0] = dataList[0] + "(Enter \'$\' to end posting.)"
						#boolean for writing post
						if(dataList[0] == "Post: "):
							writePost = True
						#print data received from server
						if(dataList[0] == "User is not logged in\n"):
							dataList[0] =  dataList[0] + "So Log In" 
							#print("Log in")
							set_mode("DEFAULT")
							dp = True
							
						sys.stdout.write(dataList[0] +'\n')
						sys.stdout.flush()		
						if(len(dataList) > 1):
							if(dataList[1] == "end"):
								set_exit_next(True)
						else:
							set_exit_next(False)
				else:
					#send message to server
					msg = sys.stdin.readline()
					#split and parse msg to server
					msg_parse = msg.strip().split()
					#make sure user is logged in
					
					#check what client is sending
					if(len(msg_parse) > 0):
						#check if user is logging in or out
						if msg.strip() == "logout":
							s.send(msg)
							sys.exit()
						elif msg_parse[0] == "login":
							s.send(msg)
						#for the different modes, send the proper protocol to the server.
						
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
						#create post text to submit
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
							#		print(msg_parse)
							#		print(MODE)
									print("Invalid sub-command, no mode was specified")            
						elif(msg.strip() == "help"):
							s.send("help")
						else:
							print("Invalid sub-command for mode " + MODE)
		except Exception as e:	
			#print str(e)
			continue
                


#set the current mode
def set_mode(string):
	global MODE	
	if(string == "DEFAULT" and MODE != "DEFAULT"):
		print("Exited " + modeDic[MODE] + " mode")
	elif(string == "DEFAULT"):
		print("Invalid sub-command, no mode was specified") 
	MODE = string
        
def set_exit_next(b):
	global exitModeNext
	exitModeNext = b
if __name__ == "__main__":
	sys.exit(client())
