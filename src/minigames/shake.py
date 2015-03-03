import math
import os
import pygame
import random

import helpers

class Shake:
	def __init__(self,manager):
		self.manager = manager

		if self.manager.difficulty == 1:
			self.level = 1
		elif self.manager.difficulty <= 3:
			self.level = 2
		elif self.manager.difficulty <= 5:
			self.level = 3
		else:
			self.level = 4

		if self.level == 1:
			self.bgImage = None
			self.peepsImage = helpers.loadPNG(os.path.join('minigames','shake','shake'),0)
			self.fgImage = None
			self.winImage = None
		if self.level == 2:
			self.bgImage = helpers.loadPNG(os.path.join('minigames','shake','scene1BG'),0)
			self.peepsImage = helpers.loadPNG(os.path.join('minigames','shake','scene1Peeps'),0)
			self.fgImage = helpers.loadPNG(os.path.join('minigames','shake','scene1FG'),0)
			self.winImage = helpers.loadPNG(os.path.join('minigames','shake','scene1Win'),0)
			self.shakeSize = 30
		if self.level == 3:
			self.bgImage = helpers.loadPNG(os.path.join('minigames','shake','scene2BG'),0)
			self.peepsImage = helpers.loadPNG(os.path.join('minigames','shake','scene2Peeps'),0)
			self.fgImage = None
			self.winImage = helpers.loadPNG(os.path.join('minigames','shake','scene2Win'),0)
			self.shakeSize = 15
		if self.level == 4:
			self.bgImage = None
			self.peepsImage = helpers.loadPNG(os.path.join('minigames','shake','scene3'),0)
			self.fgImage = None
			self.winImage = helpers.loadPNG(os.path.join('minigames','shake','scene3win'),0)

		self.neededShakeAmount = 3000
		self.shakeAmount = 0
		self.curShake = 0
		self.oldk = (.01,0)

		self.time = 350 - 30*self.manager.difficulty

		#A very short animation when you win.
		self.won = 0
		self.winTime = 22 - 2*self.manager.difficulty

		self.music = helpers.loadOGG('shake')
		self.music.set_volume(self.manager.main.normMusicVolume)
		self.music.play()

	def compute(self):
		k = pygame.mouse.get_rel()
		pygame.mouse.set_pos(self.manager.SCREEN_WIDTH/2,self.manager.SCREEN_HEIGHT/2)
		#Shake amount depends on both the distance and the angle change from before.
		distance = math.sqrt(k[0]**2 + k[1]**2)
		angleChange = helpers.angleDifference(math.atan2(k[1],k[0]),math.atan2(self.oldk[1],self.oldk[0]))
		'''angleChange1 = abs(math.atan2(k[1],k[0]) - math.atan2(self.oldk[1],self.oldk[0]))
		angleChange2 = math.pi*2 - angleChange1 #Because .001 and math.pi*2 - .001 are .002 apart
		angleChange = min(angleChange1,angleChange2)'''
		self.curShake = distance*(angleChange/math.pi)
		self.shakeAmount += self.curShake

		self.oldk = k

		if self.shakeAmount >= self.neededShakeAmount:
			#If you have a winning image to display, do so and take up self.winTime frames. If not, just end the minigame.
			if self.winImage:
				self.won = 1
			else:
				self.manager.win()

		if self.won:
			self.winTime -= 1
			if self.winTime == 0:
				self.manager.win()

		self.time -= 1
		if self.time == 0 and not self.won:
			self.manager.lose()


	def draw(self,surface):
		if self.bgImage:
			surface.blit(self.bgImage,(0,0))

		'''r = (self.image.get_width() - surface.get_width())/2.0 /2
		maxShake = 20.0
		thisShake = min(self.curShake,maxShake)/maxShake
		ang = random.random()*math.pi*2
		pos = (-r - r*thisShake*math.cos(ang),-r - r*thisShake*math.sin(ang))
		surface.blit(self.image,pos)'''

		#Shaken part is transparent on edges, only takes up SCREEN_WIDTH,SCREEN_HEIGHT. For peeps
		if not (self.level == 3 and self.won): #If level 2, after winning the original vase disappears giving way to the dead vase.
			tab = (self.peepsImage.get_width() - surface.get_width())/2
			if tab > 0:
				r = tab
			else:
				r = self.shakeSize
			maxShake = 20.0
			thisShake = min(self.curShake,maxShake)/maxShake
			ang = random.random()*math.pi*2
			pos = (-tab + r*thisShake*math.cos(ang),-tab + r*thisShake*math.sin(ang))
			surface.blit(self.peepsImage,pos)

		if self.fgImage:
			surface.blit(self.fgImage,(0,0))

		if self.won:
			self.winDraw(surface)

	def winDraw(self,surface):
		surface.blit(self.winImage,(0,0))
