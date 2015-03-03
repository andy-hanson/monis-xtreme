import math
import os
import pygame
import random

import helpers

class MangoBounce:
	def __init__(self,manager):
		self.manager = manager

		self.bg = helpers.loadPNG(os.path.join('minigames','mango','flowerBG'),0)
		self.bouncer = self.Bouncer(self)
		self.mango = self.Mango(self)
		self.newHearts = []
		'''#The hearts form rings
		for i1 in xrange(3,4):
			rad = (i1-1)*120
			numSpots = i1**2
			for i2 in xrange(numSpots):
				ang = math.pi*2*i2/numSpots
				x = 400 + rad*math.cos(ang)
				y = 400 + rad*math.sin(ang)
				self.newHearts.append(self.NewHeart(self,x,y))'''

		numHearts = 1 + self.manager.difficulty/2
		tab = 100
		for i in xrange(numHearts):
			x = random.randint(tab,self.manager.SCREEN_WIDTH-tab)
			y = random.randint(tab,self.manager.SCREEN_HEIGHT-tab)
			self.newHearts.append(self.NewHeart(self,x,y))

		self.timeLeft = 900


		self.bounceSound = helpers.loadOGG('bumper')
		self.bounceSound.set_volume(self.manager.main.normSoundVolume)
		self.getFlowerSound = helpers.loadOGG('getFlower')
		self.getFlowerSound.set_volume(self.manager.main.normSoundVolume)

	def compute(self):
		self.bouncer.compute()
		self.mango.compute()
		for newHeart in self.newHearts:
			newHeart.compute()

		if len(self.newHearts) == 0:
			self.manager.win()
		self.timeLeft -= 1
		if self.timeLeft == 0:
			self.manager.lose()

	def draw(self,surface):
		surface.blit(self.bg,(0,0))
		for newHeart in self.newHearts:
			newHeart.draw(surface)
		self.mango.draw(surface)
		self.bouncer.draw(surface)

	class Bouncer:
		def __init__(self,mangoBounce):
			self.mangoBounce = mangoBounce
			self.manager = self.mangoBounce.manager
			self.length = 160 - 15*self.manager.difficulty
			self.centery = 600
			self.x1 = self.manager.SCREEN_WIDTH/2-self.length/2
			self.y1 = self.centery
			self.x2 = self.manager.SCREEN_WIDTH/2+self.length/2
			self.y2 = self.centery
			self.spinAngle = 0
			self.angle = 0
			self.bumpingPower = 8.0
			self.spinSpeed = math.pi / 240 * (1 + self.manager.difficulty / 3.0)

		def compute(self):
			#self.angle = math.atan2(self.y2-self.y1,self.x2-self.x1)
			self.centerx = self.manager.mousePos[0]
			self.centery = self.manager.mousePos[1]
			self.spinAngle += self.spinSpeed
			self.x1 = self.centerx - self.length/2*math.cos(self.spinAngle)
			self.y1 = self.centery - self.length/2*math.sin(self.spinAngle)
			self.x2 = self.centerx + self.length/2*math.cos(self.spinAngle)
			self.y2 = self.centery + self.length/2*math.sin(self.spinAngle)

			if self.x1 > self.x2:
				tX = self.x1
				tY = self.y1
				self.x1 = self.x2
				self.y1 = self.y2
				self.x2 = tX
				self.y2 = tY

			self.angle = math.atan2(self.y2-self.y1,self.x2-self.x1)

		def draw(self,surface):
			self.getImage()
			if self.angle > 0:
				blitX = self.x1 - self.width*math.sin(self.angle) - self.width*math.cos(self.angle)
				blitY = self.y1 - self.width*math.cos(self.angle) - self.width*math.sin(self.angle)
			else:
				blitX = self.x1 - self.width*math.sin(-self.angle) - self.width*math.cos(-self.angle)
				blitY = self.y1 - self.width*math.cos(-self.angle) - self.length*math.sin(-self.angle) - self.width*math.sin(-self.angle)
			surface.blit(self.image,(blitX,blitY))

		def getImage(self):
			mainImage = helpers.loadPNG(os.path.join('minigames','mango','bumper'),0)
			self.width = mainImage.get_height()/2.0
			mainImage = pygame.transform.scale(mainImage,(int(self.length),int(self.width*2))).convert_alpha()
			self.image = pygame.Surface((self.length + int(2*self.width),int(self.width*2))).convert_alpha()
			self.image.fill((0,0,0,0))
			capImage = helpers.loadPNG(os.path.join('minigames','mango','bumperCap'),0)
			self.image.blit(pygame.transform.flip(capImage,1,0).convert_alpha(),(0,0))
			self.image.blit(mainImage,(int(self.width),0))
			self.image.blit(capImage,(int(self.width)+self.length,0))
			self.image = pygame.transform.rotozoom(self.image,-self.angle*180/math.pi,1).convert_alpha()

	class Mango:
		def __init__(self,mangoBounce):
			self.mangoBounce = mangoBounce

			self.image = helpers.loadPNG(os.path.join('minigames','mango','player'),0)
			self.rad = self.image.get_width()/2

			self.x = self.mangoBounce.manager.SCREEN_WIDTH/2
			self.y = -self.rad
			self.circle = helpers.Circle(self.x,self.y,self.rad)
			self.grav = .20
			self.jump = 3.25
			self.down = math.pi/2
			self.up = -math.pi/2
			self.xVel = 0
			self.yVel = 0

		def compute(self):
			self.accel(self.down,self.grav)
			self.x += self.xVel
			self.y += self.yVel
			self.circle.update(self.x,self.y)

			if self.yVel > 0:
				self.collideLine(self.mangoBounce.bouncer)

			if self.x < 0 and self.xVel < 0:
				self.x = self.mangoBounce.manager.SCREEN_WIDTH
			if self.x > self.mangoBounce.manager.SCREEN_WIDTH and self.xVel > 0:
				self.x = 0

			if self.y > self.mangoBounce.manager.SCREEN_HEIGHT:
				self.mangoBounce.manager.lose()

		def draw(self,surface):
			surface.blit(self.image,(self.x-self.image.get_width()/2,self.y-self.image.get_height()/2))

		def collideLine(self,line):
			#We will determine the distance from the circle to the line.
			#If that distance if less than or equal to the circle's radius, then the circle is touching the line.
			#Now we will determine an mx+b equation for both the line and
			#A line perpendicular to this line which passes through player's center.
			if line.x1 == line.x2:
				#special case; use different method
				dist = abs(self.x - line.x1)
				touchesSegment = min(line.y1,line.y2) < self.y < max(line.y1,line.y2)
				if dist <= self.rad and touchesSegment:
					above = self.x > line.x1
					self.reactToLine(line,dist,above)
					return 1
				return 0

			else:
				m1 = math.tan(line.angle)
				b1 = line.y1 - m1*line.x1
				m2 = math.tan(line.angle+math.pi/2)
				#y = mx + b, know m,x,y
				b2 = self.y - m2*self.x
				#Intersection of 2 lines:
				#y = m1*x + b
				#y = m2*x + b2
				intersectX = (b2 - b1)/(m1 - m2)
				intersectY = m1*intersectX + b1#(b1*m2 + b2*m1)/(m1 - m2)
				dist = math.sqrt((intersectX-self.x)**2 + (intersectY-self.y)**2) #CHECK!
				#But we're only going to collide with it if we touch the line segment.
				lesserX = min(line.x1,line.x2)
				greaterX = max(line.x1,line.x2)
				lesserY = min(line.y1,line.y2)
				greaterY = max(line.y1,line.y2)
				touchesSegment = lesserX <= intersectX <= greaterX and lesserY <= intersectY <= greaterY

				if dist <= self.rad*2 and touchesSegment:
					above = self.y < intersectY #Greater y value means go down
					self.reactToLine(line,dist,above)
					return 1
				return 0

		def reactToLine(self,line,dist,above):
			magnitude = math.sqrt(self.xVel**2+self.yVel**2)
			direction = math.atan2(self.yVel,self.xVel)

			down = magnitude*math.cos(self.down - direction) #My current movement in the self.down direction
			self.accel(self.up,self.jump+down)

			magnitude = math.sqrt(self.xVel**2+self.yVel**2)
			direction = math.atan2(self.yVel,self.xVel)

			if above:
				perp = magnitude*math.sin(-line.angle + direction) #My movement perpendicular to the line.
			else:
				perp = magnitude*math.sin(math.pi - line.angle + direction)
			bump = line.bumpingPower + perp
			if above:
				self.accel(line.angle - math.pi/2,bump)
			else:
				self.accel(line.angle + math.pi/2,bump)
			#So, line.bumpingPower should ALWAYS be greater than self.jump so that you don't jump through lines perpendicular to your up.
			self.line = None
			self.onGround = 0

			self.mangoBounce.bounceSound.play()

		def accel(self, direction, amount):
			self.xVel += amount * math.cos(direction)
			self.yVel += amount * math.sin(direction)

	class NewHeart:
		'''Raises Mango's maximum health by 1 and completely fills his health.'''
		#Actually it only does that in the actual game
		def __init__(self,mangoBounce,x,y):
			self.mangoBounce = mangoBounce
			self.image = helpers.loadPNG(os.path.join('minigames','mango','darkFlower'),0)#self.image = helpers.loadPNG(os.path.join('minigames','mango','heartFull'),0)
			size = 96 - 4 * self.mangoBounce.manager.difficulty
			self.image = pygame.transform.smoothscale(self.image,(size,size))
			self.circle = helpers.Circle(x,y,self.image.get_width()/2,self.image)

		def compute(self):
			if self.mangoBounce.mango.circle.collideCircle(self.circle):
				self.mangoBounce.newHearts.remove(self)
				self.mangoBounce.getFlowerSound.play()

		def draw(self,surface):
			self.circle.draw(surface)
