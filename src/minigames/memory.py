import os
import pygame
import random

import graphics
import helpers

class Memory:
	def __init__(self,manager):
		self.manager = manager

		self.gridSize = 5
		self.correctGrid = []
		for x in xrange(self.gridSize):
			thisColumn = []
			for y in xrange(self.gridSize):
				thisColumn.append(0)
			self.correctGrid.append(thisColumn)

		self.grid = helpers.copyList(self.correctGrid)

		#Fill in difficulty squares.
		numOn = 5 + self.manager.difficulty
		for i in xrange(numOn):
			while 1:
				x = random.randint(0,self.gridSize-1)
				y = random.randint(0,self.gridSize-1)
				if not self.correctGrid[x][y]:
					self.correctGrid[x][y] = 1
					break

		self.showCorrectTime = 90 - 5*self.manager.difficulty
		self.answerTime = 600 - 50*self.manager.difficulty

		self.BG = helpers.loadPNG(os.path.join('minigames','memory','BG'),0)
		self.image0 = helpers.loadPNG(os.path.join('minigames','memory','0'),0)
		self.image1 = helpers.loadPNG(os.path.join('minigames','memory','1'),0)
		self.image0 = pygame.transform.smoothscale(self.image0,(self.manager.SCREEN_WIDTH/self.gridSize,self.manager.SCREEN_HEIGHT/self.gridSize))
		self.image1 = pygame.transform.smoothscale(self.image1,(self.manager.SCREEN_WIDTH/self.gridSize,self.manager.SCREEN_HEIGHT/self.gridSize))

		self.cursor = graphics.Cursor(self) #Trace will act as Cursor's main.

		self.mousePressed = 0 #If mouse was down before, don't count it again.

		self.sounds = []
		for x in xrange(1,16+1):
			new = helpers.loadOGG('memory' + str(x))
			new.set_volume(self.manager.main.normSoundVolume)
			self.sounds.append(new)
		self.curSound = 0


	def compute(self):
		if self.showCorrectTime:
			self.showCorrectTime -= 1
		else:
			if self.manager.mouseLeftDown or self.manager.mouseRightDown:
				if not self.mousePressed:
					x = self.mousePos[0]/int(self.manager.SCREEN_WIDTH/float(self.gridSize))
					y = self.mousePos[1]/int(self.manager.SCREEN_HEIGHT/float(self.gridSize))
					self.grid[x][y] = not self.grid[x][y]
					#Play a sound, and set up to play the next sound.
					self.sounds[self.curSound].play()
					self.curSound += 1
					if self.curSound >= len(self.sounds):
						self.curSound = 0
			else:
				if self.mousePressed:
					self.mousePressed = 0

			if helpers.equalMatrices(self.grid,self.correctGrid):
				self.manager.win()

			self.answerTime -= 1
			if self.answerTime == 0:
				self.manager.lose()

		self.mousePos = self.manager.mousePos
		self.cursor.compute()

	def draw(self,surface):
		surface.blit(self.BG,(0,0))

		if self.showCorrectTime:
			grid = self.correctGrid
		else:
			grid = self.grid

		for x in xrange(0,self.gridSize):
			for y in xrange(0,self.gridSize):
				if grid[x][y]:
					img = self.image1
				else:
					img = self.image0
				surface.blit(img,(x*surface.get_width()/self.gridSize,y*surface.get_height()/self.gridSize))

		self.cursor.draw(surface)
