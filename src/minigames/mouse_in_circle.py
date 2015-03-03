import math
import os
import pygame
import random

import helpers
import graphics

class MouseInCircle:
	#The mouse is set to be inside a circle displayed on the screen. The circle moves between a set of points, and the player must keep the mouse in the circle.
	def __init__(self,manager):
		self.manager = manager
		self.indent = 50 #Points are inside of indent rect.
		self.numPoints = 3 + self.manager.difficulty
		self.speed = 2 + self.manager.difficulty/2
		self.curSpeed = 0 #Speeds up at the start and slows down at the end.
		self.accel = .025 #Also decel.
		self.deceling = 0
		self.points = []
		for k in xrange(self.numPoints):
			x = random.randint(self.indent,self.manager.SCREEN_WIDTH-self.indent)
			y = random.randint(self.indent,self.manager.SCREEN_HEIGHT-self.indent)
			self.points.append([x,y])
		#self.started = 0 #Player must put mouse inside of circle first.
		self.curPos = list(self.points[0]) #Where the circle is at the moment.
		self.mousePos = (0,0)
		self.dist = 0 #The distance from the mouse to where it should be
		pygame.mouse.set_pos(self.curPos)
		self.point = 0

		self.cursor = graphics.Cursor(self) #SimpleQ will act as Cursor's main.
		self.unscaledCircleImage = helpers.loadPNG(os.path.join('minigames','mouseInCircle','circle'), 0)
		self.bg = helpers.loadPNG(os.path.join('minigames','mouseInCircle','background'),0)

		self.music = helpers.loadOGG('mouseInCircle')
		self.music.play()

	def compute(self):
		fractionDone = float(self.point) / (len(self.points) - 1)
		self.circleRad = int(200 - 20 * self.manager.difficulty * fractionDone)

		self.mousePos = self.manager.mousePos
		self.cursor.compute()
		self.curSpeed += self.accel
		if self.curSpeed > self.speed:
			self.curSpeed = self.speed
		nextPoint = self.points[self.point+1]
		direction = math.atan2(nextPoint[1]-self.curPos[1],nextPoint[0]-self.curPos[0])
		self.curPos[0] += self.curSpeed * math.cos(direction)
		self.curPos[1] += self.curSpeed * math.sin(direction)
		newDirection = math.atan2(nextPoint[1]-self.curPos[1],nextPoint[0]-self.curPos[0])
		give = .001 #For round-off error.
		if not newDirection - give < direction < newDirection + give and not self.deceling:
			#You're on the other side of the point now.
			self.point += 1

		self.dist = math.sqrt((self.mousePos[0]-self.curPos[0])**2 + (self.mousePos[1]-self.curPos[1])**2)
		if self.dist >= self.circleRad:
			self.manager.lose()

		if self.deceling:
			self.speed -= self.accel
			if self.speed <= 0:
				self.manager.win()
		elif self.point == len(self.points) - 2:
			#You're heading to the last point. Slow down.
			self.deceling = 1

		self.music.set_volume(.125 + self.dist/self.circleRad*.875)

	def draw(self,surface):
		self.circleImage = pygame.transform.smoothscale(self.unscaledCircleImage, (self.circleRad*2+1,self.circleRad*2+1))

		b = self.dist / self.circleRad
		if b > 1:
			b = 1
		col = (b*255,b*128,b*128)
		bg = self.bg.copy()
		s = pygame.Surface(self.bg.get_size())
		s.fill(col)
		bg.blit(s,(0,0),None,pygame.BLEND_ADD)
		surface.blit(bg,(0,0))
		surface.blit(self.circleImage,(int(round(self.curPos[0]-self.circleRad)),int(round(self.curPos[1]-self.circleRad))))
		#pygame.draw.circle(surface,(0,0,0),(int(round(self.curPos[0])),int(round(self.curPos[1]))),self.circleRad,0)
		self.cursor.draw(surface)
