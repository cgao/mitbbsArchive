# exclude 'vote'

import mitbbs
import argparse
import sys

if __name__ == '__main__':
    #config = mitbbs.getConfig()
    #quiet = False
    #boards = mitbbs.getAllBoard(config = config, quiet = quiet)
    #for board in boards:
    #    print(board)
    #    mitbbs.writeNewThreads(board, quiet = True)


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
    #print(config)
    if not args.board and not args.character:
        boards = mitbbs.getAllBoard(config = config, quiet = True)
        for board in boards[boards.index(args.board) if args.board in boards else 0:]:
            if board != 'vote':
                print("........." + board + ".............")
                mitbbs.writeNewThreads(board, quiet = True, config = config)
        sys.exit()
    if args.board and not args.character:
        if board != 'vote':
            print("........." + board + ".............")
            mitbbs.writeNewThreads(board, quiet = True, config = config)
        sys.exit()
    if args.character:
        boards = mitbbs.getAllBoard(config = config, quiet = True)
        for board in boards[boards.index(args.board) if args.board in boards else 0:]:
            #print("........." + board + ".............")
            if board[0].lower() == args.character.lower():
                #pdb.set_trace()
                if board != 'vote':
                    print("........." + board + ".............")
                    mitbbs.writeNewThreads(board, quiet = True, config = config)
        sys.exit()