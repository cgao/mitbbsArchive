# -*- coding: utf-8 -*-
from __future__ import print_function
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
import urllib2

import re
import sys

import copy
import pdb

from datetime import date, datetime, timedelta
import mysql.connector
from mysql.connector import errorcode
import argparse
import time

#server = 'com'
server = 'ca'

# remote connect
# used by setConfig
# set it to True when you connect to the database using a remote computer
# remoteconnect = False


class BoardPageParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if(len(attrs) == 2 and attrs[1] == ('class', 'a2')):
            #pdb.set_trace()
            if ('bbsdoc' in attrs[0][1] or '/mitbbs_bbsboa.php?' in attrs[0][1]):
                if('level=1' not in attrs[0][1]):  #avoid "回到上一级" infinite loop
                    self.URLs.append('http://www.mitbbs.'+server+attrs[0][1])
                    #print(attrs[0][1])
    def __init__(self):
        HTMLParser.__init__(self)
        self.URLs = []


# define user customized exception class
class MyException(Exception):
    def __init__(self, msg):
        self.msg = msg
    #def __str__(self):
    #    return repr(self.value)


class IPvalue():
    def __init__(self,bbsid, ip_st,ip_no,ipA, ipB,  dt, date, time, year, month, day, hour, minute, second):
        self.bbsid = bbsid
        self.ip_st = ip_st
        self.ip_no = ip_no
        self.ipA = ipA
        self.ipB = ipB
        self.datetime = dt
        self.date = date
        self.time = time
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

class IPs():
    def __init__(self,bbsid,ip_no, ip_st, ipA, ipB, dt):
        self.bbsid = bbsid
        self.ip_no = ip_no
        self.ip_st = ip_st
        self.ipA = ipA
        self.ipB = ipB
        self.datetime = dt


class pageParser(HTMLParser):
    def handle_data(self, data):
        data = data.decode(self.webpage_encoding).encode(self.system_encoding)
        if('发信人' in data):
            self.flag = True
        if(self.flag):
            self.content.append(data)
        if('来源:' in data):
            self.flag = False
    def __init__(self,webpage_encoding,system_encoding):
        HTMLParser.__init__(self)
        self.content = []
        self.webpage_encoding = webpage_encoding
        self.system_encoding = system_encoding
        self.flag = False

class Thread():
    def __init__(self, board, thread_id, url, bbsid, ip, nickname,title,time, content, dt):
        self.board = board
        self.thread_id = thread_id
        self.url = url
        self.bbsid = bbsid
        self.ip = ip
        self.nickname = nickname
        self.title = title
        self.time = time
        self.content = content
        self.dt = dt


class URLsParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        #print "Start tag:", tag
        #for attr in attrs:
            #print "     attr:", attr
            #print(type(attr))
        if(len(attrs) == 2 and attrs[1] == ('class', 'news1')):
            #print(attrs[0][1])
            #pdb.set_trace()
            self.URLs.append('http://www.mitbbs.'+server+attrs[0][1])
    def __init__(self):
        HTMLParser.__init__(self)
        self.URLs = []



# # test Parser
# class TestHTMLParser(HTMLParser):
#     def handle_starttag(self, tag, attrs):
#         print "Start tag:", tag
#         for attr in attrs:
#             print "     attr:", attr
#     def handle_endtag(self, tag):
#         print "End tag  :", tag
#     def handle_data(self, data):
#         print "Data     :", data
#     def handle_comment(self, data):
#         print "Comment  :", data
#     def handle_entityref(self, name):
#         c = unichr(name2codepoint[name])
#         print "Named ent:", c
#     def handle_charref(self, name):
#         if name.startswith('x'):
#             c = unichr(int(name[1:], 16))
#         else:
#             c = unichr(int(name))
#         print "Num ent  :", c
#     def handle_decl(self, data):
#         print "Decl     :", data



# add column datetime into board tables......
def addColDatetimetoBoard(board, cnx = False, config = False, quiet = False):
    status = True
    if not config:
        config = getConfig(quiet = quiet)
    flag = False
    if not cnx:
        cnx = mysql.connector.connect(**config)
        flag = True
    cursor = cnx.cursor()
    query = "ALTER TABLE " + board + " ADD datetime datetime"
    try:
        cursor.execute(query)
    except:
        status = False
    if flag:
        cnx.close()
    return status

    #datetimes = 



