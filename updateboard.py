import mitbbs
import argparse
import sys
# usage:
#   python updateboard.py -b History               ;; will update History
#   python updateboard.py -c h                      ;; will update all boards with leading name 'h/H'
#   python updateboard.py -c h -b History          ;; will update from History to all boards with leading name 'h/H' that are after History


if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser(description="mitbbs")
    parser.add_argument('-b', '--board', help="mitbbs board whose name = board will be run")
    parser.add_argument('-c', '--character', help="mitbbs boards whose names begin with character will be run")
    parser.add_argument('-r', '--remoteconnection', help="remote connection. y or n")
    args = parser.parse_args()
    board = args.board
    
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
        mitbbs.writeNewThreads(board, config = config, quiet = True)
        sys.exit()
    if args.character:
        boards = mitbbs.getAllBoard(config = config, quiet = True)
        for board in boards[boards.index(args.board) if args.board in boards else 0:]:
            #print("........." + board + ".............")
            if board[0].lower() == args.character.lower():
                #pdb.set_trace()
                print("........." + board + ".............")
                mitbbs.writeNewThreads(board, config = config, quiet = True)
        sys.exit()


    