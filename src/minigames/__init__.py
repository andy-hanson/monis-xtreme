import math
import pygame
import os
import random

import helpers
import graphics




class CircleBounce:
	def __init__(self,manager):
		self.manager = manager

		self.minBouncerSpeed = 4 + 1.5*self.manager.difficulty
		self.bouncerRad = 16
		numBouncers = 1#(self.manager.difficulty + 1)/2 #Integer division. num is 1, 2, then 3.
		self.bouncerAccel = 1
		self.bouncers = []
		for x in xrange(numBouncers):
			speed = self.minBouncerSpeed#self.minBouncerSpeed + (x/3.0)*(self.maxBouncerSpeed-self.minBouncerSpeed) #Slowly adds faster bouncers as difficulty goes up 1-6
			self.bouncers.append(self.Bouncer(self.manager,self,speed,self.bouncerRad,self.bouncerAccel))

		self.reflectorRadius = self.manager.SCREEN_WIDTH/2 * 2/3
		self.reflectorAngle = 0
		self.reflectorAngleSize = math.pi/4 + math.pi/12 #Looks to be pi/4, give them some extra room.
		self.reflectorWidth = 24 #Estimated from image
		self.reflectorSpeed = math.pi/144 * (1 + self.manager.difficulty/6.0) #Multiplyer for the mouse movement. It can go infinitely fast.
		self.bounceAngleVariance = math.pi/6 #The angle bounced to will be off by a random amount, with this as its maximum offness.

		self.BG = helpers.loadPNG(os.path.join('minigames','circleBounce','BG'),0)
		self.reflectorImage = helpers.loadPNG(os.path.join('minigames','circleBounce','reflector'),0)
		self.bouncerImage = pygame.transform.smoothscale(helpers.loadPNG(os.path.join('minigames','circleBounce','bouncer'),0),(self.bouncerRad*2,self.bouncerRad*2))

		self.timeTillWin = 256

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
			#pygame.draw.circle(surface,(0,0,0),(self.x,self.y),2)
			surface.blit(self.circleBounce.bouncerImage,(self.x-self.rad,self.y-self.rad))



class TimedShoot:
	def __init__(self,manager):
		self.manager = manager

		self.shotSpeed = 10
		self.shotSize = 10
		self.targetSize = int(round(64 - self.manager.difficulty*32/6.0))

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
			speed = 3*self.manager.difficulty - 2.5*self.manager.difficulty*random.random()*i/numTargets
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

		self.timeLeft = 840


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
			self.length = 160 - 20*self.manager.difficulty
			self.centery = 600
			self.x1 = self.manager.SCREEN_WIDTH/2-self.length/2
			self.y1 = self.centery
			self.x2 = self.manager.SCREEN_WIDTH/2+self.length/2
			self.y2 = self.centery
			self.spinAngle = 0
			self.angle = 0
			self.bumpingPower = 8.0
			self.spinSpeed = math.pi/240

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
			size = 96 - 8*self.mangoBounce.manager.difficulty
			self.image = pygame.transform.smoothscale(self.image,(size,size))
			self.circle = helpers.Circle(x,y,self.image.get_width()/2,self.image)

		def compute(self):
			if self.mangoBounce.mango.circle.collideCircle(self.circle):
				self.mangoBounce.newHearts.remove(self)
				self.mangoBounce.getFlowerSound.play()

		def draw(self,surface):
			self.circle.draw(surface)
