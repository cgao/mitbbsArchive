import mitbbs
import argparse
import pdb
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="mitbbs")
    parser.add_argument('-q', '--quiet', help="quiet. y or n")
    parser.add_argument('-u', '--bbsid', help="bbsid")
    parser.add_argument('-a', '--all', help="all users. y or n")
    parser.add_argument('-r', '--remoteconnection', help="remote connection. y or n")
    args = parser.parse_args()

    #pdb.set_trace()
    
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
        
    config = mitbbs.getConfig(remoteconnection = remoteconnection, quiet = True)

    if not args.bbsid:
        bbsid = None
    else:
        bbsid = args.bbsid
 

    if not args.all:
        all = True
    elif args.all == 'y':
        all = True
    elif args.all == 'n':
        all = False
    else:
        print("-a must be either y or n...")
        sys.exit()


    #pdb.set_trace()

    mitbbs.updateIP(config = config, quiet = quiet, bbsid = bbsid, all = all)

      
