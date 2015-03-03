import math
import os
import pygame
import random

import helpers
import graphics

class Trace:
	def __init__(self,manager):
		self.manager = manager

		self.dotRad = int(round(24 - 12 * math.sqrt(self.manager.difficulty/6.0)))
		self.speed = 12.0 / 6 + 1.0 / 6 * self.manager.difficulty

		self.bg = helpers.loadPNG(os.path.join('minigames','trace','bg'),0)
		dotUnscaled = helpers.loadPNG(os.path.join('minigames','trace','dot'),0)
		self.dotImage = pygame.transform.smoothscale(dotUnscaled, (self.dotRad*2,self.dotRad*2))
		self.cursor = graphics.Cursor(self) #Trace will act as Cursor's main.

		self.numDots = 800
		self.dots = []
		a = random.random()*2*math.pi
		pos = [self.manager.SCREEN_WIDTH/2 + self.manager.SCREEN_WIDTH/3*math.cos(a), self.manager.SCREEN_HEIGHT/2 + self.manager.SCREEN_HEIGHT/3*math.sin(a)]
		ang = a + math.pi + (random.random()*2-1)*math.pi/2 #Start going generally towards the center.
		angChangeMult = 0
		for i in xrange(self.numDots):
			if ang >= 2*math.pi:
				ang -= 2*math.pi
			if ang < 0:
				ang += 2*math.pi
			#Must turn towards the center.
			towardsCenter = math.atan2(self.manager.SCREEN_HEIGHT/2 - pos[1], self.manager.SCREEN_WIDTH/2 - pos[0])
			if towardsCenter < 0:
				towardsCenter += math.pi*2
			#The change in angle needed to be going straight towards the center if turning right:
			angleChangeRight = ang - towardsCenter
			if angleChangeRight < 0:
				angleChangeRight = (2*math.pi + ang) - towardsCenter
			#If turning left:
			angleChangeLeft = towardsCenter - ang
			if angleChangeLeft < 0:
				angleChangeLeft = towardsCenter - (ang - 2*math.pi)

			turningRight = angleChangeRight <= angleChangeLeft

			if random.random() > angChangeMult:
				angChangeMult += .12*(math.sin(i/32)+1)/2
			else:
				angChangeMult -= .12*(math.sin(i/32)+1)/2
			if random.random() < 1.0/12:
				angChangeMult = 1
			if angChangeMult < 0:
				angChangeMult = 0
			if angChangeMult > 1:
				angChangeMult = 1

			if turningRight:
				ang -= angChangeMult**2*math.pi/48
			else:
				ang += angChangeMult**2*math.pi/48

			pos[0] += (self.speed*math.cos(ang))
			pos[1] += (self.speed*math.sin(ang))

			tab = 40
			if pos[0] < tab or pos[0] > self.manager.SCREEN_WIDTH - tab or pos[1] < tab or pos[1] > self.manager.SCREEN_HEIGHT - tab:
				ang += math.pi

			self.dots.append(self.Dot(self,pos[0],pos[1],angChangeMult))

		self.curDot = 0
		self.destroyingDots = 0
		self.dotDestroyBegin = 200

		self.music = helpers.loadOGG('trace')
		self.music.set_volume(0)
		self.music.play()
		#MistakeSound plays when the player skips some dots. (hit-hit-not hit-hit)
		self.mistakeSound = helpers.loadOGG('traceMistake')
		self.mistakeSound.set_volume(self.manager.main.normSoundVolume)
		self.recentlyMadeMistake = 0 #Once a mistake

	def compute(self):
		self.mousePos = self.manager.mousePos

		if self.curDot < self.dotDestroyBegin:
			self.curDot += 1
		if len(self.dots) == 0: #No more dots.
			self.manager.win()

		if self.curDot > len(self.dots):
			self.curDot = len(self.dots)

		hitDot = 0
		for i in xrange(self.curDot):
			dot = self.dots[i]
			#Check if the mouse is in the dot.
			if math.sqrt((self.mousePos[0] - dot.x)**2 + (self.mousePos[1] - dot.y)**2) < self.dotRad:
				self.dots[i].hit = 1
				hitDot = 1

		if self.curDot >= self.dotDestroyBegin:
			self.destroyingDots = 1
		if self.destroyingDots:
			if self.dots[0].hit:
				self.dots.remove(self.dots[0])
			else:
				self.manager.lose()

		if self.curDot > len(self.dots):
			self.curDot = len(self.dots)

		if len(self.dots) == 0: #No more dots.
			self.manager.win()

		self.cursor.compute()

		if hitDot:
			self.music.set_volume(self.manager.main.normMusicVolume)
		else:
			self.music.set_volume(0)

		#Check for mistakes. Must find an unhit dot, then a hit one later.
		hasMistake = 0
		foundUnhit = 0
		for i in xrange(self.curDot):
			if not self.dots[i].hit:
				foundUnhit = 1
			else:
				if foundUnhit:
					hasMistake = 1

		if hasMistake:
			if not self.recentlyMadeMistake:
				self.mistakeSound.stop()
				self.mistakeSound.play()
				self.recentlyMadeMistake = 1
		else:
			self.recentlyMadeMistake = 0


	def draw(self,surface):
		surface.blit(self.bg,(0,0))
		for i in xrange(self.curDot):
			self.dots[i].draw(surface)

		self.cursor.draw(surface)

	class Dot:
		def __init__(self,trace,x,y,angleChangeMult):
			self.trace = trace
			self.x = x
			self.y = y
			self.angleChangeMult = angleChangeMult
			self.hit = 0 #Whether the mouse has passed over it.

		def draw(self,surface):
			b = self.angleChangeMult*255
			if self.hit:
				col = (0,255,0,255)
			else:
				col = (0,0,b,255)
			img = self.trace.dotImage.copy()
			s = pygame.Surface(img.get_size()).convert_alpha()
			s.fill(col)
			img.blit(s,(0,0),None,pygame.BLEND_RGBA_MULT)
			surface.blit(img,(int(round(self.x)) - img.get_width()/2,int(round(self.y)) - img.get_height()/2))
			#pygame.draw.circle(surface,col,(int(round(self.x)),int(round(self.y))),8)
