import mitbbs

if __name__ == '__main__':
    # parse arguments
    #parser = argparse.ArgumentParser(description="mitbbs")
    #parser.add_argument('-b', '--board', help="mitbbs board name", required=True)
    #args = parser.parse_args()
    #board = args.board
    config = mitbbs.getConfig()

    mitbbs.createDB(config = config)
    mitbbs.createID(config = config)
    mitbbs.createIP(config = config)
    mitbbs.createBoardNames(config = config)
    # run this once a few months. The boardnames shouldn't change frequently
    mitbbs.writeBoardNames(config = config)
    