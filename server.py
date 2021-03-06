#SERVER CODE

import socket
import sys
import select
import sqlite3
import datetime
import threading

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

help_menu = "\nHELP MENU: \n\n"
ag_menu = "\nAG MODE sub-command options: \n\ns  [s N] | [s] subscribe to a group. \nu  [u N] unsubscribe from group. \nn  display remaining groups or exit if all displayed. \nq  quit from mode\n"
sg_menu = "\nSG MODE sub-command options: \n\nu  [u N] unsubscribe from group. \nn  display remaining groups or exit if all displayed. \nq  quit from mode\n"
rg_menu = "\nRG MODE sub-command options: \n\n[id]  select a number denoting a post to display.]nr  marks a post as read. \np  post to the group. \nn  display remaining groups or exit if all displayed. \nq  quit from mode\n"
login_menu = "\nInvalid argument for login. Please include your USER ID.\n"
error_msg = "\nInvalid sub_commands for\n"
#conn = sqlite3.connect('./database/InterestDB.db')
#conn.row_factory = sqlite3.Row
#connCursor = conn.cursor()

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
	server_socket.bind(("", PORT))
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
				#open thread for client
				t = threading.Thread(target = userThread, args = (sockfd,))
				t.start()
				LIST_SOCKETS.remove(sockfd)
				#broadcast
		
	server_socket.close()			
#thread for individual users
def userThread(sock):
	while True:

		try:
			#process client data
			#data from socket
			data = sock.recv(BUFF)
			if data:
				#deal with data
		#		print(str(data))
				data_list = data.strip().split()
						
				#help menu
				if data.strip() == "help":
					sock.send(help_menu)
					sock.send(ag_menu)
					sock.send(sg_menu)
					sock.send(rg_menu)
				elif data_list[0] == "login":
					if(getUserBySocket(sock) is not None):
						o=0 #LAZY WAY TO IGNORE A CONDITION
					elif len(data_list) < 2:
						sock.send(login_menu)
					else:
						user = loginUser(data_list[1], sock)
						user_list.append(user) 
						# print(data_list[1] + " has logged in")
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
								sock.send(ag_menu)
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
								sock.send(sg_menu)
					#rg command
					elif data_list[0] == "rg":
						if(len(data_list) == 2):
							if(data_list[1] == "n"):
								send_restPostlist(sock)		
							elif(data_list[1] == "p"):
								createNewPost(sock)	
							elif(data_list[1][0] == "["):
								strId = data_list[1][1:]
								strId = strId[:-1]

								readPost(int(strId), sock)
							elif(getGroupByGroupName(data_list[1], getSubscribedGroupList(sock)) is not None):
						#		print("GOT HERE")
								send_resultRG(DEFAULT,data_list, sock)
							else:
						#		print("Not subscribed")
								sock.send("Not subscribed")
							#	print("FAIL")
						#else
						else:
							if(data_list[1] == "r"):
								if(len(data_list) != 3):
									print("error")
									sock.send(rg_menu)
								else:
									print(data_list[2])
									if(len(data_list[2]) == 1):
										markPostRead(int(data_list[2]), sock)
									else:
										for i in xrange(int(data_list[2][0]), int(data_list[2][-1]) + 1):
											markPostRead(i, sock)
									sock.send("Success!")	
							elif(data_list[2].isdigit()):
								send_resultRG(int(data_list[2]),data_list, sock)
							else:
								sock.send(rg_menu)
					#logout
					elif data.strip() == "logout":
						sock.send("Bye")
						for i in user_list:
							if i.socket == sock:
								user_list.remove(i)
						break
					else:
						#remove socket
						if sock in LIST_SOCKETS:
							LIST_SOCKETS.remove(sock)
				#send user not logged in to client
				else:
					sock.send("User is not logged in\n")
					#sock.send(help_menu)
		#ENSURE SERVER NOT CRASH
		except Exception as e: 
			#send out
			#print("DAVE YOU GENIUS")
			print str(e)
			continue

	
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

#CHECK IF USER IS LOGGED IN
def isUserLoggedIn(sock):
	if(getUserBySocket(sock) is not None):
		return True
	else:
		return False
