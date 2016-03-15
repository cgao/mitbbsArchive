
import mitbbs
import urllib2
import argparse
import pdb
import sys
import time

    # generally, a board has < 500,000 threads. For example fleamarket has 426460 as of 3/13/15
    # http://www.mitbbs.ca/bbsdoc1/FleaMarket_number_3.html will list the threads between number -  number+99. Here number! << thread_no
    # When number > max# of threads, it will show the latest page with sticky threads
    # So my scheme is to sent i in large range, and for each increament, I will check if duplicate error happens, the process will stop

server = mitbbs.setServer()

# By default I will only retrieve up to 100,000 threads for a board. I will let runall.py to do the rest, which should be a better solution
# This initialization method is not elegant... 
def retrieveBoardFromBeginning(board, startpage = 0, endpage = 2000, config = False, quiet = False):
    pagecount = startpage 
    urls = []
    #if startpage == 0:
    #    url0 = 'http://www.mitbbs.'+server+'/bbsdoc1/'+ board + '_1_3.html'
    #    urls.append(url0)
    #pdb.set_trace()
    for i in range(startpage,endpage):
        url = 'http://www.mitbbs.'+server+'/bbsdoc1/'+ board + '_' + str(i)+'00_3.html'
        urls.append(url)
    for url in urls:
        success = True
        repeatcurloop = True 
        while repeatcurloop:
            print('****************************************************************')
            print("Current page: " + str(pagecount*100))
            print(url)
            #req = urllib2.Request(url,headers={'User-Agent':'Mozilla/5.0'})   
            #page = urllib2.urlopen(req).read()
            #pdb.set_trace()
            try:
                success = mitbbs.writeBoard(board, config = config, url = url, quiet = quiet) 
                if success == False:
                    print("repeating pages. Stop Here for board " + board + "......")
                else:   
                    pagecount += 1
            except Exception, e:
                print("Error for page: " + str(pagecount*100))
                #pdb.set_trace()
                time.sleep(10)
            else:
                #pagecount += 1
                repeatcurloop = False
        if not success:
            break
    #return success



# usage: python initialRetrieve.py -b USTC -r False -p 1  (on local machine)
# usage: python initialRetrieve.py -c k -r True -p 1  (on remote machine)
#        python initialRetrieve.py -b Automobile -p 1000 -e 2000  (initialize automobile from page 1000 to page 2000 (thread 100,000 to 200,000))
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="mitbbs")
    parser.add_argument('-b', '--board', help="mitbbs board whose name = board will be run")
    parser.add_argument('-p', '--startpage', help="start page", type=int)
    parser.add_argument('-e', '--endpage', help="end page", type=int)
    parser.add_argument('-c', '--character', help="mitbbs boards whose names begin with character will be run")
    parser.add_argument('-r', '--remoteconnection', help="remote connection. y or n")
    args = parser.parse_args()

    #pdb.set_trace()
    if not args.startpage:
        startpage = 0
    else:
        startpage = args.startpage
    if not args.endpage:
        endpage = 2000
    else:
        endpage = args.endpage    
    if not args.board and not args.character:
        print("You must specify one and only one: -b  or -c. ")
        sys.exit()
    if args.board and args.character:
        #print("You must specify one and only one: -b  or -c. ")
        #sys.exit()
        print("******* will check boards whose name begins with " + args.character + " and after board " + args.board + " *******")
    if not args.remoteconnection:
        remoteconnection = False
    elif args.remoteconnection == 'n':
        remoteconnection = False
    elif args.remoteconnection == 'y':
        remoteconnection = True
    else:
        print('remoteconnection must be either y or n.')
        sys.exit()
    config = mitbbs.getConfig(remoteconnection = remoteconnection, quiet = True)
    print(config)
    if args.board and not args.character:
        retrieveBoardFromBeginning(args.board, startpage = startpage, endpage = endpage, config = config, quiet = True)
        sys.exit()
    if args.character:
        boards = mitbbs.getAllBoard(config = config, quiet = True)
        for board in boards[boards.index(args.board) if args.board in boards else 0:]:
            #print("........." + board + ".............")
            if board[0].lower() == args.character.lower():
                #pdb.set_trace()
                print("........." + board + ".............")
                retrieveBoardFromBeginning(board, startpage = startpage, endpage = endpage, config = config, quiet = True)
        sys.exit()

