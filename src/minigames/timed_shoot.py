import math
import os
import pygame
import random

import helpers


class TimedShoot:
	def __init__(self,manager):
		self.manager = manager

		self.shotSpeed = 20
		self.shotSize = 20
		self.targetSize = int(round(128 - self.manager.difficulty*64/6.0))

		self.explosionGraphics = self.ExplosionGraphics() #Hint of a future game
		self.cannon = self.Cannon(self)
		self.shots = []
		self.targets = []
		numTargets = 5
		minX = 300
		maxX = 700
		for i in xrange(numTargets):
			x = minX + (maxX - minX)*i/(numTargets - 1)
			y = self.manager.SCREEN_HEIGHT/2
			speed = 18.0 - 15.0 * random.random() * i/numTargets
			if random.random() < 0.5:
				speed *= -1
			self.targets.append(self.Target(self,x,y,speed))

		self.BG = helpers.loadPNG(os.path.join('minigames','timedShoot','BG'),0)

		self.timeLeft = 1200 - 125*self.manager.difficulty

		self.laserSound = helpers.loadOGG('laser')
		self.laserSound.set_volume(self.manager.main.normSoundVolume)
		self.hitTargetSound = helpers.loadOGG('hitTarget')
		self.hitTargetSound.set_volume(self.manager.main.normSoundVolume)

	def compute(self):
		self.explosionGraphics.compute()
		self.cannon.compute()
		for shot in self.shots:
			shot.compute()
		for target in self.targets:
			target.compute()

		if len(self.targets) == 0:
			self.manager.win()
		self.timeLeft -= 1
		if self.timeLeft == 0:
			self.manager.lose()

	def draw(self,surface):
		surface.blit(self.BG,(0,0))
		self.cannon.draw(surface)
		for shot in self.shots:
			shot.draw(surface)
		for target in self.targets:
			target.draw(surface)
		self.explosionGraphics.draw(surface)

	class Cannon:
		def __init__(self,timedShoot):
			self.timedShoot = timedShoot
			self.manager = self.timedShoot.manager
			self.y = self.manager.SCREEN_HEIGHT/2
			self.yMargin = 50 #Must stay within margin, even if mouse is outside.
			self.image = helpers.loadPNG(os.path.join('minigames','timedShoot','cannon'),0)
			self.maxTimeTillShoot = 20
			self.timeTillShoot = 0

		def compute(self):
			self.y = self.manager.mousePos[1]
			if self.y < self.yMargin:
				self.y = self.yMargin
			if self.y > self.manager.SCREEN_HEIGHT - self.yMargin:
				self.y = self.manager.SCREEN_HEIGHT - self.yMargin

			if self.timeTillShoot:
				self.timeTillShoot -= 1
			elif self.manager.mouseLeftDown or self.manager.mouseRightDown:
				self.timedShoot.shots.append(self.timedShoot.Shot(self.timedShoot,self.image.get_width(),self.y))
				self.timeTillShoot = self.maxTimeTillShoot
				self.timedShoot.laserSound.play()

		def draw(self,surface):
			surface.blit(self.image,(0,self.y-self.image.get_height()/2))

	class Shot:
		def __init__(self,timedShoot,x,y):
			self.timedShoot = timedShoot
			self.x = x
			self.y = y
			self.speed = self.timedShoot.shotSpeed
			self.size = self.timedShoot.shotSize
			self.image = pygame.transform.smoothscale(helpers.loadPNG(os.path.join('minigames','timedShoot','shot'),0), (self.size,self.size))

		def compute(self):
			self.x += self.speed

		def draw(self,surface):
			surface.blit(self.image,(self.x-self.size, self.y-self.size))

	class Target:
		def __init__(self,timedShoot,x,y,speed):
			self.timedShoot = timedShoot
			self.x = x
			self.y = y
			self.speed = speed
			self.size = self.timedShoot.targetSize
			self.image = pygame.transform.smoothscale(helpers.loadPNG(os.path.join('minigames','timedShoot','target'),0), (self.size,self.size))
			self.yMargin = 16

		def compute(self):
			self.y += self.speed
			if self.y < self.yMargin or self.y > self.timedShoot.manager.SCREEN_HEIGHT - self.yMargin:
				self.speed *= -1

			for shot in self.timedShoot.shots:
				if math.sqrt((shot.x - self.x)**2 + (shot.y - self.y)**2) < self.size/2 + shot.size/2:
					#You collided with the shot.
					self.timedShoot.shots.remove(shot)
					self.explode()
					self.timedShoot.hitTargetSound.play()

		def draw(self,surface):
			surface.blit(self.image,(self.x-self.size/2,self.y-self.size/2))

		def explode(self):
			self.timedShoot.targets.remove(self)
			self.timedShoot.explosionGraphics.getPoint(self.x,self.y)

	class ExplosionGraphics:
		def __init__(self):
			self.explosionLastTime = 20
			self.explosionPoints = [] #X,Y,Time,minRad,maxRad
			self.explosionImage = pygame.image.load(os.path.join('data','minigames','timedShoot','Explosion.tga')).convert_alpha()
			self.xScroll = 0
			self.yScroll = 0

		def compute(self):
			i = 0
			while i < len(self.explosionPoints):
				self.explosionPoints[i][0] += self.xScroll
				self.explosionPoints[i][1] += self.yScroll
				self.explosionPoints[i][2] -= 1
				if self.explosionPoints[i][2] == 0:
					self.explosionPoints.remove(self.explosionPoints[i])
					i -= 1
				i += 1

		def draw(self,surface):
			for p in self.explosionPoints:
				minRad = p[3]
				maxRad = p[4]
				thisRad = minRad + (maxRad-minRad)*(self.explosionLastTime - p[2])/self.explosionLastTime
				scaledImage = pygame.transform.scale(self.explosionImage,(thisRad*2,thisRad*2))

				minX = p[0] - thisRad
				minY = p[1] - thisRad
				#If: Can't take a subsurface if it doesn't intersect at all!
				if minX < surface.get_width() and minY < surface.get_height() and minX + thisRad*2 > 0 and minY + thisRad*2 > 0:
					if minX < 0:
						width = thisRad*2 + minX
						minX = 0
					else:
						width = thisRad*2
					if minY < 0:
						height = thisRad*2 + minY
						minY = 0
					else:
						height = thisRad*2
					if minX + width >= surface.get_width():
						width = surface.get_width() - minX
					if minY + height >= surface.get_height():
						height = surface.get_height() - minY
					tempSurface = surface.subsurface(pygame.Rect(minX,minY,width,height)).copy()
					if minX == 0:
						blitX = width - thisRad*2
					else:
						blitX = 0
					if minY == 0:
						blitY = height - thisRad*2
					else:
						blitY = 0
					tempSurface.blit(scaledImage,(blitX,blitY))
					a = 255*p[2]/self.explosionLastTime
					tempSurface.set_alpha(a)

					surface.blit(tempSurface,(minX,minY))

		def getPoint(self,x,y,minRad=25,maxRad=100):
			self.explosionPoints.append([x,y,self.explosionLastTime - 1,minRad,maxRad])
