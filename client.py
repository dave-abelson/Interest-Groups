#CLIENT CODE

import socket
import select
import sys

usage = "Usage: python client.py hostname port"
MODE = "DEFAULT"


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
                        #receive from server
			if sock == s:
				data = sock.recv(4096)
				if not data:
					print("Not connected to Server")
					sys.exit()
				else:
					#print server message
					sys.stdout.write(data +'\n')
					

					sys.stdout.flush()
					
			#receive from server
			else:
				#send message to server
				msg = sys.stdin.readline()
				msg_parse = msg.strip().split()
				if msg.strip() == "logout":
                                        s.send(msg)
					sys.exit()

				#command mode AG	
				elif(msg_parse[0]=="ag"):
                                        set_mode("ag") 
                                        s.send(msg)
                                        
                                #command mode SG                
                                elif(msg_parse[0]=="sg"):
                                        set_mode("sg")
                                        s.send(msg)

                                #command mode RG        
                                elif(msg_parse[0]=="rg"):
                                        set_mode("rg")
                                        s.send(msg)        
                                        
                                elif(msg_parse[0]=="s"):
                                        if(MODE=="sg"):
                                                arg_str = "sg " + msg
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
                                                
                                elif(msg_parse[0]=="p" || msg_parse[0]=="r"):
                                        if(MODE=="rg"):
                                                arg_str = "rg " + msg
                                                send(arg_str)
                                        else:
                                                print("Invalid sub-command for mode " + MODE)
                                elif(msg_parse[0]=="q"):
                                        set_mode("DEFAULT")

                                elif(msg_parse[0]=="n"):
                                        if(MODE=="sg"):
                                                arg_str = "sg " + msg
                                                s.send(arg_str)
                                        elif(MODE=="ag"):
                                                arg_str = "ag " + msg
                                                s.send(arg_str)
                                        elif(MODE=="rg"):
                                                arg_str = "rg " + msg
                                                s.send(arg_str)

                                        else:
                                                 print("Invalid sub-command, no mode was specified")
                                        
                                     
                


#set the current mode
def set_mode(string):
        MODE = string
        
if __name__ == "__main__":
	sys.exit(client())
