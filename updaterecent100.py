import mitbbs
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="mitbbs")
    parser.add_argument('-r', '--remoteconnection', help="remote connection. y or n")
    parser.add_argument('-q', '--quiet', help="quiet. y or n")
    args = parser.parse_args()
    if not args.quiet:
        quiet = True
    elif args.quiet == 'y':
        quiet = True
    elif args.quiet == 'n':
        quiet = False
    else:
        print("-q must be either y or n...")
        sys.exit()

    if not args.remoteconnection:
        remoteconnection = False
    elif args.remoteconnection == 'y':
        remoteconnection = True 
    elif args.remoteconnection == 'n':
        remoteconnection = False
    else:
        print("-r must be either y or n...")
        sys.exit()
        
    config = mitbbs.getConfig(remoteconnection = remoteconnection, quiet = quiet)

    boards = mitbbs.getAllBoard(config = config, quiet = quiet)
    for board in boards:
        print("********** working on board " + board + " **********")
        mitbbs.writeBoard(board, config = config, url = False, quiet = quiet)