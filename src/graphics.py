import math
import pygame
import random

import helpers

#Check fx.py for temporary effects.

class Background:
	def __init__(self,main):
		self.main = main
		self.image = pygame.transform.smoothscale(helpers.loadPNG('background'),(self.main.SCREEN_WIDTH,self.main.SCREEN_HEIGHT))
	def compute(self):
		pass
	def draw(self,surface):
		surface.blit(self.image,(0,0))

class Cursor:
	def __init__(self,main):
		self.drawPriority = 2
		self.main = main
		self.on = 1
		self.size = 40
		self.normalImage = pygame.transform.smoothscale(helpers.loadPNG('cursor'),(self.size,self.size))
		self.bombImage = pygame.transform.smoothscale(helpers.loadPNG('bombCursor'),(self.size,self.size))
		self.bombOn = 0
		self.pos = (0,0)
	def compute(self):
		self.pos = [self.main.mousePos[0] - self.size/2, self.main.mousePos[1] - self.size/2]
	def draw(self,surface):
		if 1:#self.on: #I decided to let it be on all the time.
			if self.bombOn:
				surface.blit(self.bombImage,self.pos)
			else:
				surface.blit(self.normalImage,self.pos)

class GridBackground:
	def __init__(self,blockManager):
		self.image = pygame.transform.smoothscale(helpers.loadPNG('gridBG'),(360,720))
		self.blockManager = blockManager
	def compute(self):
		pass
	def draw(self,surface):
		surface.blit(self.image,(self.blockManager.indentX,self.blockManager.indentY))


class GridForeground:
	def __init__(self,blockManager):
		self.image = pygame.transform.smoothscale(helpers.loadPNG('grid'),(360,720))
		self.image2 = helpers.loadPNG('gridCover')
		self.blockManager = blockManager
	def compute(self):
		pass
	def draw(self,surface):
		surface.blit(self.image,(self.blockManager.indentX,self.blockManager.indentY))
		surface.blit(self.image2,(0,0))

class HighlightDrawer:
	def __init__(self,main,blockManager):
		self.drawPriority = 2
		self.main = main
		self.blockManager = blockManager
		self.horizHighlightImage = pygame.transform.smoothscale(helpers.loadPNG('highlightH'), \
																(self.blockManager.gridWidth*self.blockManager.blockSize,self.blockManager.blockSize))
		self.vertiHighlightImage = pygame.transform.smoothscale(helpers.loadPNG('highlightV'), \
																(self.blockManager.blockSize,self.blockManager.gridHeight*self.blockManager.blockSize))

	def compute(self):
		pass

	def draw(self,surface):
		if not self.main.hasItem:
			if self.blockManager.movementType == 'hSlider':
				surface.blit(self.horizHighlightImage,(self.blockManager.indentX,self.blockManager.indentY + self.blockManager.mouseGridY*self.blockManager.blockSize))
			elif self.blockManager.movementType == 'vSlider':
				surface.blit(self.vertiHighlightImage,(self.blockManager.indentX + self.blockManager.mouseGridX*self.blockManager.blockSize,self.blockManager.indentY))

class Star:
	def __init__(self,blockManager,x,y):
		'''Shows stars where blocks have recently been destroyed.'''
		self.blockManager = blockManager
		self.pos = (x,y)
		self.image = helpers.loadPNG('star')
		self.alpha = 255
		self.lastTime = 64
		self.maxImageSize = 128
		self.imageSize = self.maxImageSize
		self.maxRotate = (random.random()*2+1)*math.pi*2
		if random.random() < .5:
			self.maxRotate *= -1
		self.rotate = 0
		self.time = 0

	def compute(self):
		self.alpha = 255*(1 - float(self.time)/self.lastTime)
		self.imageSize = self.maxImageSize*(1 - float(self.time)/self.lastTime)
		self.rotate = self.maxRotate*(1 - float(self.time)/self.lastTime)
		self.time += 1

		if self.time == self.lastTime:
			self.dead = 1

	def draw(self,surface):
		scale = self.imageSize/self.image.get_width()
		rotated = pygame.transform.rotozoom(self.image,self.rotate*180/math.pi,scale)

		#Fill it in a random bright saturated opaque color.
		colorSurf = pygame.Surface(rotated.get_size())
		color = pygame.Color(0,0,0,0)
		h = random.random()*360
		color.hsva = (h,100,100,100)
		colorSurf.fill(color)
		rotated.blit(colorSurf,(0,0),None,pygame.BLEND_MULT)

		rect = rotated.get_rect(center=(self.pos))
		s = pygame.Surface(rect.size)
		s.fill((0,0,0))
		rect2 = pygame.rect.Rect(rect) #Make sure rect2 is in surface
		blitX = 0
		blitY = 0
		if rect2.left < 0:
			rect2.width += rect2.left #Is decreased
			rect2.left = 0
			blitX = rect.width - rect2.width
		if rect2.top < 0:
			rect2.height += rect2.top
			rect2.top = 0
			blitY = rect.height - rect2.height
		if rect2.right > surface.get_width():
			rect2.width = surface.get_width() - rect2.left
		if rect2.bottom > surface.get_height():
			rect2.height = surface.get_height() - rect2.top
		s2 = surface.subsurface(rect2).copy()
		#pygame.draw.rect(surface,(0,0,0),rect2,4)
		s.blit(s2,(blitX,blitY))
		s.blit(rotated,(0,0))
		s.set_alpha(self.alpha)
		surface.blit(s,rect.topleft)

