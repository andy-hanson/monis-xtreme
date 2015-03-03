import math
import pygame
import random

import helpers

class SillinessManager:
	def __init__(self,main):
		self.main = main
		self.SCREEN_WIDTH = self.main.SCREEN_WIDTH
		self.SCREEN_HEIGHT = self.main.SCREEN_HEIGHT
		self.sillies = []

		self.newSillyChance = 0

	def compute(self):
		i = 0
		while i < len(self.sillies):
			self.sillies[i].compute()
			try:
				if self.sillies[i].dead:
					del self.sillies[i]
			except AttributeError:
				pass #Has no attribute dead yet
			i += 1

		if random.random() < self.newSillyChance:
			self.getNewSilly()

	def draw(self,surface):
		for s in self.sillies:
			s.draw(surface)

	def getNewSilly(self):
		r = random.randint(0,7)

		#Make the screamers and musicVolumes infrequent
		if r == 0 or r == 4:
			r = random.randint(0,7)

		if r == 0:
			s = Screamer(self)
		elif r == 1:
			s = Juggled(self)
		elif r == 2:
			s = Bird(self)
		elif r == 3:
			s = Ball(self)
		elif r == 4:
			s = MusicVolume(self)
		elif r == 5:
			s = FlyAcrossScreen(self)
		elif r == 6:
			s = Food(self)
		elif r == 7:
			s = Spider(self)

		self.sillies.append(s)

class Screamer:
	def __init__(self,manager):
		self.manager = manager
		self.image = helpers.loadPNG('scream')
		self.manager.main.movementSwitcher.stopMusic()
		r = random.randint(0,1)
		self.sound = helpers.loadOGG('scream' + str(r))
		#Acts instantly
		self.manager.main.screen.blit(self.image,(0,0))
		self.sound.play()
		pygame.display.flip()
		pygame.time.wait(32*1000/40)
		self.dead = 1

	def compute(self):
		pass

	def draw(self,surface):
		pass


class Juggled:
	#Both shovels and Wobbuffets
	def __init__(self,manager):
		self.manager = manager
		k = 4 #Scale of conversion from Mango Saves the World's 240-high screen
		if random.random() < .5:
			self.image = helpers.hardScale(helpers.loadPNGNoAlpha('juggled'),k)
			#self.image = pygame.transform.scale(self.image, (k*self.image.get_width(),k*self.image.get_height()))
			self.image.set_colorkey((0,0,0))
			self.goingDownImage = pygame.transform.flip(self.image.copy(),0,1)
			self.goingDownImage.set_alpha(None)
			self.goingDownImage.set_colorkey((0,0,0))
			self.ySpeed = -4*k
		else:
			self.image = helpers.loadPNG('wobbuffet')
			self.image = pygame.transform.smoothscale(self.image, (int(round(.25*self.image.get_width())),int(round(.25*self.image.get_height()))))
			self.goingDownImage = pygame.transform.flip(self.image,0,1)
			self.ySpeed = -18
		self.rect = self.image.get_rect()
		self.rect.centerx = random.randint(0,self.manager.SCREEN_WIDTH)
		self.realY = self.manager.SCREEN_HEIGHT
		self.rect.y = self.realY

		self.grav = .035*k

	def compute(self):
		self.realY += self.ySpeed
		self.ySpeed += self.grav
		if self.ySpeed > 0:
			self.image = self.goingDownImage
		self.rect.y = self.realY

		if self.rect.y > self.manager.SCREEN_HEIGHT:
			self.dead = 1

	def draw(self,surface):
		surface.blit(self.image,(self.rect.x,self.rect.y))

class Bird:
	def __init__(self,manager):
		self.manager = manager

		self.image = helpers.loadPNGNoAlpha('bird')
		self.image.set_colorkey((255,0,255))
		self.image.set_alpha(0)
		self.rect = self.image.get_rect()
		self.rect.center = (self.manager.SCREEN_WIDTH/2, self.manager.SCREEN_HEIGHT/2)
		self.xVel = random.randint(3,6)
		if random.random() < .5:
			self.xVel *= -1
		self.yVel = random.randint(3,6)
		if random.random() < .5:
			self.yVel *= -1

		self.lastTime = 512
		self.time = 0

	def compute(self):
		self.rect.x += self.xVel
		self.rect.y += self.yVel
		if self.rect.left < 0:
			self.xVel = abs(self.xVel)
		if self.rect.right > self.manager.SCREEN_WIDTH:
			self.xVel = -abs(self.xVel)
		elif self.rect.top < 0:
			self.yVel = abs(self.yVel)
		if self.rect.bottom > self.manager.SCREEN_HEIGHT:
			self.yVel = -abs(self.yVel)

		self.time += 1
		self.image.set_alpha(255 * math.sin(math.pi*self.time/self.lastTime)**(1.0/2))
		if self.time == self.lastTime:
			self.dead = 1

	def draw(self,surface):
		surface.blit(self.image,self.rect.topleft)


