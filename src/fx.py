import math
#import numpy
import os
import pygame
import random

import helpers

class FXManager:
	def __init__(self,main):
		self.main = main
		self.numFX = 1
		self.fx = []
		self.possibleEffects = ['Flip(self.main)','Blur(self.main)','Wobble(self.main)','Wrap(self.main)' \
								,'PixelAddSub(self.main)', 'Noise(self.main)','Fragment(self.main)','DiscoLights(self.main)']
		#Note: Blur, TimeDistort, Noise, Fragment, and DiscoLights should not make gameplay much harder.
		self.fxTime = self.main.movementSwitchK
		#self.getFX()
		self.prob = 0 #The probability after each round that a minigame will appear.

		self.running = 1 #Whether it does anything!

	def compute(self):
		if self.running:
			for fx in self.fx:
				fx.time -= 1
				if fx.time == 0:
					fx.die()
					self.fx.remove(fx)
					#self.getFX()
				else:
					fx.compute()

	def draw(self,surface):
		if self.running:
			for fx in self.fx:
				fx.draw(surface)

	def getFX(self):
		#Randomly selects an FX.
		r = random.randint(0,len(self.possibleEffects) - 1)
		fx = eval(self.possibleEffects[r])
		fx.time = self.fxTime
		self.fx.append(fx)

	def getNewMovementType(self):
		if random.random() < self.prob:
			self.getFX()

def Flip(main):
	if random.random() < .5:
		return VFlip(main)
	else:
		return HFlip(main)

class VFlip:
	def __init__(self,main):
		self.main = main

	def compute(self):
		self.main.mousePos = (self.main.mousePos[0],self.main.SCREEN_HEIGHT - self.main.mousePos[1])

	def draw(self,surface):
		surface.blit(pygame.transform.flip(surface,0,1),(0,0))

	def die(self):
		pass

class HFlip:
	def __init__(self,main):
		self.main = main

	def compute(self):
		self.main.mousePos = (self.main.SCREEN_WIDTH - self.main.mousePos[0],self.main.mousePos[1])

	def draw(self,surface):
		surface.blit(pygame.transform.flip(surface,1,0),(0,0))

	def die(self):
		pass

class Blur:
	def __init__(self,main):
		self.main = main
		self.s = self.main.screen.copy()

	def compute(self):
		pass

	def draw(self,surface):
		p = surface.copy()
		p.set_alpha(48)
		self.s.blit(p,(0,0))
		surface.blit(self.s,(0,0))

	def die(self):
		pass

class Wobble:
	def __init__(self,main):
		'''Whole screen rotates left and right.'''
		self.main = main
		self.maxWobble = 60 #In either direction.
		self.wobble = 0
		self.wobbleTime = 0.0
		self.wobbleLength = self.main.movementSwitchK/2 #Frames

		'''self.minZoom = 1
		self.maxZoom = 1.5
		self.zoom = 1'''

	def compute(self):
		self.wobbleTime += 1
		self.wobble = -self.maxWobble * math.sin(math.pi*self.wobbleTime/self.wobbleLength)
		#self.zoom = self.minZoom + (self.maxZoom - self.minZoom) * math.sin(math.pi*self.time/self.wobbleLength)**2

	def draw(self,surface):
		surface.set_at((0,0),(0,0,0)) #So rotate() uses this as the background
		s = pygame.transform.rotate(surface,self.wobble)#pygame.transform.rotozoom(surface,self.wobble,self.zoom)
		blitX = (surface.get_width() - s.get_width())/2
		blitY = (surface.get_height() - s.get_height())/2
		surface.fill((0,0,0))
		surface.blit(s,(blitX,blitY))

	def die(self):
		pass

def Wrap(main):
	if random.random() < .5:
		return XWrap(main)
	else:
		return YWrap(main)

class XWrap:
	def __init__(self,main):
		self.main = main
		self.pos = 0
		self.moveSpeed = -1.0 * self.main.SCREEN_WIDTH / self.main.movementSwitchK
		self.main.cursor.on = 0

	def compute(self):
		self.pos += self.moveSpeed
		if self.pos < -self.main.SCREEN_WIDTH:
			self.pos += self.main.SCREEN_WIDTH

		newXPos = int(round(self.main.mousePos[0] - self.pos))
		if newXPos >= self.main.SCREEN_WIDTH:
			newXPos -= self.main.SCREEN_WIDTH
		self.main.mousePos = (newXPos, self.main.mousePos[1])

	def draw(self,surface):
		k = surface.copy()
		surface.blit(k,(self.pos,0))
		surface.blit(k,(self.pos+self.main.SCREEN_WIDTH,0))
		self.main.cursor.pos[0] += self.pos
		self.main.cursor.on = 1
		self.main.cursor.draw(surface)
		if self.main.cursor.pos[0] < 0:
			#Draw it again on the right, so it appears to loop.
			self.main.cursor.pos[0] += self.main.SCREEN_WIDTH
			self.main.cursor.draw(surface) #Again

		self.main.cursor.on = 0

	def die(self):
		self.main.cursor.on = 1