#ACCESS SQL
def accessSQL(statement):
	conn = sqlite3.connect('./database/InterestDB.db')
	conn.row_factory = sqlite3.Row
	connCursor = conn.cursor()
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
			if(rp['groupId'] == p.groupId and rp['subject'] == p.subject and rp['userId'] == user.username):
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
		sock.send(error_msg+" "+data_list[0])
		sock.send(ag_menu)
	else:
		for x in range(2, len(data_list)):
			user = getUserBySocket(sock)
			subscribedGroup = user.groupList[int(data_list[x]) - 1]
			accessSQL("INSERT INTO subscription VALUES (\'" + str(subscribedGroup.groupID)  + "\',\'" + user.username + "\')")
	#reset counter
		get_groups(DEFAULT, sock)
	return True

#For command AG or SG
def unsubscribeGroups(data_list, sock):
	if len(data_list)<3:
		if(data_list[0]=="ag"):
			sock.send(error_msg+" "+data_list[0])
			sock.send(ag_menu)
		elif(data_list[0]=="sg"):
			sock.send(error_msg+" "+data_list[0])
			sock.send(sg_menu)
	else:
		for x in range(2, len(data_list)):
			user = getUserBySocket(sock)
			subscribedGroup = user.groupList[int(data_list[x]) - 1]		
			query = "DELETE FROM subscription WHERE groupID = %d and userId = \'%s\'" % (subscribedGroup.groupID, user.username)
			accessSQL(query)
		if(data_list[0] == "ag"):
			user = getUserBySocket(sock)
			get_groups(user.numLineToRead, sock)
		else:
			user = getUserBySocket(sock)
			get_subscribeGroups(user.numLineToRead, sock, True)
	return True

def print_restGroups(sock, mode):
	user = getUserBySocket(sock)
	print(user.groupIndex)
	sendGroup(user, user.groupIndex, user.groupIndex + user.numLineToRead, sock, mode)
	#reset counter
	return True




#Prints for command RG
#Order them by unread/new posts first
def send_resultRG(N,data_list ,sock):        
	get_subscribeGroups(0, sock, False)
	user = getUserBySocket(sock)
	user.readingGroup = getGroupByGroupName(data_list[1], user.groupList)
	#print(user.readingGroup)
	#TODO CHECK IF READING GROUP IS NONE
	markReadPost(user.readingGroup, user)
	#print(user.readingGroup.posts)
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

def markPostRead(n, sock):
	#print("Mark these posts read: " + n)
	user = getUserBySocket(sock)
	post = user.readingGroup.posts[n - 1]
	post.groupId
	accessSQL("INSERT INTO postStatus(subject, userId, groupId) VALUES (\'" + str(post.subject)  + "\',\'" + user.username + "\'," + str(post.groupId) + " )")

def createNewPost(sock):
	user = getUserBySocket(sock)
	sock.send("Enter Post Subject: ")
	subject = sock.recv(BUFF)
	sock.send("Post: ")
	post = sock.recv(BUFF)
	now = datetime.datetime.now()
	date_time = now.strftime("%B %d %H:%M:%S")
	day = now.strftime("%A")
	weekday = day[:3].upper()
	
	subject = escapeQuotes(subject)
	post = escapeQuotes(post)
	
	newPost = Posts(subject, user.username, weekday, date_time, "EST 2016", post, user.readingGroup.groupID)

	accessSQL("INSERT INTO posts(subject, userId, weekDay, date_time, timeZone_year, post, groupId) VALUES (\'" + str(newPost.subject) + "\',\'" + str(newPost.username) + "\',\'" + str(newPost.weekDay) + "\',\'" + str(newPost.datetime) + "\',\'" + str(newPost.timezoneYear) + "\',\'" + str(newPost.post) + "\'," + str(newPost.groupId) + " )")
	sock.send("Posted")

def readPost(num, sock):
	user = getUserBySocket(sock)
	post = user.readingGroup.posts[num - 1]

	curGroupName = user.readingGroup.groupname
	curSubject = post.subject
	curAuthor = post.username
	curDate = post.weekDay + ", " + post.datetime + " " + post.timezoneYear

	output = ("Group: " + curGroupName) + "\n" + ("Subject: " + curSubject) + ("Author: " + curAuthor) + "\n" + ("Date: " + curDate) + "\n" + ( post.post)
	
	sock.send(output)


#set the cu


#USE THIS FOR EVERY USER STRING INPUT INTO DATABASE, ADD EXTRA ESCAPES IF YOU NEED
def escapeQuotes(string):
	newString = ""
	for s in string:
		if(s == "\'" or s == "\""):
			newString = newString + s + s
		else:
			newString = newString + s
	return newString

def set_mode(string):
	MODE = string
	

if __name__ == "__main__":
	server()
	sys.exit()