class Ball:
	def __init__(self,manager):
		self.manager = manager
		self.image = helpers.loadPNGNoAlpha('ball')
		self.image.set_colorkey((255,255,255))
		self.rect = self.image.get_rect()
		self.rect.center = (random.randint(-self.image.get_width(),self.manager.SCREEN_WIDTH), random.randint(-self.image.get_height(),self.manager.SCREEN_HEIGHT))

	def compute(self):
		if self.rect.collidepoint(self.manager.main.mousePos):
			self.dead = 1
			self.deathSound = helpers.loadOGG('ballShot')
			self.deathSound.set_volume(self.manager.main.normSoundVolume)
			self.deathSound.play()

	def draw(self,surface):
		surface.blit(self.image,self.rect.topleft)

class MusicVolume:
	def __init__(self,manager):
		self.manager = manager
		self.lastTime = 128
		self.time = 0

	def compute(self):
		self.time += 1
		sin = math.sin(2*math.pi*self.time/self.lastTime)
		if sin > 0:
			vol = self.manager.main.normMusicVolume + (1 - self.manager.main.normMusicVolume)*sin #Range norm to 1
		else:
			vol = self.manager.main.normMusicVolume + self.manager.main.normMusicVolume*sin #Range norm to 0
		self.manager.main.movementSwitcher.setMusicVolume(vol)

		if self.time == self.lastTime:
			self.dead = 1

	def draw(self,surface):
		pass

class FlyAcrossScreen:
	def __init__(self,manager):
		'''Chooses between a variety of objects to move across the screen linearly at a constant speed.'''
		self.manager = manager
		self.choice = random.randint(0,3)

		#(self.x,self.y) is the image center

		if self.choice == 0:
			r = random.randint(0,1) #There are 2 cloud images
			self.image = helpers.loadPNG('cloud' + str(r))
			self.rect = self.image.get_rect(center = (self.manager.SCREEN_WIDTH + self.image.get_width()/2, \
													  random.random()*(self.manager.SCREEN_HEIGHT + self.image.get_height()) - self.image.get_height()/2))
			self.xVel = -7 - random.random()*22
			self.yVel = 0

		elif self.choice == 1:
			self.image = helpers.loadPNG('x')
			ang = random.random()*2*math.pi
			rad = self.manager.SCREEN_WIDTH
			self.rect = self.image.get_rect(center = (self.manager.SCREEN_WIDTH/2 + rad*math.cos(ang), self.manager.SCREEN_HEIGHT/2 + rad*math.sin(ang)))
			speed = 15
			self.xVel = -speed*math.cos(ang) #Going back towards the center
			self.yVel = -speed*math.sin(ang)

		elif self.choice == 2:
			ang = random.random()*2*math.pi
			rad = self.manager.SCREEN_WIDTH
			speed = 15
			self.xVel = -speed*math.cos(ang) #Going back towards the center
			self.yVel = -speed*math.sin(ang)
			if self.xVel > 0:
				self.image1 = helpers.hardScale(helpers.loadPNG('bulletR1'),4)
				self.image2 = helpers.hardScale(helpers.loadPNG('bulletR2'),4)
			else:
				self.image1 = helpers.hardScale(helpers.loadPNG('bulletL1'),4)
				self.image2 = helpers.hardScale(helpers.loadPNG('bulletL2'),4)
			self.image = self.image1
			self.rect = self.image.get_rect(center = (self.manager.SCREEN_WIDTH/2 + rad*math.cos(ang), self.manager.SCREEN_HEIGHT/2 + rad*math.sin(ang)))

		elif self.choice == 3:
			self.image = helpers.hardScale(helpers.loadPNG('finalBoss'),4)
			ang = random.random()*2*math.pi
			rad = self.manager.SCREEN_WIDTH
			self.rect = self.image.get_rect(center = (self.manager.SCREEN_WIDTH/2 + rad*math.cos(ang), self.manager.SCREEN_HEIGHT/2 + rad*math.sin(ang)))
			speed = 4
			self.xVel = -speed*math.cos(ang) #Going back towards the center
			self.yVel = -speed*math.sin(ang)


	def compute(self):
		self.rect.x += self.xVel
		self.rect.y += self.yVel

		if (self.rect.right < 0 and self.xVel < 0) or (self.rect.bottom < 0 and self.yVel < 0) or \
			(self.rect.left > self.manager.SCREEN_WIDTH and self.xVel > 0) or (self.rect.top > self.manager.SCREEN_HEIGHT and self.yVel > 0):
			self.dead = 1

	def draw(self,surface):
		if self.choice == 2:
			if self.image is self.image1:
				self.image = self.image2
			else:
				self.image = self.image1

		surface.blit(self.image,self.rect.topleft)


