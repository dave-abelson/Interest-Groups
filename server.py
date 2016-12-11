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

help_menu = "SEND HELP SUSAN!!!! HALP"

conn = sqlite3.connect('./database/InterestDB.db')
conn.row_factory = sqlite3.Row
connCursor = conn.cursor()

class User:
	def __init__(self, username, socket):
		self.username = username
		self.socket = socket
		self.groupList = []
		self.numLineToRead = 0 
		self.groupIndex = 0 
		self.postIndex = 0
		self.readingGroup = None
		
	def reset(self):
		self.groupList = []
		self.numLineToRead = 0
		self.groupIndex = 0
		self.postIndex = 0
		self.readingGroup = None

class Group:
	def __init__(self, groupname, groupID):
		self.groupname = groupname
		self.groupID = groupID
		self.isSubscribed = False
		self.posts = []
	
class Posts:
	def __init__(self, subject, username, weekDay, datetime, timezoneYear, post, groupId):
		self.subject = subject
		self.username = username
		self.weekDay = weekDay
		self.datetime = datetime
		self.timezoneYear = timezoneYear
		self.post = post
		self.groupId = groupId
		self.new = True

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
				try:
					#process client data
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
							if(getUserBySocket(sock) is not None):
								o=0 #LAZY WAY TO IGNORE A CONDITION
							elif len(data_list) < 2:
								sock.send(help_menu)
							else:
								user = loginUser(data_list[1], sock)
								user_list.append(user) 
								print(data_list[1] + " has logged in")
								sock.send(data_list[1] + " has logged in")
						#arg command
						elif(isUserLoggedIn(sock)):
							if data_list[0] == "ag":
								if len(data_list)<2:
									get_groups(DEFAULT, sock)
								else:
									if(data_list[1] == "s"):
										subscribeGroups(data_list, sock)
									elif(data_list[1] == "u"):
										unsubscribeGroups(data_list, sock)
									elif(data_list[1] == "n"):
										print_restGroups(sock, "ag")
									elif(data_list[1] == "q"):
										set_mode("DEFAULT")
									elif(data_list[1].isdigit()):
										get_groups(int(data_list[1]), sock)
									else:
										sock.send(help_menu)
							#sg command
							elif data_list[0] == "sg":
								if len(data_list)<2:
									get_subscribeGroups(DEFAULT, sock, True)
								else:
									if(data_list[1] == "n"):
										print_restGroups(sock, "sg")
									elif(data_list[1] == "u"):
										unsubscribeGroups(data_list, sock)
									elif(data_list[1] == "q"):
										set_mode("DEFAULT")
									elif(data_list[1].isdigit()):
										get_subscribeGroups(int(data_list[1]), sock, True)
									else:
										sock.send(help_menu)
							elif data_list[0] == "rg":
								if(len(data_list) == 2):
									if(data_list[1] == "n"):
										send_restPostlist(sock)
									elif(getGroupByGroupName(data_list[1], getSubscribedGroupList(sock)) is not None):
										print("GOT HERE")
										send_resultRG(DEFAULT,data_list, sock)
									else:
										print("FAIL")
								else:
									if(data_list[2].isdigit()):
										send_resultRG(int(data_list[2]),data_list, sock)
									else:
										sock.send(help_menu)
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
						else:
							sock.send("User is not logged in\n")
							sock.send(help_menu)
				except Exception as e: 
					#send out
					print("DAVE YOU IDIOT")
					print str(e)
					continue

	server_socket.close()
	
# For command AG
# @para N number of groups to print or default value
def loginUser(username, socket):
	usersDB = accessSQL("SELECT * FROM users")
	for u in usersDB:
		if(u['userId'] == username):
			return User(username, socket)
	accessSQL("INSERT INTO users VALUES (\'" + username + "\')")
	#print("HERE")
	return User(username, socket)

def isUserLoggedIn(sock):
	if(getUserBySocket(sock) is not None):
		return True
	else:
		return False
	
def accessSQL(statement):
	connCursor.execute(statement)
	dbreturned = connCursor.fetchall()
	conn.commit()
	return dbreturned

def getUserBySocket(sock):
	for u in user_list:
		if(u.socket == sock):
			return u
	return None
	
def getUserByUserName(userName):
	for u in user_list:
		if(u.socket == userName):
			return u
	return None

def getGroupByGroupName(groupName, groupList):
	for g in groupList:
		if(g.groupname == groupName):
			return g
	return None
	
def getSubscribedGroupList(sock):
	user = getUserBySocket(sock)
	query = "SELECT * FROM groups, subscription WHERE subscription.userId == \'%s\' and groups.groupID == subscription.groupID" % (user.username)
	groupsDB = accessSQL(query)
	groupList = []
	for g in groupsDB:
		groupModel = Group(g['groupName'], g['groupID'])
		groupList.append(groupModel)
		groupModel.isSubscribed = True
	return groupList
	
def get_groups(N, sock):
	#for loop	
	groupsDB = accessSQL("SELECT * FROM groups")
	user = getUserBySocket(sock)	
	subscriptions = accessSQL("SELECT * FROM subscription")
	user.reset()
	for g in groupsDB:
		groupModel = Group(g['groupName'], g['groupID'])
		user.groupList.append(groupModel)
		for s in subscriptions:
			if(s['groupID'] == g['groupID'] and s['userId'] == user.username):
				groupModel.isSubscribed = True		
	user.numLineToRead = N
	sendGroup(user,user.groupIndex, user.groupIndex + N, sock, "ag")
	
	