class YWrap:
	def __init__(self,main):
		self.main = main
		self.pos = 0
		self.moveSpeed = self.moveSpeed = -1.0 * self.main.SCREEN_HEIGHT / self.main.movementSwitchK
		self.main.cursor.on = 0

	def compute(self):
		self.pos += self.moveSpeed
		if self.pos < -self.main.SCREEN_WIDTH:
			self.pos += self.main.SCREEN_WIDTH

		newYPos = int(round(self.main.mousePos[1] - self.pos))
		if newYPos >= self.main.SCREEN_WIDTH:
			newYPos -= self.main.SCREEN_WIDTH
		self.main.mousePos = (self.main.mousePos[0],newYPos)

	def draw(self,surface):
		k = surface.copy()
		surface.blit(k,(0,self.pos))
		surface.blit(k,(0,self.pos+self.main.SCREEN_HEIGHT))
		self.main.cursor.pos[1] += self.pos
		self.main.cursor.on = 1
		self.main.cursor.draw(surface)
		if self.main.cursor.pos[1] < 0:
			#Draw it again on the bottom, so it appears to loop.
			self.main.cursor.pos[1] += self.main.SCREEN_HEIGHT
			self.main.cursor.draw(surface)

		self.main.cursor.on = 0

	def die(self):
		self.main.cursor.on = 1

class PixelAddSub:
	def __init__(self,main):
		self.main = main
		self.maxAmount = 255 #In either direction
		self.changeTime = 0
		self.length = self.main.movementSwitchK/2
		self.amount = 0

	def compute(self):
		self.changeTime += 1
		self.amount = self.maxAmount * math.sin(math.pi*self.changeTime/self.length)

	def draw(self,surface):
		k = surface.copy()
		if self.amount > 0:
			k.blit(k,(0,0),None,pygame.BLEND_ADD)
		else:
			k.blit(k,(0,0),None,pygame.BLEND_SUB) #Completely black!
		k.set_alpha(abs(self.amount))
		surface.blit(k,(0,0))

	def die(self):
		pass

class Noise:
	def __init__(self,main):
		self.main = main
		self.images = []
		for x in xrange(6):
			self.images.append(helpers.loadPNG(os.path.join('noises','noise' + str(x))))

		self.sound = helpers.loadOGG('noise')
		self.sound.play()

	def compute(self):
		self.sound.set_volume(random.random())

	def draw(self,surface):
		i = random.randint(0,len(self.images)-1)
		if random.randint(0,1):
			surface.blit(self.images[i],(0,0),None,pygame.BLEND_MIN)
		else:
			surface.blit(self.images[i],(0,0),None,pygame.BLEND_MAX)

	def die(self):
		pass

class Fragment:
	def __init__(self,main):
		self.main = main
		self.numFragments = 4
		self.dist = 8
		self.xBlits = [0]*self.numFragments
		self.yBlits = [0]*self.numFragments

	def compute(self):
		for i in xrange(0,self.numFragments):
			self.xBlits[i] = random.randint(-self.dist,self.dist)
			self.yBlits[i] = random.randint(-self.dist,self.dist)

	def draw(self,surface):
		k = surface.copy()
		k.set_alpha(int(round(255.0/(self.numFragments+1))))
		for i in xrange(0,self.numFragments):
			surface.blit(k,(self.xBlits[i],self.yBlits[i]))

	def die(self):
		pass

class DiscoLights:
	def __init__(self,main):
		self.main = main
		#Uses hsv color.
		#H = [0, 360]
		self.frame = 0
		self.totalTime = self.main.movementSwitchK

	def compute(self):
		self.frame += 1

	def draw(self,surface):
		col = pygame.Color(0,0,0)
		h = 360*self.frame/self.totalTime
		s = 100
		v = 50
		a = 100
		col.hsva = (h,s,v,a)
		s = pygame.Surface(surface.get_size())
		s.fill(col)
		surface.blit(s,(0,0),None,pygame.BLEND_ADD)

	def die(self):
		self.die