class Converter:
	'''Helps with circles. Coordinates are in relation to the center.'''
	#Xs and Ys are from origin in center
	def __init__(self,WH):
		self.WH = WH
	def convert(self,x,y):
		if x**2+y**2>=(self.WH/2)**2:
			#It's off the edge and must warp!
			theta = math.atan2(y,-x) #Why negative X? I have no clue!
			newTheta = -theta #Since it's on the other side of the circle
			#If the old radius goes X past the boundary, the new radius will be X short of the boundary.
			oldRad = math.sqrt(x**2+y**2)
			if oldRad > self.WH/2:
				newRad = self.WH/2 - (oldRad-self.WH/2)
			else:
				newRad = self.WH/2
			return (newRad*math.cos(newTheta),newRad*math.sin(newTheta))
		return (x,y)
	def convertBack(self,x,y):
		'''Converts from the converter's origin to an upper-left origin. For drawing.'''
		return (int(x + self.WH/2),int(y + self.WH/2))
	def randomPoint(self):
		return helpers.randomCirclePoint(self.WH/2)
	def drawCircle(self,surface,color,x,y,rad,width):
		x,y = self.convert(x,y) #Takes warping into account
		x,y = self.convertBack(x,y) #Moves origin to upper-left, instead of center.
		pygame.draw.circle(surface,color,(x,y),int(rad),int(width))
	def circleCollide(self,x1,y1,r1,x2,y2,r2):
		'''Collision detection between 2 circles. Returns a boolean.'''
		return (x1 - x2)**2 + (y1 - y2)**2 <= (r1 + r2)**2

class Food:
	def __init__(self,manager):
		'''Rules is an integer value telling the food what to do.'''
		self.drawPriority = 1
		#evil is a boolean telling whether this food is evil.
		self.manager = manager
		self.converter = Converter(self.manager.SCREEN_WIDTH)
		self.evil = 0
		self.x = self.manager.SCREEN_WIDTH/2
		self.y = self.manager.SCREEN_HEIGHT/2
		self.rules = random.randint(1,5)
		self.radius = self.converter.WH*6/700
		self.speed = random.random()*self.converter.WH/140+self.converter.WH/70
		if self.evil:
			#Follows player
			self.speed = (random.random()+.1)*self.player.speed/1.2
		elif self.rules == 1:
			#Goes straight
			self.direction = random.random()*360
		elif self.rules == 2:
			#Curves
			self.direction = random.random()*360
			self.spinVel = random.random()/15-1.0/30
		elif self.rules == 3:
			#Spirals
			self.direction = random.random()*360
			self.spinVel = 0
			self.spinAccell = random.random()/25-random.random()/50
		elif self.rules == 4:
			#Zigzags
			self.direction = random.random()*360
			self.frequency = random.randint(40,60)
			self.time = 0
			temp = random.randint(0,1)
			self.turn = random.random()*math.pi*2
		elif self.rules == 5:
			#Teleports. Each new teleportation is a straight-line movement of the last one
			self.waitTime = 25 #The time to wait between jumps
			self.timeWaited = 0 #The time so far since the last jump
			self.jumpLength = random.random()*self.converter.WH/9+self.converter.WH/9
			self.direction = random.random()*math.pi*2
			self.nextPoint =  (self.x+self.jumpLength*math.cos(self.direction),\
							   self.y+self.jumpLength*math.cos(self.direction))
			self.nextPoint = self.converter.convert(self.nextPoint[0],self.nextPoint[1])


		#New stuff
		self.highlightImage = helpers.loadPNG('circleHighlight')
		self.surviveTime = 96
		self.mouseRad = 12 #The radius for the circle used in collision between the mouse and food.

	def compute(self):
		if self.evil:
			direction = math.atan2(self.player.y-self.y,self.player.x-self.x)
			self.x += self.speed*math.cos(direction)
			self.y += self.speed*math.sin(direction)
			self.x,self.y = self.converter.convert(self.x,self.y)
		elif self.rules == 1:
			self.x += self.speed*math.cos(self.direction)
			self.y += self.speed*math.sin(self.direction)
			self.x,self.y = self.converter.convert(self.x,self.y)
		elif self.rules == 2:
			self.direction += self.spinVel
			self.x += self.speed*math.cos(self.direction)
			self.y += self.speed*math.sin(self.direction)
			self.x,self.y = self.converter.convert(self.x,self.y)
		elif self.rules == 3:
			self.spinVel += self.spinAccell
			self.direction += self.spinVel
			if self.spinVel >= .2 or self.spinVel <= -.2:
				self.spinAccell *= -1
			self.x += self.speed*math.cos(self.direction)
			self.y += self.speed*math.sin(self.direction)
			self.x,self.y = self.converter.convert(self.x,self.y)
		elif self.rules == 4:
			self.time += 1
			if self.time == self.frequency:
				self.time = 0
				self.direction += self.turn
			self.x += self.speed*math.cos(self.direction)
			self.y += self.speed*math.sin(self.direction)
			self.x,self.y = self.converter.convert(self.x,self.y)
		elif self.rules == 5:
			self.timeWaited += 1
			if self.timeWaited >= self.waitTime:
				self.timeWaited = 0
				self.x, self.y = self.nextPoint
				self.nextPoint =  (self.x+self.jumpLength*math.cos(self.direction),\
								   self.y+self.jumpLength*math.cos(self.direction))
				self.nextPoint = self.converter.convert(self.nextPoint[0],self.nextPoint[1])


		#New stuff
		#Must convert mouse position so that (0,0) is the center of the screen.
		if self.converter.circleCollide(self.x,self.y,self.radius, \
							self.manager.main.mousePos[0]-self.manager.SCREEN_WIDTH/2,self.manager.main.mousePos[1]-self.manager.SCREEN_HEIGHT/2,self.mouseRad):
			self.dead = 1
			sound = helpers.loadOGG('getFood')
			sound.set_volume(self.manager.main.normSoundVolume)
			sound.play()
			self.manager.main.itemManager.getBonus(1)

		self.surviveTime -= 1
		if self.surviveTime == 0:
			self.dead = 1



	def draw(self,surface):
		#Make sure only one highlight image is drawn.
		for o in self.manager.sillies:
			if isinstance(o,Food):
				if o is self:
					surface.blit(self.highlightImage,(0,0))
				else:
					break

		if self.rules == 5 and not self.evil:
			#Special drawing: both where it is and where it's about to be
			color = (255,255,0)
			width = int(self.radius/2)
			self.converter.drawCircle(surface,color,self.x,self.y,self.radius,width)

		else:
			if self.evil:
				color = (0,0,0)
			elif self.rules == 1:
				color = (255,0,0)
			elif self.rules == 2:
				color = (0,0,255)
			elif self.rules == 3:
				color = (0,255,0)
			elif self.rules == 4:
				color = (255,0,255)
			width = int(self.radius/2)
			self.converter.drawCircle(surface,color,self.x,self.y,self.radius,width)

