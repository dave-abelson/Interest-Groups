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
DEFAULT = 10
DISPLAY_GP_FLAG = -1
MODE = "DEFAULT"
COUNTER = 0
GROUP_LIST = []

user_list = []
global_ID = 0

help_menu = "MAKE HELP MENU"

class User:
	def __init__(self, username, ID, socket):
		self.username = username
		self.ID = ID
		self.socket = socket

class Group:
        def __init__(self, groupname, groupID, isSubscribed):
                self.groupname = groupname
                self.groupID = groupID
                self.isSubscribed = isSubscribed

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

						#arg command
						elif data_list[0] == "ag":
                                                        if len(data_list)<2:
                                                                get_group(DEFAULT)
                                                        else:
                                                                if(data_list[1] == "s"):
                                                                        subscribeGroup(data_list)
                                                                elif(data_list[1] == "u"):
                                                                        unsubscribeGroup(data_list)
                                                                elif(data_list[1] == "n"):
                                                                        print_restGroups()
                                                                elif(data_list[1] == "q"):
                                                                
                                                                else:
                                                                        sock.send(help_menu)
                                                                get_group(data_list[1])
                                                #sg command
                                                elif data_list[0] == "sg":
                                                        if len(data_list)<2:
                                                                get_subscribeGroups(DEFAULT)
                                                        else:
                                                                set_mode("sg")
                                                                get_subscribeGroups(data_list[1])

                                                #check for mode and specific sub_command for each mode
                                                elif data_list[0] == "s" || data_list[0] == "u"
                                                        || data_list[0] == "n" || data_list[0] == "q":
                                                        if(MODE=="ag"):
                                                                if(data_list[0] == "s"):
                                                                        subscribeGroup(data_list)
                                                                elif(data_list[0] == "u"):
                                                                        unsubscribeGroup(data_list)
                                                                elif(data_list[0] == "n"):
                                                                        print_restGroups()
                                                                elif(data_list[0] == "q"):
                                                                        set_mode("DEFAULT")
                                                                else:
                                                                        sock.send(help_menu)
                                                        elif(MODE=="sg"):
                                                                elif(data_list[0] == "u"):
                                                                        unsubscribeGroup(data_list)
                                                                elif(data_list[0] == "n"):
                                                                        print_restGroups()
                                                                elif(data_list[0] == "q"):
                                                                        set_mode("DEFAULT")
                                                                else:
                                                                        sock.send(help_menu)        
                                                        else:
                                                                sock.send(help_menu)
                                                                
                                                #logout
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
	
# For command AG
# @para N number of groups to print or default value
def get_groups(N):
        MODE = "ag"
        #for loop
                print_result_AG_SG()


# For command AG or SG
# @para N number of groups to print or default value
def subscribeGroups(data_list):
        if len(data_list)<2:
                sock.send(help_menu)
        elif:
                for a in range(1, len(data_list))
                        #subcribe here

        #reset counter
        return True

#For command AG or SG
def unsubscribeGroups(data_list):
        final_str = ""
        if len(data_list)<2:
                sock.send(help_menu)
        else:
                for a in range(1, len(data_list))
                        #unsubscribe here
                

        #reset counter
        return True

def print_restGroups():
        if len(data_list)<2:
                sock.send(help_menu)
        elif

        #reset counter
        return True
def print_post():
        final_str = "" 
        final_str = final_str + "Group: " + "put" + "\n"
        final_str = final_str + "Subject: " + "put" + "\n"
        final_str = final_str + "Author: " + "put" + "\n"
        final_str = final_str + "Date: " + "put" + "\n"

        sock.send(final_str)

#Prints for commands AG and SG
def print_result_AG_SG(final_str, data_list):

        #print group counter 
        print(counter + ". ")

        if(MODE=="ag"):
                #check if the current user is subscribed to this specific group
                if():
                        print("(" + "put status here" + ")  ")
                else:
                        print("( )")
        elif(MODE=="sg"):
                #print the number of unread/new posts or empty string
                print("put number of unread/new post here" + "  ")
                
        #print the group name
        print("put here")

#Prints for command RG
#Order them by unread/new posts first
def print_resultRG():        
        #print group counter 
        print(counter + ". ")

        #status of the post, "N" for unread/new post or empty string for read
        print(" put N or empty space" + " ")

        #date and time of the post
        print("put date/time here" + " ")

        #sibject of the post
        print("put subject of post here")

#set the cu
def set_mode(string):
        MODE = string
        

if __name__ == "__main__":
	sys.exit(server())