def get_subscribeGroups(N, sock, send):
	user = getUserBySocket(sock)
	query = "SELECT * FROM groups, subscription WHERE subscription.userId == \'%s\' and groups.groupID == subscription.groupID" % (user.username)
	groupsDB = accessSQL(query)
	user.reset()
	for g in groupsDB:
		groupModel = Group(g['groupName'], g['groupID'])
		user.groupList.append(groupModel)
		groupModel.isSubscribed = True
	user.numLineToRead = N
	if(send == True):
		sendGroup(user,user.groupIndex, user.groupIndex + N, sock, "sg")

def sendGroup(user ,start, end, sock, mode):
	s = ""
	for x in range(start, end):
		if(x >= len(user.groupList)):
			break
		if(mode == "ag"):
			if(user.groupList[x].isSubscribed):
				s = s + str(x+1) + ". (S) " + user.groupList[x].groupname + "\n"
			else:
				s = s + str(x+1) + ". ( ) " + user.groupList[x].groupname + "\n"
		elif(mode == "sg"):
			npNum = markReadPost(user.groupList[x], user)
			s = s + str(x+1) + ".\t" + str(npNum) + "\t" + user.groupList[x].groupname + "\n"
		user.groupIndex += 1
	sock.send(s)
	if(x >= len(user.groupList)):
		sock.send("\a.\a.end")
		
#ONLY WORKS IF THE GROUP IS IN THE USER LIST
#ALSO RETURNS THE NUMBER OF NEW POSTS
#ALSO FILLS IN THE POSTS TO THE GROUP
def markReadPost(group, user):
	getGroupPosts(group)
	query = "SELECT * FROM postStatus"
	readPost = accessSQL(query)
	x = len(group.posts)
	for p in group.posts:
		for rp in readPost:
			if(rp['groupId'] == p.groupId and rp['subject'] == p.subject):
				p.new = False
				x -= 1
	return x
	

def getGroupPosts(group):
	query = "SELECT * FROM posts WHERE posts.groupId = %d" % group.groupID
	postsDB = accessSQL(query)
	for p in postsDB:  
		postModel = Posts(p['subject'], p['userId'], p['weekDay'], p['date_time'], p['timeZone_year'], p['post'], p['groupId'])
		group.posts.append(postModel)
	
	
# For command AG or SG
# @para N number of groups to print or default value
def subscribeGroups(data_list, sock):
	if len(data_list)<3:
		sock.send(help_menu)
	else:
		for x in range(2, len(data_list)):
			user = getUserBySocket(sock)
			subscribedGroup = user.groupList[int(data_list[x]) - 1]
			accessSQL("INSERT INTO subscription VALUES (\'" + str(subscribedGroup.groupID)  + "\',\'" + user.username + "\')")
	#reset counter
	return True

#For command AG or SG
def unsubscribeGroups(data_list, sock):
	if len(data_list)<3:
		sock.send(help_menu)
	else:
		for x in range(2, len(data_list)):
			user = getUserBySocket(sock)
			subscribedGroup = user.groupList[int(data_list[x]) - 1]		
			query = "DELETE FROM subscription WHERE groupID = %d and userId = \'%s\'" % (subscribedGroup.groupID, user.username)
			accessSQL(query)
	return True

def print_restGroups(sock, mode):
	user = getUserBySocket(sock)
	print(user.groupIndex)
	sendGroup(user, user.groupIndex, user.groupIndex + user.numLineToRead, sock, mode)
	#reset counter
	return True
def print_post(sock):
	final_str = "" 
	final_str = final_str + "Group: " + "put" + "\n"
	final_str = final_str + "Subject: " + "put" + "\n"
	final_str = final_str + "Author: " + "put" + "\n"
	final_str = final_str + "Date: " + "put" + "\n"

	sock.send(final_str)

#Prints for commands AG and SG
def print_result_AG_SG(final_str, data_list, sock):

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
def send_resultRG(N,data_list ,sock):        
	get_subscribeGroups(0, sock, False)
	user = getUserBySocket(sock)
	user.readingGroup = getGroupByGroupName(data_list[1], user.groupList)
	print(user.readingGroup)
	#TODO CHECK IF READING GROUP IS NONE
	markReadPost(user.readingGroup, user)
	print(user.readingGroup.posts)
	user.numLineToRead = N
	sendGroupPostlist(user, user.postIndex, user.postIndex + N, sock)

def send_restPostlist(sock):
	user = getUserBySocket(sock)
	sendGroupPostlist(user, user.postIndex, user.postIndex + user.numLineToRead, sock)
	
def sendGroupPostlist(user ,start, end, sock):
	s = ""
	for x in range(start, end):
		if(x >= len(user.readingGroup.posts)):
			break
		p = user.readingGroup.posts[x]
		if(p.new):
			s = s + str(x+1) + ". N \t" + p.datetime + "\t" + p.subject + "\n"
		else:
			s = s + str(x+1) + ".   \t" + p.datetime + "\t" + p.subject + "\n"			
		user.postIndex += 1
	sock.send(s)
	if(x >= len(user.readingGroup.posts)):
		sock.send("\a.\a.end")

#set the cu
def set_mode(string):
	MODE = string
	

if __name__ == "__main__":
	server()
	sys.exit()
