# dumn it
# I need to move the data in mitbbs_crash into mitbbs
# I am going to:
#   1. get all the tables's name: tables
#   2. for table in tables && table not in {id, ip, boardnames}:
#           if table not in mitbbs:
#               create mitbbs::table     
#               for row in table:
#                   write row into mitbbs::table if row is not in mitbbs::table;  boardThreadCountIncre(table)
#   3. for row in id:
#           if row not in mitbbs.id:
#               write row into mitbbs.id          
#   4. for row in ip:            
#           if row not in mitbbs.ip:
#               write row into mitbbs.ip

import mitbbs

import mysql
import pdb

configOld = { 
    'user': 'username', 
    'password': 'password', 
    'host': 'localhost',    
    'database': 'mitbbs_crash', 
    'raise_on_warnings': True,
    } 

configNew = { 
    'user': 'username', 
    'password': 'password', 
    'host': 'localhost', 
    'database': 'mitbbs', 
    'raise_on_warnings': True,
    } 


def moveBoard(board):
    dbOld = 'mitbbs_crash'
    dbNew = 'mitbbs'
    threadOld = mitbbs.getAllThread(board, config = configOld)
    #pdb.set_trace()
    if threadOld == False:
        return False   # table not exist
    if checkTableExists(board) == 1:   # board table not exist for mitbbs database
        # need to create a table
        mitbbs.createBoard(board,config = configNew)
    cnx = mysql.connector.connect(**configNew)
    cursor = cnx.cursor()   
    for thread in threadOld:
 # Insert thread table 
        print("Inserting thread table: " + thread.board + "  "+ thread.title)
        add_thread = ("INSERT INTO `" + board.lower() + "` "
                      "(board, thread_id, url, name, ip, nickname, title, time, content) "
                      "VALUES (%(board)s, %(thread_id)s, %(url)s, %(name)s, %(ip)s, %(nickname)s, %(title)s, %(time)s, %(content)s)")
        data_thread = {
          #'id_num': id_no,
          'board': thread.board,
          'thread_id': thread.thread_id,
          'url': thread.url,
          'name': thread.bbsid,
          'ip': thread.ip,
          'nickname': thread.nickname,
          'title': thread.title,
          'time': thread.time,
          'content': thread.content,
        }
        try:
            cursor.execute(add_thread, data_thread)
            mitbbs.boardThreadCountIncre(board, cnx = cnx) # add mitbbs::boardnames::thread_count by 1 where mitbbs::boardnames::board = board
        except mysql.connector.Error as err:
            print(str(err.errno) + ": " + err.msg)
            #pdb.set_trace()
    cnx.commit()
    cursor.close()
    cnx.close()





def moveID():
    dbOld = 'mitbbs_crash'
    dbNew = 'mitbbs'
    idOld = mitbbs.getAllID(config = configOld)
    cnx = mysql.connector.connect(**configNew)
    cursor = cnx.cursor()   
    count = 0
    for bbsid in idOld:
        count += 1
        if (count%100 == 0):
            print(str(count) + ": inserting id table: " + bbsid)
        add_id = ("INSERT INTO id "
                       "(name) "
                       "VALUES (%s)")
        data_id = (bbsid,)
        try:
            cursor.execute(add_id, data_id)
        except mysql.connector.Error as err:
            pass
            #print(str(err.errno) + ": " + err.msg)
        #id_no = cursor.lastrowid
        # Insert ip table
        #pdb.set_trace()
    cnx.commit()
    cursor.close()
    cnx.close()

def moveIP():
    dbOld = 'mitbbs_crash'
    dbNew = 'mitbbs'
    ipOld = mitbbs.getAllIP(config = configOld)
    cnx = mysql.connector.connect(**configNew)
    cursor = cnx.cursor()   
    count = 0
    for ip in ipOld:
        count += 1
        if (count%100 == 0):
            print(str(count) + ": inserting ip table: " + ip.bbsid)
        add_ip = ("INSERT INTO ip "
                      "(name, ip_no, ip_st, ipA, ipB, datetime) "
                      "VALUES (%(name)s, %(ip_no)s, %(ip_st)s, %(ipA)s, %(ipB)s, %(datetime)s) On DUPLICATE KEY UPDATE `datetime`=%(datetime)s")
        data_ip = {
          #'id_num': id_no,
          'name': ip.bbsid,
          'ip_no': ip.ip_no,
          'ip_st': ip.ip_st,
          'ipA': ip.ipA,
          'ipB': ip.ipB,
          'datetime': ip.datetime,
        }
        try:
            cursor.execute(add_ip, data_ip)
        except mysql.connector.Error as err:
            print(str(err.errno) + ": " + err.msg)
            pdb.set_trace()
    cnx.commit()
    cursor.close()
    cnx.close()


# this is not a good function
# because mitbbs and mitbbs_crash could have same table name, 
# when cursor.fetchone()[0] = 2, it means board is in both database
# when cursor.fetchone()[0] = 1, it means board is only in mitbbs_crash
def checkTableExists(tablename, config = False):
    if not config:
        config = mitbbs.getConfig()
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()   
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(tablename.replace('\'', '\'\'')))
    return cursor.fetchone()[0]

if __name__ == '__main__':
    #moveID()
    #moveIP()
    #moveBoard('Ohio')
    boards = mitbbs.getAllBoard()
    flag = False
    for board in boards:
        print(board)
        if (board == 'Olympics'):
            flag = True
        if (flag):
            moveBoard(board)
