#!/usr/bin/env python
#coding:utf-8

from BaseAI import BaseAI
from utils import *
from random import randint
import time

#infinity = 1.0e400

class PlayerAI(BaseAI):
    def __init__(self):
        self.grid = None
        self.move = -1
        self.eval = 0
        self.isPlayer = True
        self.displayer = None

    def smoothness(self, grid):  # concept from https://github.com/ov3y/2048-AI/blob/master/js/grid.js smooth function
        smoothness = 0
        for x in range(4):
            for y in range(4):
                if not grid.canInsert((x, y)):
                    currCellValue = log2(grid.map[x][y])
                    for direction in range(2):
                        processed = 0
                        targetCellValue = infinity
                        if direction == 0 and not grid.crossBound((x + 1, y)) and grid.map[x + 1][y] > 0:
                            targetCellValue = log2(grid.map[x + 1][y])
                            processed = 1
                        if direction == 1 and not grid.crossBound((x, y + 1)) and grid.map[x][y + 1] > 0:
                            targetCellValue = log2(grid.map[x][y + 1])
                            processed = 1
                        if processed != 0:
                            smoothness -= abs(currCellValue - targetCellValue) #abs(currCellValue - targetCellValue)
        return smoothness

    def monotonicity(self, grid):  # concept from https://github.com/ov3y/2048-AI/blob/master/js/grid.js monotonicity2 function
        totals = [0, 0, 0, 0]
        # up and down direction
        for x in range(4):
            current = 0
            next = current + 1
            while (next < 4):
                while next < 4 and not grid.canInsert((x, next)):
                    next += 1
                if (next >= 4):
                    next -= 1
                currentValue = 0
                if not grid.canInsert((x, current)):
                    currentValue = log2(grid.map[x][current])
                nextValue = 0
                if not grid.canInsert((x, next)):
                    nextValue = log2(grid.map[x][next])
                if (currentValue > nextValue):
                    totals[0] += nextValue - currentValue
                elif (nextValue > currentValue):
                    totals[1] += currentValue - nextValue
                current = next
                next += 1
        # right and left direction
        for y in range(4):
            current = 0
            next = current + 1
            while (next < 4):
                while next < 4 and not grid.canInsert((next, y)):
                    next += 1
                if (next >= 4):
                    next -= 1
                currentValue = 0
                if not grid.canInsert((current, y)):
                    currentValue = log2(grid.map[current][y])
                nextValue = 0
                if not grid.canInsert((next, y)):
                    nextValue = log2(grid.map[next][y])
                if (currentValue > nextValue):
                    totals[2] += nextValue - currentValue
                elif (nextValue > currentValue):
                    totals[3] += currentValue - nextValue
                current = next
                next += 1

        return max(totals[0], totals[1]) + max(totals[2], totals[3])

    def monotonicity2(self, grid):
        monotonicity = 0
        totals = [0, 0, 0, 0]
        for x in xrange(grid.size):
            current = 0
            next = current + 1
            while next < 4:
                while next < 4 and grid.getCellValue((x, next)) == 0:
                    next += 1
                if next >= 4:
                    next -= 1
                currentvalue = grid.getCellValue((x, current))
                if currentvalue != 0:
                    currentvalue = math.log(currentvalue) / math.log(2)
                nextvalue = grid.getCellValue((x, next))
                if nextvalue != 0:
                    nextvalue = math.log(nextvalue) / math.log(2)
                if currentvalue > nextvalue:
                    totals[0] += (nextvalue - currentvalue)
                elif currentvalue < currentvalue:
                    totals[1] += (current - nextvalue)
                current = next
                next += 1
        for y in xrange(grid.size):
            current = 0
            next = current + 1
            while next < 4:
                while next < 4 and grid.getCellValue((next, y)) == 0:
                    next += 1
                if next >= 4:
                    next -= 1
                currentvalue = grid.getCellValue((current, y))
                if currentvalue != 0:
                    currentvalue = int(math.log(currentvalue) / math.log(2))
                nextvalue = grid.getCellValue((x, next))
                if nextvalue != 0:
                    nextvalue = int(math.log(nextvalue) / math.log(2))
                if currentvalue > nextvalue:
                    totals[2] += nextvalue - currentvalue
                elif currentvalue < currentvalue:
                    totals[3] += current - nextvalue
                current = next
                next += 1
        monotonicity = max(totals[0], totals[1]) + max(totals[2], totals[3])
        return monotonicity

    def getMaxTileLocation(self, grid):
        maxTileLocation = []
        maxTile = 0
        for x in xrange(grid.size):
            for y in xrange(grid.size):
                if grid.map[x][y] > maxTile:
                    maxTile = grid.map[x][y]
                    maxTileLocation.append((x, y))

        return maxTileLocation

    def getRankedValueLocationDir(self, grid):
        dir = {}
        maxTile = 0
        for x in xrange(grid.size):
            for y in xrange(grid.size):
                if not grid.canInsert((x,y)):
                    dir[grid.map[x][y]] = (x,y)
        return dir

    def isBigTileInCorner(self, grid):
        currLocaList = self.getMaxTileLocation(grid)
        inCorner = 0
        for currLoca in currLocaList:
            if currLoca == (grid.size - 1, grid.size - 1) or currLoca == (0, 0) or currLoca == (
                    0, grid.size - 1) or currLoca == (grid.size - 1, 0):
                inCorner = 1
        if inCorner == 1:
            return True
        else:
            return False

    def willMoveLetBiggestTileOffCorner(self, move, grid):  # assume the biggest tile is in one of the corners
        gridCopy = grid.clone()
        preLoc = self.getMaxTileLocation(grid)
        gridCopy.move(move)
        currLoc = self.getMaxTileLocation(gridCopy)
        if self.isBigTileInCorner(gridCopy) or preLoc != currLoc:
            return False
        else:
            return True

    def getAverageScorePerGrid(self,grid):
        total = 0
        occuCellNum = 0
        for x in xrange(grid.size):
            for y in xrange(grid.size):
                if not grid.canInsert((x,y)):
                    total += grid.map[x][y]
                    occuCellNum += 1
        if occuCellNum ==0:
            return 0
        else:
            return float(total)/occuCellNum

    def getAverageScorePerGrid_tail(self,grid):
        numberIncluded = 12
        rankDir = self.getRankedValueLocationDir(grid)
        total = 0
        occuCellNum = 0
        i=0
        for key in sorted(rankDir):
            i += 1
            if i <= numberIncluded:
                if key != 0:
                    total += key
                    occuCellNum += 1
        if occuCellNum == 0:
            return 0
        else:
            return float(total)/occuCellNum

    def biggerTilesOnBoarderPreference(self,grid):
        numberIncluded = 4
        rankDir = self.getRankedValueLocationDir(grid)
        total = 0
        i=0
        for key in reversed(sorted(rankDir)):
            i += 1
            if i <= numberIncluded:
                if key != 0:
                    if rankDir[key][0] == 0 or rankDir[key][0] == grid.size -1 or rankDir[key][1] == 0 or rankDir[key][1] == grid.size -1:
                        total += key
        return float(total)

    def island(self, grid):
        return random.randrange(0, 1)

    def eval_fn1(self, grid):
        """
		最大的不能离开角落
		不一定大的先合并
		如果走一步能合并不只一对这样比较好
		不用留尽量多的空格
		"""
        emptyCellLength = len(grid.getAvailableCells())
        if emptyCellLength == 0:
            emptyCellLength = 1
        biggestTileInCornerPenalty = -100000000000  # NEGATIVE
        smoothWeight = 6.0
        mono2Weight = 17.0 #15.0
        emptyWeight = 2.0#1
        maxWeight = 1.0#2.0
        averWeight = 2
        boarderWeight = 0.5

        self.eval = self.smoothness(grid) * smoothWeight \
                    + self.monotonicity2(grid) * mono2Weight \
                    + grid.getMaxTile() * maxWeight \
                    + emptyCellLength * emptyWeight+1 \
                    + self.getAverageScorePerGrid_tail(grid) * averWeight \
                    + (1-self.isBigTileInCorner(grid)) * biggestTileInCornerPenalty \
                    + self.biggerTilesOnBoarderPreference(grid) * boarderWeight
        #+ (1 - self.isBigTileInCorner(grid)) * biggestTileInCornerPenalty \
        #
        return self.eval

    def alphabeta_search(self, grid, d, cutoff_test=False):
        """
		Search game to determine best action; use alpha-beta pruning.
		This version cuts off search and uses an evaluation function.
		"""
        #player maximize the possible score from eval_function
        def max_value(currGrid, alpha, beta,
                      depth):  # CURRDRIP is the grid waiting for player to move, wanting the max score
            bestScore = alpha
            if depth > d or not currGrid.canMove():
                self.eval_fn1(currGrid)
                return self.eval
            for move in currGrid.getAvailableMoves():  # move is a integer: vecIndex = [UP, DOWN, LEFT, RIGHT] = range(4)
                succGrid = currGrid.clone()
                succGrid.move(move)  # succGrid is the grids that have been moved in different conditions
                v = min_value(succGrid, bestScore, beta,
                              depth + 1)  # we want to choose the max value condition to actually move
                if v >= bestScore:
                    bestScore = v
                    self.bestMove = move
                if bestScore > beta:
                    return beta

        def min_value(currGrid, alpha, beta, depth):  # special min_value function compare to classic minmax algo.
            """
			We select the "best" add tile place based on eval function for current grid after adding tile.
			We do not deepen the depth for computer, only for next round of move
			"""
            if depth > d or not currGrid.canMove():
                self.eval_fn1(currGrid)
                return self.eval

            candiInserts = []
            for possibleValue in [2, 4]:
                tmp = {}
                for place in currGrid.getAvailableCells():  # [(x,y),()...]
                    succGrid = currGrid.clone()
                    succGrid.insertTile(place, int(possibleValue))
                    value = self.smoothness(succGrid) + self.monotonicity(succGrid)
                    tmp[value] = succGrid
                maxKey = max(k for k, v in tmp.iteritems())
                candiInserts.append(tmp[maxKey])

            bestScore = beta  # beta
            for twoCandi in candiInserts:
                candiToContinue = twoCandi.clone()
                value = max_value(candiToContinue, alpha, bestScore, depth)
                if value < bestScore:
                    bestScore = value
                if bestScore < alpha:
                    return alpha

        # Body of alphabeta_search starts here:
        # The default test cuts off at depth d or at a terminal state
        self.bestMove = -1
        currGrid = grid.clone()
        depth = 0
        max_value(currGrid, -infinity, infinity, depth + 1)

        return self.bestMove


    def search(self, grid, depth, alpha, beta, positions, isPlayer =True, errorLog=False):
        self.grid = grid
        args = [grid, depth, alpha, beta, positions, isPlayer,'False']
        if errorLog:
            print "!!!!!!!!!!!!!!!!!!!start of new search: ",depth, alpha, beta, isPlayer, positions
        # the maxing player
        bestMove = -1

        if isPlayer:
            bestScore = alpha
            if errorLog:
                print "valid moves: ", grid.getAvailableMoves()
            for move in grid.getAvailableMoves():
                #if self.isBigTileInCorner(grid) and self.willMoveLetBiggestTileOffCorner(move, grid) and len(grid.getAvailableMoves()) > 1:
                    #continue
                newGrid = grid.clone()
                if 1:
                    newGrid.move(move)
                    positions += 1
                    if depth == 0:
                        if errorLog:
                            print 'place2'
                            print "a-b: ", alpha,beta
                        result = {'move': move, 'score': self.eval_fn1(newGrid), 'positions': positions}
                        if errorLog:
                            print "~~~~~~result from 1"
                            print result
                    else:
                        result = self.search(newGrid, depth-1, bestScore, beta, positions, False)
                        if errorLog:
                            print "===================", 'new search para: ',newGrid, depth-1, bestScore,beta,positions, 'false'
                            print "~~~~~~~result from 2"
                            print result
                        positions = result['positions']
                    if result['score'] > bestScore:
                        if errorLog:
                            print "assign value: ", result['score'], bestScore, result['score'],result['move']
                        bestScore = result['score']
                        bestMove = move #result['move']
                    if bestScore > beta:
                        if errorLog:
                            print 'return from place3:'
                            print "a-b-d: ", alpha,beta,depth
                            print {'move': bestMove, 'score': beta, 'positions': positions}
                        return {'move': move, 'score': beta, 'positions': positions}
            if errorLog:
                print 'return from place9:'
                print "!!!!!!!!!!!!!!!!!!!end of new search: ",depth, alpha, beta, isPlayer, positions
                print {'move': bestMove, 'score': bestScore, 'positions': positions}
            if bestMove == -1 and not errorLog:
                #print "uncommon return bestMove==-1, activate errorLog: "
                #self.search(args[0],args[1],args[2],args[3],args[4],args[5],args[6])
                possList = grid.getAvailableMoves()
                if len(possList)>0:
                    bestMove = possList[randint(0,len(possList)-1)]
                elif 0:
                    from Displayer import Displayer
                    self.displayer = Displayer()
                    print "This grid returns no available move: "
                    self.displayer.display(self.grid)
            return {'move': bestMove, 'score': bestScore, 'positions': positions}
        # computer turn
        else:
            bestScore = beta
            candidates = []
            cells = grid.getAvailableCells()
            scores = {2: [], 4: []}
            for value in scores.keys():
                for cell in cells:
                    newGrid = grid.clone()
                    newGrid.insertTile(cell,value)
                    tmp = -self.smoothness(newGrid) + self.island(newGrid)
                    scores[value].append(tmp)
            maxScore = max(scores[2]+scores[4])
            for value in scores.keys():
                for i in range(len(scores[value])):
                    if scores[value][i] == maxScore:
                        candidates.append({'position': cells[i], 'value': value})

            # search on each candidate
            for i in range(len(candidates)):
                position = candidates[i]['position']
                value = candidates[i]['value']
                newGrid = grid.clone()
                newGrid.insertTile(position, value)
                positions += 1
                result = self.search(newGrid, depth, alpha, bestScore, positions, True)
                positions = result['positions']
                if result['score'] < bestScore:
                    bestScore = result['score']
                    bestMove = result['move']
                if bestScore < alpha:
                    if errorLog:
                        print 'return from place 4'
                        print "a-b-d: ", alpha,beta,depth
                        print {'move': None, 'score': alpha, 'positions': positions}
                    return {'move': None, 'score': alpha, 'positions': positions}
            if errorLog:
                print "from place 5"
                print "a-b: ", alpha,beta
                print {'move': bestMove, 'score': bestScore, 'positions': positions}
            return {'move': bestMove, 'score': bestScore, 'positions': positions}

    def iterativeDeep(self, grid):

        depth = 0
        best = None
        while 1:
            start = time.clock()
            newBest = self.search(grid, depth, -infinity, infinity, 0, True)
            end = time.clock()
            if (end-start > 0.15):
                print "time usage per step: ", time.clock()-start
                #print 'depth', depth
                break
            if newBest['move'] == -1:
                print 'break ahead'
                break
            else:
                best = newBest
            depth += 1
        return best


    # The return value of getMove() in PlayerAI is an integer indicating the direction (UP, DOWN, LEFT, RIGHT) = (0,1,2,3)
    def getMove(self, grid):

        availableMethods ={'c':'categoricalDeep',"i":'iterativeDeep'}
        method = availableMethods['c']

        emptyCellNum = len(grid.getAvailableCells())

        #self.move = int(self.alphabeta_search(grid, 6))
        if method == 'iterativeDeep':
            self.move = int(self.iterativeDeep(grid)['move'])

        if method == 'categoricalDeep':
            depth = 1
            if emptyCellNum < 6:
                depth = 3
            if emptyCellNum < 3:
                depth = 3
            if emptyCellNum <= 1:
                depth = 3
            self.move = int(self.search(grid,depth,-infinity,infinity,0,True)['move'])

        print self.move
        if self.move != -1:
            return self.move
        else:
            return False