def addColDatetimetoAllBoard(config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    boards = getAllBoard(config = config, quiet = quiet)
    cnx = mysql.connector.connect(**config)
    for board in boards:
        if not quiet:
            print("Adding datetime to board: " + board)
        status = addColDatetimetoBoard(board, cnx = cnx, config = config, quiet = quiet)
        if not quiet:
            if status:
                print("Success: add datetime to " + board)
            else:
                print("Failure: add datetime to " + board)
    cnx.close()


# usage: convertColTimetoDatetime(startboard = 'Database')
# not working for 
#           Database
#           E-sports
#              
def convertColTimetoDatetime(startboard = False, config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    boards = getAllBoard(config = config, quiet = quiet)
    cnx = mysql.connector.connect(**config)
    if not startboard:
        startboard = boards[0]
    flag = False
    for board in boards:
        if board == startboard:
            flag = True
        if flag:
            cursor = cnx.cursor()
            if not quiet:
                print("Converting time to datetime for board: " + board + "...")
            update_stmt = ("UPDATE `" + board.lower() + "` SET datetime = STR_TO_DATE(SUBSTRING_INDEX(time, ',',1), '%a %b %d %T %Y')"
                            " WHERE datetime IS NULL and time like '%:%';")
            # time like '%:%' is needed for boards like Animals (where some threads has '宝禄' as time)
            #                                       and Apple (where some threads has '无将' as time)
            # but for database and e-sports, it't not working. Even if I add the backtick `board`, it's still not working..

            try:
                cursor.execute(update_stmt)
                if not quiet:
                    print("Success: ")
                cnx.commit()
                #pdb.set_trace()
            except:
                if not quiet:
                    print("Failure:")
                pdb.set_trace()
            cursor.close()
    cnx.close()

# merge all board tables into a table called threads

# usage: 
# status = mitbbs.mergaAllBoardTables(startboard = 'ac', endboard = 'zumba')
# for safety, better do it in bunkle
# status = mitbbs.mergaAllBoardTables(startboard = 'ac', endboard = 'hainan')
# status = mitbbs.mergaAllBoardTables(startboard = 'hainan', endboard = 'ohio')
# status = mitbbs.mergaAllBoardTables(startboard = 'ohio', endboard = 'tvgame')
# status = mitbbs.mergaAllBoardTables(startboard = 'tvgame', endboard = 'zumba')


# error
    # inserting bnu
    # succeed: bnu
    # inserting board
    # Table 'mitbbs.board' doesn't exist
    # inserting boston
    # succeed: boston
    # inserting database
    # Column count doesn't match value count at row 1
    # inserting e-sports
    # Column count doesn't match value count at row 1


def mergaAllBoardTables(startboard = False, endboard = False, config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    createBoard('threads',config = config, quiet = quiet)
    #pdb.set_trace()
    boards = getAllBoard(config = config, quiet = quiet)
    print("ok....... got all boards...")
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    startflag = False
    endflag = False
    startboard = startboard.lower()
    endboard = endboard.lower()
    for board in boards:
        board = board.lower()
        if board == startboard:
            startflag = True
        #pdb.set_trace()
        if startflag and not endflag:
            print("inserting " + board)
            #insert_stmt = ("INSERT IGNORE INTO `threads` SELECT * FROM `" + board + "` ON DUPLICATE KEY UPDATE")
            insert_stmt = ("INSERT INTO `threads` SELECT * FROM `" + board + "`")
            try:
                cursor.execute(insert_stmt)
                cnx.commit()
                print("succeed: " + board)
            except Exception, e:
                #pdb.set_trace()
                #cursor.close()
                #cnx.close()
                #return board
                print(e.msg)
        if board == endboard:
            endflag = True
    cursor.close()
    cnx.close()
    return True


# get the board thread_count from mitbbs::boardnames::thread_count
def boardThreadCount(board, cnx = False, quiet = False):
    flag = False
    if not cnx:
        config = getConfig(quiet = quiet)
        cnx = mysql.connector.connect(**config)
        flag = True  # indicator that we need to close the current cursor in the end of the program 
    cursor = cnx.cursor()
    select_stmt = ("SELECT thread_count FROM boardnames WHERE board = %(board)s")
    cursor.execute(select_stmt, { 'board': board })
    thread_count = cursor.fetchone()[0]
    cursor.close()
    if flag:
        cnx.close()
    return thread_count


# increase table::board::count by 1
def boardThreadCountIncre(board, cnx = False, quiet = False):
    flag = False
    if not cnx:
        config = getConfig(quiet = quiet)
        cnx = mysql.connector.connect(**config)
        flag = True
    cursor = cnx.cursor()
    thread_count = boardThreadCount(board, cnx = cnx, quiet = quiet)
    updateBoardThreadCount(board, thread_count+1, cnx = cnx, quiet = quiet)
    cursor.close()
    if flag:
        cnx.close()


# check how many rows in mitbbs::board, and write it into mitbbs::boardnames::thread_count
def checkBoardThreadCount(board, cnx = False, quiet = False):
    flag = False
    if not cnx:
        config = getConfig(quiet = quiet)
        cnx = mysql.connector.connect(**config)
        flag = True  # indicator that we need to close the current cursor in the end of the program 
    cursor = cnx.cursor()
    query ="SELECT COUNT(*) from `%s`" %board
    cursor.execute(query)             #execute query separately
    res=cursor.fetchone()
    total_rows=res[0]      #total rows
    # update thread_count
    updateBoardThreadCount(board, total_rows, cnx = cnx, quiet = quiet)
    cursor.close()
    if flag:
        cnx.close()    


def checkAllBoardThreadCount(config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    cnx = mysql.connector.connect(**config)
    boards = getAllBoard(config = config, quiet = quiet)
    for board in boards:
        checkBoardThreadCount(board, cnx = cnx, quiet = quiet)


def createBoard(board,config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    # for the table name, we should use lowercase in Mac OS
    # See http://dev.mysql.com/doc/refman/5.5/en/identifier-case-sensitivity.html
    TABLE = (
        "CREATE TABLE `" + board.lower() +"` ("
        "  `board` varchar(50) NOT NULL,"
        "  `thread_id` int(10) NOT NULL,"
        "  `url` varchar(70) NOT NULL,"
        "  `name` varchar(12),"
        "  `ip` varchar(7),"    
        "  `nickname` varchar(50),"
        "  `title` TEXT,"
        "  `time` varchar(50),"
        "  `content` TEXT,"        
        "  `datetime` datetime default null,"
        "  PRIMARY KEY (`board`, `thread_id`), "
        "  INDEX `" + board + "_index_1` (`thread_id`), "
        "  INDEX `board_index_1` (`board`), "
        "  INDEX `name_index_1` (`name`), "
        "  INDEX `ip_index_1` (`ip`), "
        "  CONSTRAINT `" + board + "_ibfk_1` FOREIGN KEY (`name`)"
        "     REFERENCES `id` (`name`) ON DELETE CASCADE"
        ") ENGINE=InnoDB")
    #cnx = mysql.connector.connect(**config)
    try:
        cnx = mysql.connector.connect(user = config['user'], password = config['password'], host = config['host'])
    except Exception, e:
        pass
        pdb.set_trace()
    #cursor = cnx.cursor()
    try:
        cnx.database = config['database']    
    except mysql.connector.Error as err:
        if not quiet:
            print('database not exist. Table' + board + ' creation failed. ')
        return False
    cursor = cnx.cursor() 
    try:
        if not quiet:
            print("Creating table {}: \n".format(board), end='')
        cursor.execute(TABLE)
        if not quiet:
            print('Table ' + board + ' created')
        return True
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            if not quiet:
                print('Table ' + board + ' already exists.')
            return True
        else:
            #pdb.set_trace()
            if not quiet:
                print(err.msg)
                print(err.errno)
                print('Table ' + board  + ' creation failed')
            #pdb.set_trace()
            return False
    else:
        if not quiet:
            print("OK")
        #pass
    cursor.close()
    cnx.close()    

  
# create table::boardnames 
def createBoardNames(config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    name = 'boardnames'
    TABLE = (
        "CREATE TABLE `" + name + "` ("
        "  `board` varchar(30) NOT NULL,"
        "  `zone_no` int(2) NOT NULL,"
        "  `boardurl` varchar(70) NOT NULL,"
        "  `thread_count` int(10) unsigned NOT NULL DEFAULT 0,"
        "  `thread_id_max` int(15) unsigned DEFAULT 0, "
        "  PRIMARY KEY (`board`)"
        ") ENGINE=InnoDB")
    #cnx = mysql.connector.connect(**config)
    cnx = mysql.connector.connect(user = config['user'], password = config['password'], host = config['host'])
    cursor = cnx.cursor()
    try:
        cnx.database = config['database']    
    except mysql.connector.Error as err:
        if not quiet:
            print('database not exist. Table' + name + ' creation failed. ')
        return False
    cursor = cnx.cursor()   
    try:
        if not quiet:
            print("Creating table {}: ".format(name), end='')
        cursor.execute(TABLE)
        if not quiet:
            print('Table' + name + ' created')
        return True
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            if not quiet:
                print("Table' + name + ' already exists.")
            return True
        else:
            if not quiet:
                print(err.msg)
                print("Table' + name + ' creation failed")
            return False
    else:
        if not quiet:
            print("OK")
    cursor.close()
    cnx.close()

   
def createDB(config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    #cnx = mysql.connector.connect(**config)
    cnx = mysql.connector.connect(user = config['user'], password = config['password'], host = config['host'])
    cursor = cnx.cursor()
    try:
        cnx.database = config['database']   
        if not quiet:
            print('database exist.')
        return True 
    except mysql.connector.Error as err:
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8mb4'".format(config['database']))
            if not quiet:
                print('database created.')
            return True
        except mysql.connector.Error as err:
            if not quiet:
                print("Failed creating database: {}".format(err))
            return False
    cursor.close()
    cnx.close()

def createID(config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    tablename = 'id'
    TABLE = (
        "CREATE TABLE `id` ("
        #"  `id_no` int(11) NOT NULL AUTO_INCREMENT,"
        "  `name` varchar(12) NOT NULL,"
        "  PRIMARY KEY (`name`)"
        ") ENGINE=InnoDB")
    #cnx = mysql.connector.connect(**config)
    cnx = mysql.connector.connect(user = config['user'], password = config['password'], host = config['host'])
    cursor = cnx.cursor()
    try:
        cnx.database = config['database']    
    except mysql.connector.Error as err:
        if not quiet:
            print('database not exist. Table id creation failed. ')
        return False
    cursor = cnx.cursor()   
    try:
        if not quiet:
            print("Creating table {}: ".format(tablename), end='')
        cursor.execute(TABLE)
        if not quiet:
            print('Table id created')
        return True
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            if not quiet:
                print("Table id already exists.")
            return True
        else:
            if not quiet:
                print(err.msg)
                print("Table id creation failed")
            return False
    else:
        if not quiet:
            print("OK")
        #pass
    cursor.close()
    cnx.close()


def createIP(config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    tablename = 'ip'
    TABLE = (
        "CREATE TABLE `ip` ("
        "  `name` varchar(12) NOT NULL,"
        "  `ip_no` int(7) NOT NULL,"
        "  `ip_st` varchar(7) NOT NULL,"
        "  `ipA` int(3) NOT NULL,"
        "  `ipB` int(3) NOT NULL,"    
        "  `datetime` datetime NOT NULL,"
        "  PRIMARY KEY (`name`,`ip_no`),"
        "  CONSTRAINT `ip_ibfk_1` FOREIGN KEY (`name`)"
        "     REFERENCES `id` (`name`) ON DELETE CASCADE"
        ") ENGINE=InnoDB")
    #cnx = mysql.connector.connect(**config)
    cnx = mysql.connector.connect(user = config['user'], password = config['password'], host = config['host'])
    cursor = cnx.cursor()
    try:
        cnx.database = config['database']    
    except mysql.connector.Error as err:
        if not quiet:
            print('database not exist. Table ip creation failed. ')
        return False
    cursor = cnx.cursor() 
    try:
        if not quiet:
            print("Creating table {}: \n".format(tablename), end='')
        cursor.execute(TABLE)
        return True
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            if not quiet:
                print("Table ip already exists.")
            return True
        else:
            if not quiet:
                print(err.msg)
                print("Table ip creation failed")
            pdb.set_trace()
            return False
    else:
        if not quiet:
            print("OK")
        #pass
    cursor.close()
    cnx.close()


def getAllBoard(config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    allboard = []
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()    
    cursor.execute("SELECT board FROM boardnames")
    results = cursor.fetchall()  # caution: the result is a list of tuples like (u'AC',)
    cursor.close()
    cnx.close()
    for result in results:
        board = str(result[0])
        allboard.append(board)
    return allboard

# usage: ids = getAllID()
# return: a list of all ids, from table::id
def getAllID(config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    allid = []
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()    
    if not quiet:
        print("fetchall ids. This may take a while...")
    cursor.execute("SELECT name FROM id")
    time.sleep(1) #I don't know why. But I need to stop here for a while to make fetchall() work...
    #pdb.set_trace()
    results = cursor.fetchall()  # caution: the result is a list of tuples like (u'AC',)
    #pdb.set_trace()
    if not quiet:
        print("fetching ends.")
    for result in results:
        bbsid = str(result[0])
        allid.append(bbsid)
        #print(bbsid)
    cursor.close()
    cnx.close()
    return allid


# usage: ips = getAllIP()
# return: a list of all rows in table::ip
def getAllIP(config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    allip = []
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()    
    # it will take forever to load at once. So I load the result by first  Byte
    for i in range(0,256):
        if not quiet:
            print("working on 1st byte = " + str(i))
        cursor.execute("SELECT * FROM ip WHERE ipA = %s", (i,))
        time.sleep(0.1)   # I need to sleep here.... Otherwise i = 24 will get stuck. I am now testing on a remote laptop
        results = cursor.fetchall()
        for result in results:
            ip = IPs(str(result[0]), result[1],str(result[2]),result[3],result[4],result[5])
            allip.append(ip)
    cursor.close()
    cnx.close()
    return allip



def getAllThread(board, config = False, quiet = False):
    system_encoding = sys.getfilesystemencoding()
    if not config:
        config = getConfig(quiet = quiet)
    allthread = []
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()    
    #pdb.set_trace()
    try:
        cursor.execute("SELECT * FROM " + board)
    except Exception, e:
        if not quiet:
            print("table " + board + "probably doesn't exist.")
        return False
        #pdb.set_trace()
    results = cursor.fetchall()
    for result in results:
        thread = Thread(str(result[0].encode(system_encoding)), result[1], str(result[2].encode(system_encoding)), 
                        str(result[3].encode(system_encoding)), str(result[4].encode(system_encoding)), str(result[5].encode(system_encoding)), 
                        str(result[6].encode(system_encoding)), str(result[7].encode(system_encoding)), str(result[8].encode(system_encoding)))
        allthread.append(thread)
    cursor.close()
    cnx.close()
    return allthread


def getBoardName(quiet = False):
    zones = ['http://www.mitbbs.'+server+'/bbsboa/0.html',
                'http://www.mitbbs.'+server+'/bbsboa/1.html',
                'http://www.mitbbs.'+server+'/bbsboa/2.html',
                'http://www.mitbbs.'+server+'/bbsboa/3.html',
                'http://www.mitbbs.'+server+'/bbsboa/4.html',
                'http://www.mitbbs.'+server+'/bbsboa/5.html',
                'http://www.mitbbs.'+server+'/bbsboa/6.html',
                'http://www.mitbbs.'+server+'/bbsboa/7.html',
                'http://www.mitbbs.'+server+'/bbsboa/8.html',
                'http://www.mitbbs.'+server+'/bbsboa/9.html',
                'http://www.mitbbs.'+server+'/bbsboa/10.html',
                #'http://www.mitbbs.'+server+'/bbsboa/11.html',  # club zone. avoid it for now
                'http://www.mitbbs.'+server+'/bbsboa/12.html'
                ]
    boardURLs = []
    boardNames = []
    for zone in zones:
        zoneURLs = getBoardNamefromZone(zone)
        boardURLs.append(zoneURLs)
    for zoneURLs in boardURLs:
        zoneNames = []
        for url in zoneURLs:
            name = re.findall('bbsdoc\\/(.*)\\.html', url)
            zoneNames.append(name)
        boardNames.append(zoneNames)
    return (boardNames, boardURLs)



def getBoardNameAssist(url, quiet = False):
    parser = BoardPageParser()
    req = urllib2.Request(url,headers={'User-Agent':'Mozilla/5.0'})  
    try:
        page = urllib2.urlopen(req).read()
    except urllib2.HTTPError, e:
        print(e.fp.read())
        #pdb.set_trace()
    parser.feed(page)
    return parser.URLs

# getBoardNameAssist(url) will return URLs like:
#   http://www.mitbbs.com/mitbbs_bbsboa.php?group=0&yank=0&group2=389
#   http://www.mitbbs.com/bbsdoc/BusinessNews.html
#   http://www.mitbbs.com/bbsdoc/ChinaNews.html
#
# The first is a folder. i need to parser it to get 2nd (or even 3rd) level board urls

def getBoardNamefromZone(zoneurl, quiet = False):
    #print(zoneurl)
    URLs = getBoardNameAssist(zoneurl, quiet = quiet)  # URLs 
    boardURLs = []
    for boardurl in URLs:
        if ('/mitbbs_bbsboa.php?' in boardurl):
            try:
                urls = getBoardNamefromZone(boardurl, quiet = quiet)
                boardURLs.extend(urls)
            except Exception, e:
                pass
                #pdb.set_trace()
        else:
            boardURLs.append(boardurl)
    return boardURLs


# I will change this part.
# better use HTMLParser
def getIP(bbsid, quiet = False):
    path = 'http://www.mitbbs.'+server+'/mobile/muserinfo.php?userid='+bbsid
    req = urllib2.Request(path,headers={'User-Agent':'Mozilla/5.0'})   
    page = urllib2.urlopen(req).read()
    webpage_encoding = re.search('charset=(.+?)\"',page,re.IGNORECASE).group(1)
    system_encoding = sys.getfilesystemencoding()
    #<div id="grxx_1">\r\n  <p>\xc9\xcf\xb4\xce\xd4\xda[Tue Mar 10 12:18:21 2015]\xb4\xd3[198.125]\xb5\xbd\xc3\xc0\xb9\xfa\xd5\xbe\xd2\xbb\xd3\xce<p>\r\n
    try:
        string=re.findall(re.escape("<div id=\"grxx_1\">\r\n  <p>")+"(.*?)"+re.escape("<p>\r\n"),page)[0]
    except:
        raise MyException("user doesn't exist ")
    result = re.findall(re.escape('[')+"(.*?)"+re.escape(']'),string)
    ip_st = result[1]
    try:
        ipA = int(re.findall("(.*)"+re.escape('.'),ip_st)[0])
        ipB = int(re.findall(re.escape('.')+"(.*)",ip_st)[0])
    except Exception, e:
        #pdb.set_trace()
        raise MyException("probably IPV6 encountered. I will set ip_st = '999.999' ipA = ipB = 999. ")
        ip_st = '999.999'
        ipA = 999
        ipB = 999
    ip_no = int(ipA*1e3+ipB)
    dt = result[0]
    dt = datetime.strptime(dt, '%a %b %d %H:%M:%S %Y')
    date = dt.date()
    time = dt.time()
    year = dt.date().year
    month = dt.date().month
    day = dt.date().day
    hour = dt.time().hour
    minute = dt.time().minute
    second = dt.time().second
    return IPvalue(bbsid, ip_st,ip_no,ipA, ipB, dt, date, time, year, month, day, hour, minute, second)


#
#       getMaxThreadIdDB(board, config = False, quiet = False)
#       getMaxThreadIdBoard(board, config = False, quiet = False)
#       updateBoard(board, config = False, quiet = False)  
# 



# change the size of table::board::board to len(board)
def modifyBoardColSize(config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    boards = getAllBoard(config = config, quiet = quiet)
    for board in boards:
        if not quiet:
            print("modifying board: " + board)
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()   
        try:
            cursor.execute("ALTER TABLE " + board.lower() + " MODIFY board VARCHAR(" + str(len(board)) + ")")
        except:
            #pdb.set_trace()
            if not quiet:
                print("table " + board + " doesn't exist.")
    return True


# allow these cols to be NULL
# because sometimes retrieveURL returns some NULL fields        
def modifyBoardColNull(config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    boards = getAllBoard(config = config, quiet = quiet)
    for board in boards:
        if not quiet:
            print("modifying board: " + board + "...")
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()   
        try:
            #cursor.execute("ALTER TABLE " + board.lower() + " MODIFY thread_id int(10)") primary key cannot be NULL?
            cursor.execute("ALTER TABLE `" + board.lower() + "` MODIFY name VARCHAR(30)")
            cursor.execute("ALTER TABLE `" + board.lower() + "` MODIFY ip VARCHAR(7)")
            cursor.execute("ALTER TABLE `" + board.lower() + "` MODIFY nickname VARCHAR(50)")
            cursor.execute("ALTER TABLE `" + board.lower() + "` MODIFY title TEXT")
            cursor.execute("ALTER TABLE `" + board.lower() + "` MODIFY time VARCHAR(50)")
            cursor.execute("ALTER TABLE `" + board.lower() + "` MODIFY content TEXT")
            print("succeed...")
        except Exception, e:
            pdb.set_trace()
            if not quiet:
                print("Some error happens. ")
    return True

def modifyNicknameColSize(config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    boards = getAllBoard(config = config, quiet = quiet)
    for board in boards:
        print("modifying board: " + board)
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()   
        try:
            cursor.execute("ALTER TABLE " + board.lower() + " MODIFY nickname VARCHAR(50)")
        except:
            #pdb.set_trace()
            if not quiet:
                print("table " + board + " doesn't exist.")
    return True    


# depreciated
def retrieveBoard(board, url = False, quiet = False):
    #board = board.upper()
    #pdb.set_trace()
    if not url:
        url =  'http://www.mitbbs.'+server+'/bbsdoc2/'+board+'_3.html'
    threads = []
    parserURL = URLsParser()
    req = urllib2.Request(url,headers={'User-Agent':'Mozilla/5.0'})      
    page = urllib2.urlopen(req).read()
    parserURL.feed(page)
    URLs = parserURL.URLs
    i = 0
    for urll in URLs:
        #print i
        #i += 1
        thread = retrieveURL(urll,board, quiet = quiet)
        if (thread.bbsid != ''):
            threads.append(thread) 
    return threads



# retrieve the content of a url
# return type(Thread)
def retrieveURL(url, board, quiet = False):
    try:
        thread_id = re.findall(board + re.escape('/') + '(.*)_3.html',url, re.IGNORECASE)[0]
        thread_id = int(thread_id)
        #print(thread_id)
    except:
        #pdb.set_trace()
        #if not quiet:
            #print("cannot find thread_id. Please check if the boardname cases matches the url.")
            #print("this is probably a sticky thread. Special treament...")
            #print(url)
        # get sticky thread thread_id
        try:
            thread_id = re.findall(board + re.escape('/') + '(.*)_3_1.html',url, re.IGNORECASE)[0]
            thread_id = int(thread_id)
            print("this is a sticky thread.") 
        except:
            #pdb.set_trace()
            if not quiet:
                print("Not valid url. Return false. ")
            pdb.set_trace()
            return False
            #pdb.set_trace()
        #return Thread(board, '', url, '', '', '', '', '', '', '')
        #pdb.set_trace()
    req = urllib2.Request(url,headers={'User-Agent':'Mozilla/5.0'})   
    page = urllib2.urlopen(req).read()
    webpage_encoding = re.search('charset=(.+?)\"',page,re.IGNORECASE).group(1)
    system_encoding = sys.getfilesystemencoding()
    parserPage = pageParser(webpage_encoding,system_encoding)
    try:
        parserPage.feed(page)  
    except Exception,e:
        #pdb.set_trace()
        #seems '\x8c\xc5' caused the problem
        # for now I will just skip this thread
        # pdb.set_trace()
        #print(e)
        #print("Some unusual encoding issue. for now I will just skip this thread")
        #print("Some unusual encoding issue. " + webpage_encoding + " is not working for decoding this page. I will use gbk to decode.")
        parserPage = pageParser('gbk',system_encoding)
        try:
            parserPage.feed(page)  
        except Exception,e:
            if not quiet:
                print("Some unusual encoding issue. I will log into into database with datetime 0000-00-00 00:00:00. ")
            #pdb.set_trace()
                #return Thread(board, thread_id, url, '', '', '', '', '', '', datetime(1, 1, 1, 00, 00, 00))
                #pdb.set_trace()
                return Thread(board, thread_id, url, '', '', '', '', '', '', None)
    oldcontent = copy.copy(parserPage.content) # make deep copy
    #发信人: palm (棕榈叶) (现实点，不要再做梦了), 信区: Berkeley
    try:
        bbsid = re.findall('发信人: (.*?)'+re.escape(' ('), parserPage.content[0])[0]
    except:
        if not quiet:
            print("cannot find bbsid. pdb starts. The thread is probably deleted, or doesn't exist.")
            print(url)
        #pdb.set_trace()
        return False
        #pdb.set_trace()
    try:
        ip = getIP(bbsid, quiet = quiet)
    except Exception, e:
        if not quiet:
            print(e.msg + "for " + bbsid)
        #pdb.set_trace()
        ip = ''
    try:
        nickname = re.findall( bbsid + re.escape(' (') + '(.*)' + re.escape('), 信区') ,parserPage.content[0])[0]
    except:
        if not quiet:    
            print("cannot find nickname. seems sb used tricky nickname. Try another way.")
        #pdb.set_trace()
        # sb has nickname like pc(>>>>mac). So I need to deal with it here
        # sb has more funky nickname like chunjuan(??). So I need to deal with it here
        count = 1
        try:
            while('), 信区' not in parserPage.content[count]):
                count += 1
        except:
            #pdb.set_trace()
            return False
        parserPage.content[0:count+1] = [''.join(oldcontent[0:count+1])]
        #print(parserPage.content[0])
        # need to replace "\n"
        #发信人: remoon (代表月亮消灭你), 信区: DVD
        parserPage.content[0]  = parserPage.content[0].replace("\r\n","")
        try:
            nickname = re.findall( bbsid + re.escape(' (') + '(.*)' + re.escape('), 信区') ,parserPage.content[0], re.IGNORECASE)[0]
            if not quiet:
                print(nickname)
        except:
            if not quiet:
                print("more tricky name... Need to take a look at it.")
            return Thread(board, thread_id, url, bbsid, ip, '', '', '', '', None)
            #pdb.set_trace()
    # join '标' and '题'
    # board, thread_id, url, bbsid, ip, nickname, title, time, content, dt

    parserPage.content[1:3] = [''.join(parserPage.content[1:3])]
    # for time:
    #   some are like:  发信站: BBS 未名空间站自动发信系统 (Tue Aug  7 21:42:46 2012)
    #   some are like:  发信站: BBS 未名空间站 (Mon Mar  2 00:37:28 2015, 美东)
    #   some are like:  发信站: BBS 未名空间站 (Wed Dec 2 13:23:37 2009, 北京)
    #   some are like:  发信站: The unknown SPACE (Thu Sep 14 16:14:08 2000), 站内信件
    try:
        time = re.findall('\n发信站: BBS 未名空间站 \\((.*)\\)', parserPage.content[2])[0]
    except:
        #pdb.set_trace()
        if not quiet:
            print("cannot find time. probably due to some tricky title. Try another way.")
        #print("probably due to some tricky title, 1 line becomes 2 lines.")
        count_start = 2
        try:
            while('发信站:' not in parserPage.content[count_start]):
                count_start += 1
            count_end = count_start
        except Exception, e:
            # happend on http://www.mitbbs.com/article/Military/37638901_3.html
            if not quiet:
                print("No idea. Give up... ")
            return Thread(board, thread_id, url, bbsid, ip, nickname , '', '', '', None)
        #print(count_end)
        try:
            while(')' not in parserPage.content[count_end]):
                count_end += 1
        except:
            # http://www.mitbbs.com/article/PDA/32260223_3.html
            if not quiet:
                print("really tricky page. I will pass. ")
            return Thread(board, thread_id, url, bbsid, ip, nickname, '', '', '', None)
        parserPage.content[count_start:count_end+1] = [''.join(parserPage.content[count_start:count_end+1])]
        parserPage.content[1:count_start] = [''.join(parserPage.content[1:count_start])]   
        try:
            time = re.findall('\\((.*)\\)', parserPage.content[2])[0]
        except:
            if not quiet:
                print("cannot find time. Pass...")
            return Thread(board, thread_id, url, bbsid, ip, nickname, '', '', '', None)
            #pdb.set_trace()
        #print(time)
    try:
        dt = datetime.strptime(time, '%a %b %d %H:%M:%S %Y')  # should work for 发信站: BBS 未名空间站自动发信系统 (Tue Aug  7 21:42:46 2012)
    except:
        try:
            string = re.findall('(.*)\\,',time)[0]
            dt = datetime.strptime(string, '%a %b %d %H:%M:%S %Y')  # should work for 发信站: BBS 未名空间站 (Mon Mar  2 00:37:28 2015, 美东)
        except:
            print("Strange datetime format. I will set datetime 0000-00-00 00:00:00. ")
            dt = None
            #pdb.set_trace()
    try: 
        title = re.findall('\n标 题: (.*)',parserPage.content[1])[0]
        if not quiet:
            print(board + " " + bbsid + "   " + time  + " : "+title)
    except:
        if not quiet:
            print("cannot find title. Pass...")
        return Thread(board, thread_id, url, bbsid, '', nickname, '', time, '', dt)
        #pdb.set_trace()        
    content = ''.join(parserPage.content[3:])
    return Thread(board, thread_id, url, bbsid, ip, nickname, title, time, content, dt)


# def runBoard(board, config = False, quiet = False):
#     if not config:
#         config = getConfig(quiet = quiet)
#     if createBoard(board,config = config, quiet = quiet):
#         writeBoard(board, config = config, quiet = quiet)
#     else:
#         if not quiet:
#             print("cannot get data from " + board)
#         #pdb.set_trace()`


# # run through all 4xx boards
# def runWholeMITBBS(config = False, quiet = False):
#     if not config:
#         config = getConfig(quiet = quiet)
#     # first: load boardurl from table:boardnames
#     boards = getAllBoard(config = config, quiet = quiet)
#     hot = getHotBoard(quiet = quiet)
#     for board in boards:
#         if not quiet:
#             print("running board: " + board)
#         runBoard(board, config, quiet = quiet)
#     return True

# # run through all 4xx boards, except for the hot boards defined in function:getHotBoard
# # this is useful for avoiding writting conflict when running 
# #       runall.py and runhot.py
# def runWholeMITBBSExcudeHot(config = False, quiet = False):
#     if not config:
#         config = getConfig(quiet = quiet)
#     # first: load boardurl from table:boardnames
#     boards = getAllBoard(config = config, quiet = quiet)
#     hot = getHotBoard(quiet = quiet)
#     #superhot = getSuperHotBoard(quiet = quiet)
#     for board in boards:
#         if not quiet:
#             print("running board: " + board)
#         if (board not in hot):
#             runBoard(board, config, quiet = quiet)
#         else:
#             if not quiet:
#                 print("this is a superhot or hot board. I am not going to run it..")
#             #pdb.set_trace()
#     return True



# update BoardThreadCount
def updateBoardThreadCount(board, thread_count, cnx = False, quiet = False):
    flag = False
    if not cnx:
        config = getConfig(quiet = quiet)
        cnx = mysql.connector.connect(**config)
        flag = True  # indicator that we need to close the current cursor in the end of the program 
    cursor = cnx.cursor()
    update_stmt = ("""UPDATE boardnames
                    SET thread_count = (%(thread_count)s)
                    WHERE board = (%(board)s)""")
    update_data = {
                    'board': board, 
                    'thread_count': thread_count,
                    }
    cursor.execute(update_stmt, update_data)
    cnx.commit()
    cursor.close()
    if flag:
        cnx.close()    


# update all ids' ip. 
#   ids from table::id
#   ip is fetched using getIP(bbsid) 
def updateIP(config = False, quiet = False, bbsid = None, all = True):
    if not config:
        config = getConfig(quiet = quiet)
    if bbsid and not all:
        #pdb.set_trace()
        try:
            ip = getIP(bbsid, quiet = quiet)
            if not quiet:
                print(bbsid + " " + ip.ip_st)
        except Exception, e:
            if not quiet:
                print(e.msg + ": " + bbsid)
        else:
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()   
            add_ip = ("INSERT INTO ip "
                          "(name, ip_no, ip_st, ipA, ipB, datetime) "
                          "VALUES (%(name)s, %(ip_no)s, %(ip_st)s, %(ipA)s, %(ipB)s, %(datetime)s) On DUPLICATE KEY UPDATE `datetime`=%(datetime)s")
            data_ip = {
              #'id_num': id_no,
              'name': bbsid,
              'ip_no': ip.ip_no,
              'ip_st': ip.ip_st,
              'ipA': ip.ipA,
              'ipB': ip.ipB,
              'datetime': ip.datetime,
              }
            try:
                cursor.execute(add_ip, data_ip)
            except mysql.connector.Error as err:
                #pdb.set_trace()
                if not quiet:
                    print(str(err.errno) + ": " + err.msg)
            cursor.close()
            cnx.close()
    else:
        #
        ids = getAllID(config = config, quiet = quiet)
        #pdb.set_trace()
        if bbsid:
            if bbsid in ids:
                index = ids.index(bbsid)
            else:
                index = 0
        else:
            index = 0           
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()    
        for bbsid in ids[index:]:
            try:
                ip = getIP(bbsid, quiet = quiet)
                if not quiet:
                    print(bbsid + " " + ip.ip_st)
            except Exception, e:
                #pdb.set_trace()
                if not quiet:
                    print(e.msg + ": " + bbsid)
                continue
            else:
                #print("Updating ip for " + bbsid)
                add_ip = ("INSERT INTO ip "
                              "(name, ip_no, ip_st, ipA, ipB, datetime) "
                              "VALUES (%(name)s, %(ip_no)s, %(ip_st)s, %(ipA)s, %(ipB)s, %(datetime)s) On DUPLICATE KEY UPDATE `datetime`=%(datetime)s")
                data_ip = {
                  #'id_num': id_no,
                  'name': bbsid,
                  'ip_no': ip.ip_no,
                  'ip_st': ip.ip_st,
                  'ipA': ip.ipA,
                  'ipB': ip.ipB,
                  'datetime': ip.datetime,
                  }
                try:
                    cursor.execute(add_ip, data_ip)
                except mysql.connector.Error as err:
                    #pdb.set_trace()
                    if not quiet:
                        print(str(err.errno) + ": " + err.msg)
                    #pdb.set_trace()
        cursor.close()
        cnx.close()
    return True


# Depreciated. Use writeURLtoThread()
# default (url = False) means only look for the most recent page (defined in retrieveBoard)
# return value: 
#  conditiono 1
#       True:  at least one inserted thread is new
#       False: all insersions failed, or are duplicate. otherwise if there are new threads coming in very fast, it will always return True
#  conditiono 2
#       True:  at least 6 inserted thread is new
#       False: at least 95 insersions failed, or are duplicate. otherwise if there are new threads coming in very fast, it will always return True
# this return value is useful for generalboard.py
#
# this will have problem... 
# use a flag to indicate:
#       flag = True: use condition 1
#       flag = False: use condition 2

def writeBoard(board, config = False, url = False, quiet = False, flag = False):
    status = False
    count = 0 # count of failure
    if not config:
        config = getConfig(quiet = quiet)
    if not url:
        url =  'http://www.mitbbs.'+server+'/bbsdoc2/'+board+'_3.html'
    threads = []
    parserURL = URLsParser()
    req = urllib2.Request(url,headers={'User-Agent':'Mozilla/5.0'})      
    page = urllib2.urlopen(req).read()
    parserURL.feed(page)
    URLs = parserURL.URLs
    #pdb.set_trace()
    if len(URLs) == 0:
        return False
    for urll in URLs:
        if (writeURLtoThreads(board, urll, config = config, quiet = quiet) == True):
            print("succeed. " + urll)
            status = True
        else:
            #print("failed. " + urll)
            count += 1
    if flag:  # condition 1
        return status
    else:
        if count >= 95:
            return False
        else:
            return True
    # result = retrieveBoard(board, url=url, quiet = quiet)
    # # connect to mysql
    # cnx = mysql.connector.connect(**config)
    # cursor = cnx.cursor()    
    # count = 0
    # for thread in result:
    #     count += 1
    #     # Insert id table
    #     if not quiet:
    #         print("Inserting id table: " + str(count))
    #     add_id = ("INSERT INTO id "
    #                    "(name) "
    #                    "VALUES (%s)")
    #     data_id = (thread.bbsid,)
    #     try:
    #         cursor.execute(add_id, data_id)
    #     except mysql.connector.Error as err:
    #         if not quiet:
    #             print(str(err.errno) + ": " + err.msg)
    #     #id_no = cursor.lastrowid
    #     # Insert ip table
    #     #pdb.set_trace()
    #     if not quiet:
    #         print("Inserting ip table: " + str(count))
    #     if (thread.ip != ''):
    #         # Here I used to use REPLACE instead of INSERT, because I want to update the login time
    #         # however, it will delete all entrys with the same 'name' although different 'ip_st'
    #         # the reason is, I suspect, that entry if A and entry B have same 'name' and different 'ip_st', 
    #         # their primary key is different, but they share the same 'name' foreign key index through 'name' in id' table 
    #         # So what I am going to do is to use "INSERT", and check if duplicate happens (errno = 1062), I will alter the datetime,
    #         # using On DUPLICATE
    #         # column of that entry
    #         add_ip = ("INSERT INTO ip "
    #                       "(name, ip_no, ip_st, ipA, ipB, datetime) "
    #                       "VALUES (%(name)s, %(ip_no)s, %(ip_st)s, %(ipA)s, %(ipB)s, %(datetime)s) On DUPLICATE KEY UPDATE `datetime`=%(datetime)s")
    #         data_ip = {
    #           #'id_num': id_no,
    #           'name': thread.bbsid,
    #           'ip_no': thread.ip.ip_no,
    #           'ip_st': thread.ip.ip_st,
    #           'ipA': thread.ip.ipA,
    #           'ipB': thread.ip.ipB,
    #           'datetime': thread.ip.datetime,
    #         }
    #         try:
    #             cursor.execute(add_ip, data_ip)
    #         except mysql.connector.Error as err:
    #             if not quiet:
    #                 print(str(err.errno) + ": " + err.msg)
    #             #pdb.set_trace()
    #     # Insert thread table 
    #     if not quiet:
    #         print("Inserting thread table: " + str(count))
    #     add_thread = ("INSERT INTO threads "
    #                   "(board, thread_id, url, name, ip, nickname, title, time, content, datetime) "
    #                   "VALUES (%(board)s, %(thread_id)s, %(url)s, %(name)s, %(ip)s, %(nickname)s, %(title)s, %(time)s, %(content)s, %(datetime)s)")
    #     if(thread.ip != ''):
    #         ip_st = thread.ip.ip_st
    #     else:
    #         ip_st = ''
    #     data_thread = {
    #       #'id_num': id_no,
    #       'board': thread.board,
    #       'thread_id': thread.thread_id,
    #       'url': thread.url,
    #       'name': thread.bbsid,
    #       'ip': ip_st,
    #       'nickname': thread.nickname,
    #       'title': thread.title,
    #       'time': thread.time,
    #       'content': thread.content,
    #       'datetime': thread.dt,
    #     }
    #     try:
    #         cursor.execute(add_thread, data_thread)
    #         boardThreadCountIncre(board, cnx = cnx, quiet = quiet) # add mitbbs::boardnames::thread_count by 1 where mitbbs::boardnames::board = board
    #     except mysql.connector.Error as err:
    #         if not quiet:
    #             print(str(err.errno) + ": " + err.msg)
    #         if err.errno == 1062:  # Duplicaye entry error 
    #             status = False
    #         #pdb.set_trace()
    # # Make sure data is committed to the database
    # cnx.commit()
    # cursor.close()
    # cnx.close()
    # if not quiet:
    #     print(board + " loading finished")
    # return status
    # #pdb.set_trace()



# write the board names into table::boardnames 
def writeBoardNames(config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    [boardNames, boardURLs] = getBoardName()    
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()    
    for i in range(0,12):
        names = boardNames[i]
        urls = boardURLs[i]
        if (i == 11):
            i = 12
        # Insert table::boardnames
        if not quiet:
            print("Inserting boardnames table for zone " + str(i))
        for name, url in zip(names, urls):
            #pdb.set_trace()  
            if not quiet:
                print(name)    
            name = name[0]
            add_boardnames = ("INSERT INTO boardnames "
                          "(board, zone_no, boardurl) "
                          "VALUES (%(board)s, %(zone_no)s, %(boardurl)s)")
            data_boardnames = {
              #'id_num': id_no,
              'board': name,
              'zone_no': i,
              'boardurl': url,
            }
            try:
                cursor.execute(add_boardnames, data_boardnames)
            except mysql.connector.Error as err:
                if not quiet:
                    print(err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()


# check (board, thread_id) exist in the threads
def threadExist(board, thread_id, config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()   
    select_stmt = ("SELECT url FROM threads WHERE board = %(board)s AND thread_id = %(thread_id)s") 
    cursor.execute(select_stmt, { 'board': board, 'thread_id':thread_id})
    if cursor.fetchone() is None:   # not in database
        cursor.close()
        cnx.close()
        return False
    else:                           # already in database
        cursor.close()
        cnx.close()
        return True
    

# read and return the thread_id_max(int) from table::boardnames::'board'
# if it is none, return 0 and set boardnames::thread_id_max = 0
def getThreadIdMax(board, config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor() 
    query_stmt = ("SELECT thread_id_max FROM boardnames WHERE board = %(board)s")
    cursor.execute(query_stmt, { 'board': board })
    # check if return value is duple
    thread_id_max = cursor.fetchone()
    cursor.close()
    cnx.close()
    if thread_id_max is None:
        setThreadIdMax(board,0,config = config, quiet = quiet)
        return 0
    else:
        return thread_id_max[0]
    
# set boardnames::'board'::thread_id_max = thread_id
def setThreadIdMax(board, thread_id, config = False, quiet = False):
    if not config:
        config = getConfig(quiet = quiet)
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor() 
    update_stmt = ("""UPDATE boardnames
                    SET thread_id_max = (%(thread_id)s)
                    WHERE board = (%(board)s)""")
    update_data = {
                    'board': board, 
                    'thread_id': thread_id,
                    }
    #pdb.set_trace()
    cursor.execute(update_stmt, update_data)
    cnx.commit()
    cursor.close()
    cnx.close()
    #return max(thread_ids)

# get the current board webpage's maximum thread_id

def getBoardThreadIdMax(board):
    boardurl =  'http://www.mitbbs.'+server+'/bbsdoc2/'+board+'_3.html'
    threads = []
    parserURL = URLsParser()
    req = urllib2.Request(boardurl,headers={'User-Agent':'Mozilla/5.0'})      
    page = urllib2.urlopen(req).read()
    parserURL.feed(page)
    URLs = parserURL.URLs
    thread_id_max = 0
    for url in URLs:
        try:
            thread_id = re.findall(board + re.escape('/') + '(.*)_3.html',url, re.IGNORECASE)[0]
            thread_id = int(thread_id)
            #print(thread_id)
        except:
            try:
                thread_id = re.findall(board + re.escape('/') + '(.*)_3_1.html',url, re.IGNORECASE)[0]
                thread_id = int(thread_id)
                #print("this is a sticky thread.") 
            except:
                #if not quiet:
                    #print("Not valid url. Return false. ")
                thread_id = 0
        if thread_id > thread_id_max:
            thread_id_max = thread_id
    return thread_id_max

# write the content of a thread into threads table
def writeURLtoThreads(board, url, config = False, quiet = False):
    thread = retrieveURL(url, board, quiet = quiet)
    if thread == False:
        if not quiet:
            print("URL " + url + " is invalid. Skip write to the database.")
            return False
    else:
        if not config:
            config = getConfig(quiet = quiet)
        if threadExist(board, thread.thread_id, config = config, quiet = quiet):
            #pdb.set_trace()
            if not quiet:
                print("Thread already exist in the database. Skip insert again.")
            return False
        else:
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()
            add_id = ("INSERT INTO id "
                           "(name) "
                           "VALUES (%s)")
            data_id = (thread.bbsid,)
            try:
                cursor.execute(add_id, data_id)
            except mysql.connector.Error as err:
                if not quiet:
                    print(str(err.errno) + ": " + err.msg)
            #id_no = cursor.lastrowid
            # Insert ip table
            #pdb.set_trace()
            if (thread.ip != ''):
                # Here I used to use REPLACE instead of INSERT, because I want to update the login time
                # however, it will delete all entrys with the same 'name' although different 'ip_st'
                # the reason is, I suspect, that entry if A and entry B have same 'name' and different 'ip_st', 
                # their primary key is different, but they share the same 'name' foreign key index through 'name' in id' table 
                # So what I am going to do is to use "INSERT", and check if duplicate happens (errno = 1062), I will alter the datetime,
                # using On DUPLICATE
                # column of that entry
                add_ip = ("INSERT INTO ip "
                              "(name, ip_no, ip_st, ipA, ipB, datetime) "
                              "VALUES (%(name)s, %(ip_no)s, %(ip_st)s, %(ipA)s, %(ipB)s, %(datetime)s) On DUPLICATE KEY UPDATE `datetime`=%(datetime)s")
                data_ip = {
                  #'id_num': id_no,
                  'name': thread.bbsid,
                  'ip_no': thread.ip.ip_no,
                  'ip_st': thread.ip.ip_st,
                  'ipA': thread.ip.ipA,
                  'ipB': thread.ip.ipB,
                  'datetime': thread.ip.datetime,
                }
                try:
                    cursor.execute(add_ip, data_ip)
                except mysql.connector.Error as err:
                    if not quiet:
                        print(str(err.errno) + ": " + err.msg)
                    #pdb.set_trace()
            # Insert thread table 
            add_thread = ("INSERT INTO threads "
                          "(board, thread_id, url, name, ip, nickname, title, time, content, datetime) "
                          "VALUES (%(board)s, %(thread_id)s, %(url)s, %(name)s, %(ip)s, %(nickname)s, %(title)s, %(time)s, %(content)s, %(datetime)s)")
            if(thread.ip != ''):
                ip_st = thread.ip.ip_st
            else:
                ip_st = ''
            data_thread = {
              #'id_num': id_no,
              'board': thread.board,
              'thread_id': thread.thread_id,
              'url': thread.url,
              'name': thread.bbsid,
              'ip': ip_st,
              'nickname': thread.nickname,
              'title': thread.title,
              'time': thread.time,
              'content': thread.content,
              'datetime': thread.dt,
            }
            try:
                cursor.execute(add_thread, data_thread)
                boardThreadCountIncre(board, cnx = cnx, quiet = quiet) # add mitbbs::boardnames::thread_count by 1 where mitbbs::boardnames::board = board
                thread_id_max = getThreadIdMax(board, config = config, quiet = quiet)
                if thread_id_max < thread.thread_id:
                    setThreadIdMax(board, thread.thread_id, config = config, quiet = quiet)
            #except mysql.connector.Error as err:
            except Exception, err:
                #pdb.set_trace()
                #if not quiet:
                if err.errno != 1062:
                    print(url + " " + str(err.errno) + ": " + err.msg)
                if err.errno == 1118:
                    data_thread.content  = "Content too long. Check the url. "
                    try: 
                        cursor.execute(add_thread, data_thread)
                        boardThreadCountIncre(board, cnx = cnx, quiet = quiet) # add mitbbs::boardnames::thread_count by 1 where mitbbs::boardnames::board = board
                        thread_id_max = getThreadIdMax(board, config = config, quiet = quiet)
                        if thread_id_max < thread.thread_id:
                            setThreadIdMax(board, thread.thread_id, config = config, quiet = quiet)
                        cnx.commit()
                        cursor.close()
                        cnx.close()
                        return True
                    except Exception, err:
                        print(url + " " + str(err.errno) + ": " + err.msg)
                        cnx.commit()
                        cursor.close()
                        cnx.close()
                        return False
                #if err.errno == 1062:  # Duplicaye entry error 
                else:
                    cnx.commit()
                    cursor.close()
                    cnx.close()
                    return False
                #pdb.set_trace()
            # Make sure data is committed to the database
            cnx.commit()
            cursor.close()
            cnx.close()
            #pdb.set_trace()
            return True


# check if boardnames::board::thread_id_max < thread_id_max_onboard = getBoardThreadIdMax(board)
# if True:
#   for thread_id in range(thread_id_max+ 1, thread_id_max_onboard + 1):
#       if not threadExist(board, thread_id):
#           url = 'http://www.mitbbs.com/article/'board'/'thread_id'_3.html :
#           writeURLtoThreads(board, url, config = False, quiet = False)
#   setThreadIdMax(board, thread_id_max_onboard, config = False, quiet = False)     
def writeNewThreads(board, config = False, quiet = False):
    if not config:
        confit = getConfig(quiet = quiet)
    thread_id_max = getThreadIdMax(board, config = config, quiet = quiet)
    thread_id_max_onboard = getBoardThreadIdMax(board)
    print("maximum thread_id in database: " + str(thread_id_max))
    print("maximum thread_id on webpage : " + str(thread_id_max_onboard))
    if thread_id_max < thread_id_max_onboard:
        #thread_max = thread_id_max
        for thread_id in range(thread_id_max+ 1, thread_id_max_onboard + 1):
            if not threadExist(board, thread_id, config = config, quiet = quiet):
                url = 'http://www.mitbbs.com/article/'+ board +'/' + str(thread_id) +'_3.html'
                #pdb.set_trace()
                if writeURLtoThreads(board, url, config = config, quiet = quiet):
                    #if not quiet:
                    print(board + " thread " + str(thread_id) + " added to threads table. Goal: " + str(thread_id_max_onboard))
                    #thread_max = thread_id
        #setThreadIdMax(board, thread_max, config = config, quiet = quiet)
        # not necessary. the thread_id_max is already updated when calling writeURLtoThreads()

##### configuration ######

def getHotBoard(quiet = False):
    hot = [ 'Military',  'Joke', 'Money', 'FleaMarket',  'PDA',  'Automobile', 'ebiz',   'Dreamer',  'PennySaver',   'JobHunting',
            'Stock', 'Travel', 'TVChinese', 'THU', 'USTC', 'PKU', 
            'EB2EB3', 'LeisureTime', 'Parenting', 'Living', 'Immigration', 'Faculty', 'Biology', 'Sex',
            'Boston', 'SanFrancisco', 'Tennessee', 'NewYork', 'LosAngeles', 'Seattle', 'Texas', 'Chicago', 'Carolinas', 'NewJersey',
            'WashingtonDC', 'WmGame'
          ]
    return hot


def getConfig(quiet = False, remoteconnection = False):
    if not remoteconnection:
        config = { 
        'user': 'username', 
        'password': 'password', 
        'host': 'localhost', 
        'database': 'mitbbs', 
        'raise_on_warnings': True,
        } 
    else:
        config = { 
        'user': 'username', 
        'password': 'password', 
        'host': '18.189.69.47', 
        'database': 'mitbbs', 
        'raise_on_warnings': True,
        } 
    return config


def setServer():
    return server


if __name__ == '__main__':
    #parser = argparse.ArgumentParser(description="mitbbs")
    #parser.add_argument('-b', '--board', help="mitbbs board name", required=True)
    #args = parser.parse_args()
    #board = args.board
    
    config = getConfig()

    config['database'] = 'mitbbs_crash'
    board = 'History'
    getAllThread(board,config = config)

    #modifyBoardColSize(config)
    #createDB(config)
    #createID(config)
    #createIP(config)
    #createBoardNames(config)


    # run this once a few months. The boardnames shouldn't change frequently
    #writeBoardNames(config)
    

    #hot = ['Military',  'Joke', 'Money', 'FleaMarket',  'PDA',  'Automobile', 'ebiz',   'Dreamer',  'PennySaver',   'WmGame']
    #boards1 = [   'OverseasNews',   'BusinessNews', 'ChinaNews',    'ChinaNews2',   'Detective',
    #                'Donation',     'GreatPit',     'Headline',      'History',     'Military']

    #for board in hot:
    #    runBoard(board,config)
    
    #runWholeMITBBS(config)   
    #runBoard('Announcement', config)


##############################################################################
## to be done
##############################################################################





# 8. All (most) boards miss the first 100 threads. I need to add them back...
# python initialRetrieve -b board -p 0 -e 1
# http://www.mitbbs.com/bbsdoc1/"board"_1_3.html


# 9. add function to save image to local file, and use mysql's blob to reference to the image file



# 10. 文摘区 & 保留区


# 11. allow NULL for board::name, ip, nickname, title, time, content, datetime
#    this will save the threads which were not correctly parsered.



# 12
# deal with content too long error.
# 1406: Data too long for column 'content' at row 1
# http://www.mitbbs.com/article/NorthEast/31191298_3.html

# 13
# most threads on vote board are invalid(unicode problem). I need to fix it..
# for now, I will skip the threads in updateall


##############################################################################
## done 
##############################################################################

# 1. Database and E-Sports not working...
# mysql syntax problem
# I need a mapping function to 
#               map("Database") = "database0" 
#               map("E-Sports") = "esports"
#
# solution:
#  change   add_thread = ("INSERT INTO " + board.lower() + " "
#  into     add_thread = ("INSERT INTO `" + board.lower() + "` "
# It seems when: 
#       a. board contains signs like "-"
#       b. board has some mysql keyword like "database"
# you need to add "`" to avoid the confusion


# 2. write updateIP
# fetch data from table::id. And update their ips
#
# done: updateIP.py


# 3. fix the "unusual encoding issue" issue
#
# done.
# when it happens, change the decoding from "gb2312" to "gbk"
# It seems another solution is to ignore during decode? content.decode('GB2312','ignore')? How to apply?

# 4. add number of threads into table::boardnames


# 5. add a datetime col for each board tables, which will be useful for query
# methods:
#       stringToDatetime(time): not necessary. I can use datetime.strptime(b, '%a %b %d %H:%M:%S %Y')
#       addColDatetimetoBoard
#       addDatetime(board)

# in the end, I need to modify createBoardDB and writeBoard


# 6. merge all boards into threads. use mergaAllBoardTables()


# 7. change the update board method.
# The thread_id will be always even number.
# For example, if the current latest thread's thread_id is 298501, then the next new thread's thread_id will be 298503,...
# So for each board, I will check the maximum thread_id in the table, thread_id_max1.
# Then I will retrieve the urls in http://www.mitbbs.com/bbsdoc2/"board"_3.html to find the url with maximum thread_id, thread_id_max2.
# I will retrieveURL for http://www.mitbbs.com/article/"board"/(thread_id_max1 + 2 : 2 : thread_id_max2)_3.html
#
# methods:
#       getMaxThreadIdDB(board, config = False, quiet = False)
#       getMaxThreadIdBoard(board, config = False, quiet = False)
#       updateBoard(board, config = False, quiet = False)   

# Caution:  the odd thread_id is only true for recent thread_id. You will find the old thread_id can be even number. So this should be run
#           only after I finish runallboard.py, o.w. I will miss the even thread_ids...


