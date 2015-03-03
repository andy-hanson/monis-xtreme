import pygame
import random

import block
import graphics
import helpers
import movementSwitcher

class BlockManager:
	def __init__(self,main):
		self.main = main


		self.on = 1 #Used during testing, to ensure full framerate.

		self.indentX = 40
		self.indentY = 40
		self.blockSize = 40
		self.gridWidth = 9
		self.gridHeight = 18

		self.numCols = 8 #The number of colors
		self.images = []
		for x in xrange(0,self.numCols):
			self.images.append(pygame.transform.scale(helpers.loadPNG(str(x)),(self.blockSize,self.blockSize)))

		#Make the grid!
		self.grid = []
		for x in xrange(0,self.gridWidth):
			newColumn = []
			for y in xrange(0,self.gridHeight):
				newColumn.append(None)
			self.grid.append(newColumn)

		self.movementType = 'original'

		self.neededAdjacents = 5

		self.maxTimeTillFall = 8 #Compare to 256
		self.timeTillFall = self.maxTimeTillFall

		self.maxTimeTillNewBlock = 16 #Compare to 256
		self.timeTillNewBlock = self.maxTimeTillNewBlock

		self.mouseGridX = 0
		self.mouseGridY = 0

		self.movementSwitcher = movementSwitcher.MovementSwitcher(self)

		self.highlightDrawer = graphics.HighlightDrawer(self.main,self)
		self.main.objects.append(self.highlightDrawer)

		self.running = 1 #Whether it does anything! Used for BigBomb

		#self.scorer given by Main.

		if self.main.monis:
			self.fillGridBottom()

		self.fillingBottom = 0

	def compute(self):
		if self.on:
			if self.running:
				if self.movementType != 'vSlider':
					self.timeTillFall -= 1
					if self.timeTillFall == 0:
						self.moveBlocksDown()
						self.timeTillFall = self.maxTimeTillFall

					self.timeTillNewBlock -= 1
					if self.timeTillNewBlock == 0:
						self.getNewBlock()
						self.timeTillNewBlock = self.maxTimeTillNewBlock

				if not self.main.hasItem:
					self.useMovement() #original,hSlider,vSlider

				for point in self.iterateGrid():
					point.compute()

				self.checkAdj()

		self.movementSwitcher.compute()


	def draw(self,surface):
		if self.on:
			for point in self.iterateGrid():
				point.draw(surface)

		self.movementSwitcher.draw(surface)



	def checkAdj(self):
		hadRemoval = 0 #For fillingBottom
		for x in xrange(0,self.gridWidth):
			for y in xrange(0,self.gridHeight):
				if self.grid[x][y] and self.grid[x][y].recentlyMoved:
					adjs = self.checkBlockForAdjacents(x,y)
					if len(adjs) >= self.neededAdjacents:
						for p in adjs:
							self.destroyPoint(p[0],p[1])
						if self.fillingBottom:
							hadRemoval = 1
						else:
							self.scorer.getPoints(len(adjs))
					else:
						#It wasn't destroyed
						self.grid[x][y].recentlyMoved = 0

		if self.fillingBottom:
			return hadRemoval

	def checkBlockForAdjacents(self,x,y):
		l = [(x,y)] #List of all adjacent blocks with the same color
		lastLen = 0
		while lastLen != len(l):
			lastLen = len(l)
			oldL = list(l)
			for p in oldL:
				for newP in self.getNearSames(p[0],p[1]):
					l.append(newP)
			l = helpers.removeRepeats(l)
		return l

	def destroyPoint(self,x,y):
		self.grid[x][y] = None
		convertedX = self.indentX + x*self.blockSize + self.blockSize/2 #Get the center of the square
		convertedY = self.indentY + y*self.blockSize + self.blockSize/2
		self.main.objects.append(graphics.Star(self,convertedX,convertedY))

	def getNearSames(self,x,y):
		col = self.grid[x][y].col
		l = [(x,y)]
		ps = [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]
		for p in ps:
			if 0 <= p[0] < self.gridWidth and 0 <= p[1] < self.gridHeight:
				if self.grid[p[0]][p[1]] and self.grid[p[0]][p[1]].col == col:
					l.append((p[0],p[1]))
		return l

	def getNewBlock(self):
		#Check if the grid is full.
		hasEmpty = 0
		for x in xrange(0,self.gridWidth):
			if self.grid[x][0] is None:
				hasEmpty = 1

		if hasEmpty:
			pos = random.randint(0,self.gridWidth - 1)
			while self.grid[pos][0] is not None:
				pos = random.randint(0,self.gridWidth - 1)
			col = random.randint(0,self.numCols - 1)
			self.grid[pos][0] = block.Block(self,pos,0,col)

		else:
			self.main.lost = 1

	def iterateGrid(self):
		for x in xrange(0,self.gridWidth):
			for y in xrange(0,self.gridHeight):
				if self.grid[x][y]:
					yield self.grid[x][y]
	def mouseXToGridX(self,mouseX):
		x = (mouseX - self.indentX)/self.blockSize
		if 0 <= x < self.gridWidth:
			return x
		else:
			return 'badPos'
	def mouseYToGridY(self,mouseY):
		y = (mouseY - self.indentY)/self.blockSize
		if 0 <= y < self.gridHeight:
			return y
		else:
			return 'badPos'
	def mousePosToGridPos(self,mousePos):
		pos = (self.mouseXToGridX(mousePos[0]),self.mouseYToGridY(mousePos[1]))
		if pos[0] == 'badPos' or pos[1] == 'badPos':
			return 'badPos'
		else:
			return pos

	def moveBlocksDown(self):
		#Move all blocks down.
		for x in xrange(0,self.gridWidth):
			for y in xrange(self.gridHeight-2,-1,-1): #From gridHeight-2 to 0. Blocks on the bottom (y=gridHeight - 1) won't move down no matter what.
				if self.grid[x][y] and not self.grid[x][y + 1]:
					self.grid[x][y + 1] = self.grid[x][y]
					self.grid[x][y + 1].xPos = x
					self.grid[x][y + 1].yPos = y + 1
					self.grid[x][y + 1].recentlyMoved = 1
					self.grid[x][y] = None

	def moveH(self,gridY,amount):
		#Shift a row left or right
		newRow = []
		for x in xrange(0,self.gridWidth):
			wanted = x - amount
			if wanted < 0:
				wanted += self.gridWidth
			elif wanted >= self.gridWidth:
				wanted -= self.gridWidth
			newRow.append(self.grid[wanted][gridY])
		for x in xrange(0,self.gridWidth):
			self.grid[x][gridY] = newRow[x]
			if self.grid[x][gridY]: #If it's not empty:
				self.grid[x][gridY].xPos = x
				self.grid[x][gridY].recentlyMoved = 1

	def moveV(self,gridX,amount):
		#Shift a row up or down
		newColumn = []
		for y in xrange(0,self.gridHeight):
			wanted = y - amount
			if wanted < 0:
				wanted += self.gridHeight
			if wanted >= self.gridHeight:
				wanted -= self.gridHeight
			newColumn.append(self.grid[gridX][wanted])
		for y in xrange(0,self.gridHeight):
			self.grid[gridX][y] = newColumn[y]
			if self.grid[gridX][y]:
				self.grid[gridX][y].yPos = y
				self.grid[gridX][y].recentlyMoved = 1

	def setAllRecentlyMoved(self):
		for block in self.iterateGrid():
			block.recentlyMoved = 1

	def useMovement(self):
		if self.movementType == 'original':
			#All blocks which do not have either another block or the ground below them will move in that direction.
			if self.main.mouseLeftDown:
				for y in xrange(self.gridHeight-2,-1,-1): #From gridHeight-2 to 0. Blocks on the bottom (y=gridHeight - 1) won't move left no matter what.
					for x in xrange(1,self.gridWidth): #From 1 to gridWidth-1. Blocks on the left (x=0) won't move left no matter what.
						if self.grid[x][y] and  not self.grid[x - 1][y] and not self.grid[x][y + 1]:
							self.grid[x - 1][y] = self.grid[x][y]
							self.grid[x - 1][y].xPos = x - 1
							self.grid[x - 1][y].recentlyMoved = 1
							self.grid[x][y] = None

			elif self.main.mouseRightDown:
				for y in xrange(self.gridHeight-2,-1,-1): #From gridHeight-2 to 0. Blocks on the bottom (y=gridHeight - 1) won't move right no matter what.
					for x in xrange(self.gridWidth-2,-1,-1): #From gridWidth-2 to 0. Blocks on the right (x=gridWidth - 1) won't move right no matter what.
						if self.grid[x][y] and not self.grid[x + 1][y] and not self.grid[x][y + 1]:
							self.grid[x + 1][y] = self.grid[x][y]
							self.grid[x + 1][y].xPos = x + 1
							self.grid[x + 1][y].recentlyMoved = 1
							self.grid[x][y] = None

		elif self.movementType == 'hSlider':
			self.mouseGridY = (self.main.mousePos[1] - self.indentY)/self.blockSize #Integer division truncates
			if self.mouseGridY < 0:
				self.mouseGridY = 0
			if self.mouseGridY >= self.gridHeight:
				self.mouseGridY = self.gridHeight - 1
			if self.main.mouseLeftDown:
				self.moveH(self.mouseGridY,-1)
			elif self.main.mouseRightDown:
				self.moveH(self.mouseGridY,1)

		elif self.movementType == 'vSlider':
			self.mouseGridX = (self.main.mousePos[0] - self.indentX)/self.blockSize #Integer division truncates
			if self.mouseGridX < 0:
				self.mouseGridX = 0
			if self.mouseGridX >= self.gridWidth:
				self.mouseGridX = self.gridWidth - 1
			if self.main.mouseUpDown:
				self.moveV(self.mouseGridX,-1)
			elif self.main.mouseDownDown:
				self.moveV(self.mouseGridX,1)

	def fillGridBottom(self):
		self.fillingBottom = 1

		hasRemoval = 1

		while hasRemoval: #Keep filling it up and checking for adjacencies until you get a set without them.
			for x in xrange(0,self.gridWidth):
				for y in xrange(self.gridHeight/2,self.gridHeight):
					self.grid[x][y] = block.Block(self,x,y,random.randint(0,self.numCols-1))

			hasRemoval = self.checkAdj()
