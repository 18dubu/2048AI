#!/usr/bin/env python
#coding:utf-8

from random import randint
from BaseAI import BaseAI
from utils import *
import random

class ComputerAI(BaseAI):

	def alphabeta_search(state, game, d=4, cutoff_test=None, eval_fn=None):
		"""Search game to determine best action; use alpha-beta pruning.
		This version cuts off search and uses an evaluation function."""

		player = game.to_move(state)


		def max_value(state, alpha, beta, depth):
			if cutoff_test(state, depth):
				return eval_fn(state)
			v = -infinity
			for (a, s) in game.successors(state):
				v = max(v, min_value(s, alpha, beta, depth+1))
				if v >= beta:
					return v
				alpha = max(alpha, v)
			return v

		def min_value(state, alpha, beta, depth):
			if cutoff_test(state, depth):
				return eval_fn(state)
			v = infinity
			for (a, s) in game.successors(state):
				v = min(v, max_value(s, alpha, beta, depth+1))
				if v <= alpha:
					return v
				beta = min(beta, v)
			return v

		# Body of alphabeta_search starts here:
		# The default test cuts off at depth d or at a terminal state
		cutoff_test = (cutoff_test or
					   (lambda state,depth: depth > d or game.terminal_test(state)))
		eval_fn = eval_fn or (lambda state: game.utility(state, player))
		action, state = argmax(game.successors(state),
							   lambda ((a, s)): min_value(s, -infinity, infinity, 0))
		return action

	# the return value of getMove() in computer AI is a tuple(x,y) indicating the position that you want to insert.
	def getMove(self, grid):
		# I’m too simple, please change me!
		cells = grid.getAvailableCells()

		return cells[randint(0, len(cells) - 1)] if cells else None

