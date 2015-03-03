import os

import helpers


def calcLevel(score):
	if score < 10:
		return 0
	elif score < 25:
		return 1
	elif score < 45:
		return 2
	elif score < 70:
		return 3
	elif score < 100:
		return 4
	elif score < 135:
		return 5
	elif score < 175:
		return 6
	elif score < 220:
		return 7
	else:
		return 8


class DifficultyManager:
	#Controls the flow of the game.
	#Minigames have 6 difficulty levels, but there are 8 levels for the game.
	#Level 1
	def __init__(self,main):
		self.main = main
		self.level = 0

	def compute(self):
		level = calcLevel(self.main.scorer.score)
		if self.level != level:
			if self.main.PRINT_INFO:
				print 'Level change: ' + str(self.level) + ' at score ' + str(self.main.scorer.score)

			self.level = level
			if self.level == 8:
				self.main.won = 1
				self.main.scorer.score = 220
				return
			if self.level == 0:
				self.main.fxManager.prob = 0
				self.main.minigameManager.prob = 0
				self.main.minigameManager.difficulty = 1
				self.main.blockManager.maxTimeTillFall = 24
			if self.level == 1:
				self.main.fxManager.prob = 4.0/8
				self.main.minigameManager.prob = 2.0/8
				self.main.minigameManager.difficulty = 1
				self.main.blockManager.maxTimeTillFall = 20
			if self.level == 2:
				self.main.fxManager.prob = 5.0/8
				self.main.minigameManager.prob = 4.0/8
				self.main.minigameManager.difficulty = 1
				self.main.blockManager.maxTimeTillFall = 16
			if self.level == 3:
				self.main.fxManager.prob = 6.0/8
				self.main.minigameManager.prob = 5.0/8
				self.main.minigameManager.difficulty = 2
				self.main.blockManager.maxTimeTillFall = 12
			if self.level == 4:
				self.main.fxManager.prob = 7.0/8
				self.main.minigameManager.prob = 6.0/8
				self.main.minigameManager.difficulty = 3
				self.main.blockManager.maxTimeTillFall = 10
			if self.level == 5:
				self.main.fxManager.prob = 1
				self.main.minigameManager.prob = 7.0/8
				self.main.minigameManager.difficulty = 4
				self.main.blockManager.maxTimeTillFall = 9
			if self.level == 6:
				self.main.fxManager.prob = 1
				self.main.minigameManager.prob = 1
				self.main.minigameManager.difficulty = 5
				self.main.blockManager.maxTimeTillFall = 8
			if self.level == 7:
				self.main.fxManager.prob = 1
				self.main.minigameManager.prob = 1
				self.main.minigameManager.difficulty = 6
				self.main.blockManager.maxTimeTillFall = 7

			self.main.blockManager.maxTimeTillNewBlock = self.main.blockManager.maxTimeTillFall * 2

			self.main.sillinessManager.newSillyChance = 2 ** (-13 + self.level) #From 2**-13 to 2**-6

	def draw(self,surface):
		pass
