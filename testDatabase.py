import sqlite3

def accessSQL(statement):
	connCursor.execute(statement)
	dbreturned = connCursor.fetchall()
	conn.commit()
	return dbreturned

conn = sqlite3.connect('./database/InterestDB.db')
conn.row_factory = sqlite3.Row
connCursor = conn.cursor()

query = "SELECT * FROM postStatus WHERE postStatus.userId == \'Chuntak\' and postStatus.groupId == %d" (1)
accessSQL(query)
print(list)

