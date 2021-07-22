#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
import pprint
import copy
import random

class Block_Controller(object):

    # init parameter
    board_backboard = 0
    board_data_width = 0
    board_data_height = 0
    ShapeNone_index = 0
    CurrentShape_class = 0
    NextShape_class = 0

    isLevel1Mode = True

    # GetNextMove is main function.
    # input
    #    nextMove : nextMove structure which is empty.
    #    GameStatus : block/field/judge/debug information. 
    #                 in detail see the internal GameStatus data.
    # output
    #    nextMove : nextMove structure which includes next shape position and the other.
    def GetNextMove(self, nextMove, GameStatus):

        t1 = datetime.now()

        # print GameStatus
        print("========= called GetNextMove ==========================>")
        # pprint.pprint(GameStatus, width = 61, compact = True)

        ## check game mode (Level 1 or else)
        blockIndex = GameStatus["judge_info"]["block_index"]
        currentShapeIndex = GameStatus["block_info"]["currentShape"]["index"]  
        if self.isLevel1Mode == True:
            if currentShapeIndex % 7 == blockIndex % 7:
                print("==== LEVEL 1 mode! =====")
                #nextMove["strategy"]["direction"] = 0
                #nextMove["strategy"]["x"] = 0
                #nextMove["strategy"]["y_operation"] = 1
                #nextMove["strategy"]["y_moveblocknum"] = 1
                nextDir, nextX = self.calcLevel1Move(blockIndex)
                nextMove["strategy"]["direction"] = nextDir
                nextMove["strategy"]["x"] = nextX
                nextMove["strategy"]["y_operation"] = 1
                nextMove["strategy"]["y_moveblocknum"] = 1
                return nextMove
            else :
                self.isLevel1Mode = False


        print("shape_info_stat ==",GameStatus["debug_info"]["shape_info_stat"])

        # get data from GameStatus
        # current shape info
        # kaiten kanou kaisu 
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        self.CurrentShape_class = GameStatus["block_info"]["currentShape"]["class"]
        # next shape info
        NextShapeDirectionRange = GameStatus["block_info"]["nextShape"]["direction_range"]
        self.NextShape_class = GameStatus["block_info"]["nextShape"]["class"]
        # current board info
        self.board_backboard = GameStatus["field_info"]["backboard"]
        # default board definition
        self.board_data_width = GameStatus["field_info"]["width"]
        self.board_data_height = GameStatus["field_info"]["height"]
        self.ShapeNone_index = GameStatus["debug_info"]["shape_info"]["shapeNone"]["index"]

        # search best nextMove -->
        strategy = None
        # check last nextBoard
        lastNextBoard = None
        LatestEvalValue = -100000
        # search with current block Shape
        for direction0 in CurrentShapeDirectionRange:
            # search with x range
            x0Min, x0Max = self.getSearchXRange(self.CurrentShape_class, direction0)
            for x0 in range(x0Min, x0Max):
                # get board data, as if dropdown block
                board = self.getBoard(self.board_backboard, self.CurrentShape_class, direction0, x0)
                EvalValue0 =self.calcEvaluationValue(board)


                # search with next block Shape
                for direction1 in NextShapeDirectionRange:
                    # search with x range
                    x1Min, x1Max = self.getSearchXRange(self.NextShape_class, direction1)
                    for x1 in range(x1Min, x1Max):
                        # get next board data, as if dropdown block
                        nextBoard = self.getBoard(board, self.NextShape_class,direction1, x1)
                        # evaluate board
                        EvalValue1 = self.calcEvaluationValue(nextBoard)



                # evaluate board
                # EvalValue = self.calcEvaluationValueSample(board)
                # EvalValue = self.calcEvaluationValue(board)
                # update best move
                        if EvalValue0 + EvalValue1 > LatestEvalValue:
                            strategy = (direction0, x0, 1, 1)
                            LatestEvalValue = EvalValue0 + EvalValue1
                            #lastNextBoard = nextBoard

                ###test
                ###for direction1 in NextShapeDirectionRange:
                ###  x1Min, x1Max = self.getSearchXRange(self.NextShape_class, direction1)
                ###  for x1 in range(x1Min, x1Max):
                ###        board2 = self.getBoard(board, self.NextShape_class, direction1, x1)
                ###        EvalValue = self.calcEvaluationValueSample(board2)
                ###        if EvalValue > LatestEvalValue:
                ###            strategy = (direction0, x0, 1, 1)
                ###            LatestEvalValue = EvalValue
        # search best nextMove <--
        # check last nextBoard
        # print("------last nextBoard----")
        # print(lastNextBoard)

        print("===", datetime.now() - t1)
        nextMove["strategy"]["direction"] = strategy[0]
        nextMove["strategy"]["x"] = strategy[1]
        nextMove["strategy"]["y_operation"] = strategy[2]
        nextMove["strategy"]["y_moveblocknum"] = strategy[3]
        print(nextMove)
        print("## tsume code ##")
        return nextMove

    def calcLevel1Move(self, blockIndex):
        level1MoveList = [
                [1,2,0,5,0,4,0,3,0,5,0,4,0,4,0,4,0,5,0,4,# 10tern
                    0,5,0,4,0,4,0,5,0,4,0,4,0,5,0,4,0,5,0,4,#20tern
                    0,4,0,5,0,4,0,3,0,5,0,4],#26tern
                [0,0,0,0,2,9,1,1,2,9,0,0,2,9,2,5,2,3,2,5,
                    2,3,2,5,2,9,2,5,2,3,2,5,2,9,2,5,2,3,2,5,
                    2,9,2,5,2,3,1,1,2,9,2,5],
                [0,3,0,3,1,1,0,1,2,0,0,3,0,7,2,6,0,7,2,6,
                    0,1,2,0,0,7,2,6,0,1,2,0,0,7,2,6,0,1,2,0,
                    0,7,2,6,1,1,0,1,2,0,0,1],
                [3,7,0,6,3,7,0,6,3,7,0,6,3,1,0,0,3,1,0,0,
                    3,7,0,6,3,1,0,0,3,7,0,6,3,1,0,0,3,7,0,6,
                    3,1,0,0,3,7,0,6,3,7,2,5],
                [0,1,0,1,0,1,0,2,0,2,0,1,0,8,0,8,0,8,0,8,
                    0,2,0,2,0,8,0,8,0,2,0,2,0,8,0,8,0,2,0,2,
                    0,8,0,8,0,1,0,2,0,4,0,4],
                [1,8,1,8,1,8,1,8,1,8,1,8,1,2,1,2,1,2,1,2,
                    1,8,1,8,1,2,1,2,1,8,1,8,1,2,1,2,1,8,1,8,
                    1,2,1,2,1,8,1,8,1,8,1,8],
                [1,6,0,7,1,6,0,7,1,6,0,7,1,0,0,1,1,0,0,1,
                    1,6,0,7,1,0,0,1,1,6,0,7,1,0,0,1,1,6,0,7,
                    1,0,0,1,1,6,0,7,1,6,1,6]
                ]
        blockTern = int((blockIndex-1) / 7)
        blockShapeIndex = blockIndex % 7 - 1
        if blockShapeIndex < 0:
            blockShapeIndex = 6
        nextBlockDir = level1MoveList[blockShapeIndex][blockTern*2]
        nextBlockX = level1MoveList[blockShapeIndex][blockTern*2+1]
        return nextBlockDir, nextBlockX

    
    def getSearchXRange(self, Shape_class, direction):
        #
        # get x range from shape direction.
        #
        minX, maxX, _, _ = Shape_class.getBoundingOffsets(direction) # get shape x offsets[minX,maxX] as relative value.
        xMin = -1 * minX
        xMax = self.board_data_width - maxX
        return xMin, xMax

    def getShapeCoordArray(self, Shape_class, direction, x, y):
        #
        # get coordinate array by given shape.
        #
        coordArray = Shape_class.getCoords(direction, x, y) # get array from shape direction, x, y.
        return coordArray

    def getBoard(self, board_backboard, Shape_class, direction, x):
        #
        # get new board.
        #
        # copy backboard data to make new board.
        # if not, original backboard data will be updated later.
        board = copy.deepcopy(board_backboard)
        _board = self.dropDown(board, Shape_class, direction, x)
        return _board

    def dropDown(self, board, Shape_class, direction, x):
        #
        # internal function of getBoard.
        # -- drop down the shape on the board.
        #
        dy = self.board_data_height - 1
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        # update dy
        for _x, _y in coordArray:
            _yy = 0
            while _yy + _y < self.board_data_height and (_yy + _y < 0 or board[(_y + _yy) * self.board_data_width + _x] == self.ShapeNone_index):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        _board = self.dropDownWithDy(board, Shape_class, direction, x, dy)
        return _board

    def dropDownWithDy(self, board, Shape_class, direction, x, dy):
        #
        # internal function of dropDown.
        #
        _board = board
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        for _x, _y in coordArray:
            _board[(_y + dy) * self.board_data_width + _x] = Shape_class.shape
        return _board


    def calcEvaluationValue(self, board):
        #
        # sample function of evaluate board.
        #
        width = self.board_data_width
        height = self.board_data_height

        # evaluation paramters
        ## lines to be removed
        fullLines = 0
        ## number of holes or blocks in the line.
        nHoles, nIsolatedBlocks = 0, 0
        ## absolute differencial value of MaxY
        absDy = 0
        ## how blocks are accumlated
        BlockMaxY = [0] * width
        holeCandidates = [0] * width
        holeConfirm = [0] * width

        ### check board
        # each y line
        for y in range(height - 1, 0, -1):
            hasHole = False
            hasBlock = False
            # each x line
            for x in range(width):
                ## check if hole or block..
                if board[y * self.board_data_width + x] == self.ShapeNone_index:
                    # hole
                    hasHole = True
                    holeCandidates[x] += 1  # just candidates in each column..
                else:
                    # block
                    hasBlock = True
                    BlockMaxY[x] = height - y                # update blockMaxY
                    if holeCandidates[x] > 0:
                        holeConfirm[x] += holeCandidates[x]  # update number of holes in target column..
                        holeCandidates[x] = 0                # reset
                    if holeConfirm[x] > 0:
                        nIsolatedBlocks += 1                 # update number of isolated blocks

            if hasBlock == True and hasHole == False:
                # filled with block
                fullLines += 1
            elif hasBlock == True and hasHole == True:
                # do nothing
                pass
            elif hasBlock == False:
                # no block line (and ofcourse no hole)
                pass

        # nHoles
        for x in holeConfirm:
            nHoles += abs(x)

        ### absolute differencial value of MaxY
        BlockMaxDy = []
        for i in range(len(BlockMaxY) - 1):
            val = BlockMaxY[i] - BlockMaxY[i+1]
            BlockMaxDy += [val]
        for x in BlockMaxDy:
            absDy += abs(x)

        #### maxDy
        #maxDy = max(BlockMaxY) - min(BlockMaxY)
        #### maxHeight
        #maxHeight = max(BlockMaxY) - fullLines

        ## statistical data
        #### stdY
        #if len(BlockMaxY) <= 0:
        #    stdY = 0
        #else:
        #    stdY = math.sqrt(sum([y ** 2 for y in BlockMaxY]) / len(BlockMaxY) - (sum(BlockMaxY) / len(BlockMaxY)) ** 2)
        #### stdDY
        #if len(BlockMaxDy) <= 0:
        #    stdDY = 0
        #else:
        #    stdDY = math.sqrt(sum([y ** 2 for y in BlockMaxDy]) / len(BlockMaxDy) - (sum(BlockMaxDy) / len(BlockMaxDy)) ** 2)

        # calc Evaluation Value
        score = 0
        if fullLines >= 4:
            score = score + fullLines * 13.0    # try to delete 4 lines
        elif fullLines == 1:
            score = score - fullLines * 5.0     # try not to delete 1 line
        elif fullLines == 3:
            score = score + fullLines * 5.0     #try to delete 3 lines
        else :
            score = score + fullLines * 1.0     # try to delete 2  lines
        score = score - nHoles * 10.0               # try not to make hole
        score = score - nIsolatedBlocks * 1.0      # try not to make isolated block
        score = score - absDy * 1.0                # try to put block smoothly
        #score = score - maxDy * 0.3                # maxDy
        #score = score - maxHeight * 5              # maxHeight
        #score = score - stdY * 1.0                 # statistical data
        #score = score - stdDY * 0.01               # statistical data

        # print(score, fullLines, nHoles, nIsolatedBlocks, maxHeight, stdY, stdDY, absDy, BlockMaxY)
        return score


BLOCK_CONTROLLER = Block_Controller()