class Spider:
	def __init__(self,manager):
		self.manager = manager
		self.speed = random.randint(1,4)
		self.image = helpers.loadPNGNoAlpha('spider')
		self.image.set_colorkey((255,255,255))
		self.image.set_alpha(0)
		self.rect = self.image.get_rect(center=(self.manager.SCREEN_WIDTH/2,self.image.get_height()/2))
		self.xVel = self.speed
		if random.random() < .5:
			self.xVel *= -1
		self.yVel = 0

		self.lastTime = 1024
		self.time = 0

	def compute(self):
		self.rect.x += self.xVel
		self.rect.y += self.yVel

		if self.rect.x < 0:
			self.rect.x = 0
			if self.rect.top == 0:
				self.yVel = self.speed
			else:
				self.yVel = -self.speed
			self.xVel = 0

		if self.rect.right >= self.manager.SCREEN_WIDTH:
			self.rect.right = self.manager.SCREEN_WIDTH - 1
			if self.rect.top == 0:
				self.yVel = self.speed
			else:
				self.yVel = -self.speed
			self.xVel = 0

		if self.rect.y < 0:
			self.rect.y = 0
			if self.rect.left == 0:
				self.xVel = self.speed
			else:
				self.xVel = -self.speed
			self.yVel = 0

		if self.rect.bottom >= self.manager.SCREEN_HEIGHT:
			if self.rect.left == 0:
				self.xVel = self.speed
			else:
				self.xVel = -self.speed
			self.rect.bottom = self.manager.SCREEN_HEIGHT - 1
			self.yVel = 0

		if self.rect.collidepoint(self.manager.main.mousePos):
			self.xVel *= -1
			self.yVel *= -1

		self.time += 1
		self.image.set_alpha(255 * math.sin(math.pi*self.time/self.lastTime)**(1.0/2))
		if self.time == self.lastTime:
			self.dead = 1

	def draw(self,surface):
		surface.blit(self.image,self.rect.topleft)
