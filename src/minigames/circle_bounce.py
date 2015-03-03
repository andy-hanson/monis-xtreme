import math
import os
import pygame
import random

import helpers

class CircleBounce:
	def __init__(self,manager):
		self.manager = manager

		self.minBouncerSpeed = 3# + 1.5*self.manager.difficulty
		self.bouncerRad = 32
		numBouncers = 1#(self.manager.difficulty + 1)/2 #Integer division. num is 1, 2, then 3.
		self.bouncerAccel = 1 + self.manager.difficulty / 8.0
		self.bouncers = []
		for x in xrange(numBouncers):
			speed = self.minBouncerSpeed#self.minBouncerSpeed + (x/3.0)*(self.maxBouncerSpeed-self.minBouncerSpeed) #Slowly adds faster bouncers as difficulty goes up 1-6
			self.bouncers.append(self.Bouncer(self.manager,self,speed,self.bouncerRad,self.bouncerAccel))

		self.reflectorRadius = self.manager.SCREEN_WIDTH/2 * 2/3
		self.reflectorAngle = 0
		self.reflectorAngleSize = math.pi/4 + math.pi/6 #Looks to be pi/4, give them some extra room.
		self.reflectorWidth = 24 #Estimated from image
		self.reflectorSpeed = math.pi/144 * (1 + self.manager.difficulty/6.0) #Multiplyer for the mouse movement. It can go infinitely fast.
		self.bounceAngleVariance = math.pi/6 #The angle bounced to will be off by a random amount, with this as its maximum offness.

		self.BG = helpers.loadPNG(os.path.join('minigames','circleBounce','BG'),0)
		self.reflectorImage = helpers.loadPNG(os.path.join('minigames','circleBounce','reflector'),0)
		bouncerImageUnscaled = helpers.loadPNG(os.path.join('minigames','circleBounce','bouncer'),0)
		self.bouncerImage = pygame.transform.smoothscale(bouncerImageUnscaled, (self.bouncerRad*2,self.bouncerRad*2))

		self.timeTillWin = 512

		pygame.event.set_grab(1)

		self.bounceSound = helpers.loadOGG('circleBounce')
		self.bounceSound.set_volume(self.manager.main.normSoundVolume)

	def compute(self):
		#Left and right movement of the mouse causes the reflector to move counterclockwise and clockwise.
		self.reflectorAngle += self.reflectorSpeed*pygame.mouse.get_rel()[0]
		#pygame.mouse.set_pos((self.manager.SCREEN_WIDTH/2,self.manager.SCREEN_HEIGHT/2))
		#pygame.mouse.get_rel() #Cancel the set_pos. Otherwise, moving back to the center would count as movement.
		for bouncer in self.bouncers:
			bouncer.compute()
			'''if bouncer.passedReflector:
				self.manager.lose()'''

		self.timeTillWin -= 1
		if self.timeTillWin == 0:
			pygame.event.set_grab(0)
			self.manager.win()

	def draw(self,surface):
		surface.blit(self.BG,(0,0))

		for bouncer in self.bouncers:
			bouncer.draw(surface)

		rotated = pygame.transform.flip(pygame.transform.rotozoom(self.reflectorImage,self.reflectorAngle*180/math.pi,1), 1, 0)
		surface.blit(rotated, ((self.manager.SCREEN_WIDTH - rotated.get_width())/2, (self.manager.SCREEN_HEIGHT - rotated.get_height())/2))

		'''start = self.reflectorAngle - self.reflectorAngleSize/2
		end = self.reflectorAngle + self.reflectorAngleSize/2
		pygame.draw.arc(surface,(0,0,0),pygame.Rect(0,0,self.manager.SCREEN_WIDTH,self.manager.SCREEN_HEIGHT),start,end,3)'''



	class Bouncer:
		def __init__(self, manager, circleBounce, speed, rad, accel):
			self.manager = manager
			self.circleBounce = circleBounce
			self.x = self.manager.SCREEN_WIDTH/2
			self.y = self.manager.SCREEN_HEIGHT/2
			self.direction = random.random()*2*math.pi
			self.speed = speed
			self.rad = rad
			self.accel = accel

			self.passedReflector = 0
			self.maxReflectedWaitTime = 8 #You can't be reflected immediately after being reflected.
			self.reflectedWaitTime = 0

		def compute(self):
			self.x += self.speed * math.cos(self.direction)
			self.y += self.speed * math.sin(self.direction)

			if self.reflectedWaitTime:
				self.reflectedWaitTime -= 1
			else:
				#Check for collision with the reflector.
				if not self.passedReflector and \
				   math.sqrt((self.manager.SCREEN_WIDTH/2 - self.x)**2 + (self.manager.SCREEN_HEIGHT/2 - self.y)**2) \
						   + self.rad + self.circleBounce.reflectorWidth/2 >= self.circleBounce.reflectorRadius:
					myAngle = math.atan2(self.manager.SCREEN_HEIGHT/2 - self.y, self.manager.SCREEN_WIDTH/2 - self.x) #From the center. NOT DIRECTION!
					if myAngle < 0:
						myAngle += 2*math.pi
					reflectorMinAngle = self.circleBounce.reflectorAngle - self.circleBounce.reflectorAngleSize/2
					reflectorMaxAngle = self.circleBounce.reflectorAngle + self.circleBounce.reflectorAngleSize/2
					while reflectorMaxAngle < 0:
						reflectorMinAngle += 2*math.pi
						reflectorMaxAngle += 2*math.pi
					while reflectorMinAngle > 2*math.pi:
						reflectorMinAngle -= 2*math.pi
						reflectorMaxAngle -= 2*math.pi

					if reflectorMinAngle + 2*math.pi < myAngle < reflectorMaxAngle + 2*math.pi or \
					   reflectorMinAngle < myAngle < reflectorMaxAngle or \
					   reflectorMinAngle + 2*math.pi < myAngle < reflectorMaxAngle + 2*math.pi:
						#Bounce back, with a small random direction change.
						self.direction = myAngle + 2*math.pi + (random.random()*2-1)*self.circleBounce.bounceAngleVariance
						self.reflectedWaitTime = self.maxReflectedWaitTime
						self.speed += self.accel
						self.circleBounce.bounceSound.play()
					else:
						#You went passed the reflector.
						self.passedReflector = 1
			if self.x < 0 or self.x > self.manager.SCREEN_WIDTH or self.y < 0 or self.y > self.manager.SCREEN_HEIGHT:
				pygame.event.set_grab(0)
				self.manager.lose()

		def draw(self,surface):
			surface.blit(self.circleBounce.bouncerImage,(self.x-self.rad,self.y-self.rad))
