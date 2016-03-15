import mitbbs

if __name__ == '__main__':
    # parse arguments
    #parser = argparse.ArgumentParser(description="mitbbs")
    #parser.add_argument('-b', '--board', help="mitbbs board name", required=True)
    #args = parser.parse_args()
    #board = args.board
    
    #config = mitbbs.getConfig()

    hot = mitbbs.getHotBoard()
    for board in hot:
        print(board)
    
    for board in hot:
        mitbbs.writeNewThreads(board, quiet = True)
    