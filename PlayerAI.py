#!/usr/bin/env python
#coding:utf-8

from random import randint
from BaseAI import BaseAI
from utils import *
import random


class PlayerAI(BaseAI):
    def __init__(self):
        self.move = -1
        self.eval = 0

    def smoothness(self, grid):  # concept from https://github.com/ov3y/2048-AI/blob/master/js/grid.js smooth function
        smoothness = 0
        for x in range(4):
            for y in range(4):
                if not grid.canInsert((x,y)):
                    currCellValue = log2(grid.map[x][y])
                    for direction in range(2):
                        processed = 0
                        targetCellValue = infinity
                        if direction == 0 and not grid.crossBound((x+1, y)) and grid.map[x+1][y]>0:
                            targetCellValue = log2(grid.map[x+1][y])
                            processed = 1
                        if direction == 1 and not grid.crossBound((x, y+1)) and grid.map[x][y+1]>0:
                            targetCellValue = log2(grid.map[x][y+1])
                            processed = 1
                        if processed != 0:
                            smoothness -= abs(currCellValue - targetCellValue)
        return smoothness

    def monotonicity(self, grid):  # concept from https://github.com/ov3y/2048-AI/blob/master/js/grid.js monotonicity2 function
        totals = [0, 0, 0, 0]
        # up and down direction
        for x in range(4):
            current = 0
            next = current+1
            while(next < 4):
                while next < 4 and not grid.canInsert((x, next)):
                    next += 1
                if (next>=4):
                    next -= 1
                currentValue = 0
                if not grid.canInsert((x,current)):
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
            next = current+1
            while(next < 4):
                while next < 4 and not grid.canInsert((next, y)):
                    next += 1
                if (next>=4):
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

        return max(totals[0],totals[1]) + max(totals[2],totals[3])

    def getMaxTileLocation(self, grid):
        maxTileLocation = (-1, -1)
        maxTile = 0
        for x in xrange(grid.size):
            for y in xrange(grid.size):
                if grid.map[x][y] > maxTile:
                    maxTile = grid.map[x][y]
                    maxTileLocation = [x, y]
        if maxTileLocation[0] != -1:
            return (maxTileLocation[0],maxTileLocation[1])
        else:
            return False

    def isBigTileInCorner(self, grid):
        currLoca = self.getMaxTileLocation(grid)
        if currLoca == (grid.size-1, grid.size-1) or currLoca == (0, 0) or currLoca == (0, grid.size-1) or currLoca == (grid.size-1, 0):
            #print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~in conor~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            #print currLoca
            return True
        else:
            return False

    def willMoveLetBiggestTileOffCorner(self, move, grid):  # assume the biggest tile is in one of the corners
        gridCopy = grid.clone()
        gridCopy.move(move)
        if self.isBigTileInCorner(gridCopy):
            return False
        else:
            return True


    def eval_fn1(self, grid):
        """
        最大的不能离开角落
        不一定大的先合并
        如果走一步能合并不只一对这样比较好
        不用留尽量多的空格
        """
        emptyCellLength = len(grid.getAvailableCells())
        biggestTileInCornerPenalty = 0 # NEGATIVE
        smoothWeight = 1.1
        mono2Weight  = 0.1
        emptyWeight  = 1.0
        maxWeight    = 1.0

        self.eval = self.smoothness(grid) * smoothWeight \
                    + self.monotonicity(grid) * mono2Weight \
                    + log2(emptyCellLength) * emptyWeight \
                    + grid.getMaxTile() * maxWeight
        #(1-self.isBigTileInCorner(grid)) * biggestTileInCornerPenalty +\
        return True

    def alphabeta_search(self, grid, d, cutoff_test=False):
        """
        Search game to determine best action; use alpha-beta pruning.
		This version cuts off search and uses an evaluation function.
		"""

        def max_value(currGrid, alpha, beta, depth):
            if depth > d or not currGrid.canMove():
                self.eval_fn1(currGrid)
                return self.eval
            v = -infinity
            for move in currGrid.getAvailableMoves():  # move is a integer: vecIndex = [UP, DOWN, LEFT, RIGHT] = range(4)
                succGrid = currGrid.clone()
                succGrid.move(move)
                v = max(v, min_value(succGrid, alpha, beta, depth + 1))
                if v >= beta:
                    return v
                alpha = max(alpha, v)
            return v

        def min_value(currGrid, alpha, beta, depth):
            if depth > d or not currGrid.canMove():
                self.eval_fn1(currGrid)
                return self.eval
            v = infinity
            for move in currGrid.getAvailableMoves():
                succGrid = currGrid.clone()
                succGrid.move(move)
                v = min(v, max_value(succGrid, alpha, beta, depth + 1))
                if v <= alpha:
                    return v
                beta = min(beta, v)
            return v

        # Body of alphabeta_search starts here:
        # The default test cuts off at depth d or at a terminal state
        currGrid = grid.clone()
        depth = 0
        successer = []
        #print 'current grid:'
        #print currGrid.map[0][0],currGrid.map[0][1],currGrid.map[0][2],currGrid.map[1][0],currGrid.map[2][0],currGrid.map[1][1]
        for move in currGrid.getAvailableMoves():
            #if self.isBigTileInCorner(currGrid) and self.willMoveLetBiggestTileOffCorner(move, currGrid) and len(currGrid.getAvailableMoves()) > 1:
            #    continue
            succGrid = currGrid.clone()
            succGrid.move(move)
            #print 'turn'+ str(move)
            #print 'succ grid'
            #print succGrid.map[0][0],succGrid.map[0][1],succGrid.map[0][2],succGrid.map[1][0],succGrid.map[2][0],succGrid.map[1][1]

            successer.append((move, succGrid))

        action = -1
        value = -infinity
        for candi in successer:
            if min_value(candi[1], -infinity, infinity, depth) > value:
                action = candi[0]

        return action

    # The return value of getMove() in PlayerAI is an integer indicating the direction (UP, DOWN, LEFT, RIGHT) = (0,1,2,3)
    def getMove(self, grid):
        emptyCellNum = len(grid.getAvailableCells())
        gridCopy = grid.clone()
        preInCorner = self.isBigTileInCorner(gridCopy)
        maxD = int((16 - emptyCellNum)*0.5)
        self.move = int(self.alphabeta_search(grid, 5))
        gridCopy.move(self.move)
        postInCorner = self.isBigTileInCorner(gridCopy)
        if not postInCorner and preInCorner:
            print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~WTF~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        if self.move != -1:
            return self.move
        else:
            return False