import mitbbs


if __name__ == '__main__':

    #config = mitbbs.getConfig()

    #mitbbs.runWholeMITBBSExcudeHot()   
    boards = mitbbs.getAllBoard(config = config, quiet = quiet)
    hot = mitbbs.getHotBoard(quiet = quiet)
    for board in boards and board not in hot:
        print(board)
        mitbbs.writeNewThreads(board, quiet = True)