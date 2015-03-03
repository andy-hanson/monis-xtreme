import pygame
import random

import helpers


class ItemManager:
	'''Manages the item bar and item selection. Once activated, items become their own objecsts.'''
	def __init__(self,main,blockManager):
		self.main = main
		self.blockManager = blockManager
		#The item bar charges up
		self.charge = 0.0
		self.maxCharge = 12
		self.bonusChargePlus = 2 #From minigames

		#middle is 620
		#Size of the item charger bar
		self.chargerBorder = 4
		self.minX = 460
		self.maxX = 780
		self.minY = 20
		self.maxY = 100
		self.chargeImages = []
		xSize = self.maxX-self.minX + self.chargerBorder
		ySize = self.maxY-self.minY + self.chargerBorder
		self.chargeImages.append(pygame.transform.smoothscale(helpers.loadPNG('itemChargeBlack'),(xSize,ySize)))
		self.chargeImages.append(pygame.transform.smoothscale(helpers.loadPNG('itemChargeRed'),(xSize,ySize)))
		self.chargeImages.append(pygame.transform.smoothscale(helpers.loadPNG('itemChargeGreen'),(xSize,ySize)))
		self.chargeImages.append(pygame.transform.smoothscale(helpers.loadPNG('itemChargeWhite'),(xSize,ySize)))
		self.chargeBG = pygame.transform.smoothscale(helpers.loadPNG('itemChargeBackground'),(xSize,ySize))
		#1280 by 320 v. 1360 by 400
		self.chargeBorderIndent = 40 * (self.maxX - self.minX)/1280
		self.chargeBorder = pygame.transform.smoothscale(helpers.loadPNG('itemChargeBorder'), \
							(self.maxX-self.minX + self.chargeBorderIndent*2,self.maxY-self.minY + self.chargeBorderIndent*2))

		self.buttonSize = 120
		self.buttonLeftX = 440
		self.buttonTopY = 120
		#6 buttons for 3 bombs, twist, score bonus, pause
		self.bigBombImage = pygame.transform.smoothscale(helpers.loadPNG('bigBombButton'),(self.buttonSize,self.buttonSize))
		self.vertiBombImage = pygame.transform.smoothscale(helpers.loadPNG('vertiBombButton'),(self.buttonSize,self.buttonSize))
		self.horizBombImage = pygame.transform.smoothscale(helpers.loadPNG('horizBombButton'),(self.buttonSize,self.buttonSize))
		self.scoreBonusImage = pygame.transform.smoothscale(helpers.loadPNG('scoreBonusButton'),(self.buttonSize,self.buttonSize))
		self.starImage = pygame.transform.smoothscale(helpers.loadPNG('starButton'),(self.buttonSize,self.buttonSize))
		self.pauseImage = pygame.transform.smoothscale(helpers.loadPNG('pauseButton'),(self.buttonSize,self.buttonSize))

	def compute(self):
		if (self.main.mouseLeftDown or self.main.mouseRightDown) and not self.main.hasItem:
			mX = self.main.mousePos[0]
			mY = self.main.mousePos[1]
			buttonX = (mX - self.buttonLeftX)/self.buttonSize
			buttonY = (mY - self.buttonTopY)/self.buttonSize
			self.tryToUse(buttonX,buttonY)

	def draw(self,surface):
		surface.blit(self.chargeBG,(self.minX-self.chargerBorder/2,self.minY-self.chargerBorder/2))
		if self.charge != 0:
			if self.charge < self.maxCharge/4:
				i = 0#color = (0,0,0)
			elif self.charge < self.maxCharge/2:
				i = 1#color = (255,0,0)
			elif self.charge < self.maxCharge:
				i = 2#color = (0,255,0)
			else:
				i = 3#color = (255,255,255)


			if self.charge < self.maxCharge:
				newSize = self.chargerBorder/2 + (self.maxX - self.minX)*self.charge/self.maxCharge
				img = self.chargeImages[i].subsurface(pygame.Rect(0,0,newSize,self.chargeImages[i].get_height()))
				surface.blit(img,(self.minX-self.chargerBorder/2,self.minY-self.chargerBorder/2))
			else:
				surface.blit(self.chargeImages[i],(self.minX-self.chargerBorder/2,self.minY-self.chargerBorder/2))

		surface.blit(self.chargeBorder,(self.minX - self.chargeBorderIndent, self.minY - self.chargeBorderIndent))

		#thisX2 = self.minX + (self.maxX - self.minX)*self.charge/self.maxCharge
		#pygame.draw.rect(surface,color,pygame.Rect(self.minX,self.minY,thisX2-self.minX,self.maxY-self.minY))

		#BUTTONS
		surface.blit(self.bigBombImage,(self.buttonLeftX + 0*self.buttonSize,self.buttonTopY + 0*self.buttonSize))
		surface.blit(self.vertiBombImage,(self.buttonLeftX + 1*self.buttonSize,self.buttonTopY + 0*self.buttonSize))
		surface.blit(self.horizBombImage,(self.buttonLeftX + 2*self.buttonSize,self.buttonTopY + 0*self.buttonSize))
		surface.blit(self.scoreBonusImage,(self.buttonLeftX + 0*self.buttonSize,self.buttonTopY + 1*self.buttonSize))
		surface.blit(self.starImage,(self.buttonLeftX + 1*self.buttonSize,self.buttonTopY + 1*self.buttonSize))
		surface.blit(self.pauseImage,(self.buttonLeftX + 2*self.buttonSize,self.buttonTopY + 1*self.buttonSize))

	def getBonus(self,amount):
		'''From minigames. Amount is -1 or 1.'''
		self.charge += amount*self.bonusChargePlus
		if self.charge < 0:
			self.charge = 0
		if self.charge >= self.maxCharge:
			self.charge = self.maxCharge

	def getScore(self):
		if self.charge < self.maxCharge:
			self.charge += 1

	def tryToUse(self,buttonX,buttonY):
		if 0 <= buttonX <= 2 and 0 <= buttonY <= 1:
			#It's an actual button! Otherwise, you didn't click on a button.
			if buttonY == 0:
				if buttonX == 0:
					cost = self.maxCharge #BigBomb
				elif buttonX == 1:
					cost = self.maxCharge/2 #VertiBomb
				else:
					cost = self.maxCharge*3/8 #HorizBomb
			if buttonY == 1:
				if buttonX == 0:
					cost = self.maxCharge/2 #Score bonus
				elif buttonX == 1:
					cost = self.maxCharge
				else:
					cost = 0

			if self.charge >= cost:
				if buttonY == 0:
					if buttonX == 0:
						self.main.getItem(BigBomb(self.main,self.blockManager))
					elif buttonX == 1:
						self.main.getItem(VertiBomb(self.main,self.blockManager))
					else:
						self.main.getItem(HorizBomb(self.main,self.blockManager))
				else:
					if buttonX == 0:
						self.main.getItem(ScoreBonus(self.main,self.blockManager))
					elif buttonX == 1:
						#First check that there are no stars already in use.
						#You can use a star and a bomb, but not two stars.
						hasStar = 0
						for o in self.main.objects:
							if isinstance(o,Star):
								hasStar = 1
						if hasStar:
							self.charge += cost #Counteract losing the cost. In total, nothing happens.
						else:
							self.main.getItem(Star(self.main,self.blockManager))
					else:
						self.main.getItem(Pause(self.main))
				self.charge -= cost

			#Now turn off the mouse to avoid using the item on its very first frame!
			self.main.mouseLeftDown = 0
			self.main.mouseRightDown = 0

class BigBomb:
	def __init__(self,main,blockManager):
		self.main = main
		self.main.cursor.bombOn = 1
		self.main.hasItem = 1
		self.blockManager = blockManager

		self.images = []
		for x in xrange(-3,4):
			img = helpers.loadPNG('kBigBomb' + str(x))
			#We want the maximum size to be blockSize*5, there are 7 frames, linear growth.
			size = self.blockManager.blockSize*5 * (x+4)/7
			img = pygame.transform.smoothscale(img,(size,size))
			self.images.append(img)
		self.screenImages = []

		for x in xrange(0,8):
			self.screenImages.append(helpers.loadPNG('bigBombScreen' + str(x)))

		self.screenFrames = 512 #The length of the explosion images.

		self.xPos = 0
		self.yPos = 0
		self.exploding = 0
		self.explodeFrameTime = 4
		self.maxTimeTillNewScreenFrame = 12
		self.timeTillNewScreenFrame = 12
		self.screenFrame = 0

	def compute(self):
		if self.exploding:
			self.explodeFrame += 1
			if self.explodeFrame == 7 + self.screenFrames:
				self.finish()
			if self.explodeFrame >= 7:
				#The whole-screen flashes have begun.
				if self.explodeFrame == 7 + self.maxTimeTillNewScreenFrame:
					self.explodeSound = helpers.loadOGG('bigBomb')
					self.explodeSound.set_volume(self.main.normSoundVolume)
					self.explodeSound.play()
				self.timeTillNewScreenFrame -= 1
				if self.timeTillNewScreenFrame == 0:

					#Make sure the next frame is a new one.
					oldScreenFrame = self.screenFrame
					self.screenFrame = random.randint(0,5)
					while self.screenFrame == oldScreenFrame:
						self.screenFrame = random.randint(0,5)

					self.timeTillNewScreenFrame = self.maxTimeTillNewScreenFrame
		else:
			self.xPos, self.yPos = self.main.mousePos #You can't move the bomb once it's already exploded!
			if self.main.mouseLeftDown or self.main.mouseRightDown:
				self.explode()

	def draw(self,surface):
		if self.exploding:
			frame = self.explodeFrame
			if frame >= 7*self.explodeFrameTime:
				surface.blit(self.screenImages[self.screenFrame],(0,0))
			else:
				frame /= self.explodeFrameTime #Integer division
				surface.blit(self.images[frame],(self.xPos - self.images[frame].get_width()/2,self.yPos - self.images[frame].get_height()/2))

	def explode(self):
		fadeOutTime = self.explodeFrameTime*7*1000/40
		self.gridPos = self.blockManager.mousePosToGridPos(self.main.mousePos)
		if self.gridPos != 'badPos':
			self.main.cursor.on = 0
			self.main.cursor.bombOn = 0
			self.blockManager.running = 0
			self.main.scorer.comboTimeCounting = 0
			if self.main.training:
				self.main.fadeOutMusic(fadeOutTime)
			else:
				self.main.fxManager.running = 0
				self.main.movementSwitcher.fadeOutMusic(fadeOutTime)
			self.exploding = 1
			self.explodeFrame = 0

	def finish(self):
		#After the explosion animation:
		self.dead = 1
		self.main.itemOn = 0
		self.main.hasItem = 0
		self.blockManager.running = 1
		self.main.scorer.comboTimeCounting = 1
		self.main.cursor.on = 1

		for x in xrange(self.gridPos[0]-2,self.gridPos[0]+3):
			for y in xrange(self.gridPos[1]-2,self.gridPos[1]+3):
				if 0 <= x < self.blockManager.gridWidth and 0 <= y < self.blockManager.gridHeight:
					self.blockManager.destroyPoint(x,y)
					#No points. :(

		if self.main.training:
			self.main.playMusic()

class VertiBomb:
	def __init__(self,main,blockManager):
		self.main = main
		self.main.cursor.bombOn = 1
		self.main.hasItem = 1
		self.blockManager = blockManager

		self.columnImage = pygame.transform.smoothscale(helpers.loadPNG('vertiExplosion'), \
														(self.blockManager.blockSize, self.blockManager.blockSize*self.blockManager.gridHeight))

		self.xPos = 0
		self.yPos = 0

	def compute(self):
		self.xPos, self.yPos = self.main.mousePos
		self.gridX = self.blockManager.mouseXToGridX(self.xPos)
		if self.gridX == 'badPos':
			if self.xPos < self.blockManager.indentX:
				self.gridX = 0
			else:
				self.gridX = self.blockManager.gridWidth - 1
		if self.main.mouseLeftDown or self.main.mouseRightDown:
			self.explode()

	def draw(self,surface):
		surface.blit(self.columnImage,(self.blockManager.indentX+self.blockManager.blockSize*self.gridX, self.blockManager.indentY))

	def explode(self):
		x = self.gridX
		for y in xrange(self.blockManager.gridHeight):
			self.blockManager.destroyPoint(x,y)
			#No points. :(
		self.dead = 1
		self.main.hasItem = 0
		self.main.cursor.bombOn = 0

		self.sound = helpers.loadOGG('bomb')
		self.sound.set_volume(self.main.normSoundVolume)
		self.sound.play()

class HorizBomb:
	def __init__(self,main,blockManager):
		self.main = main
		self.main.cursor.bombOn = 1
		self.main.hasItem = 1
		self.blockManager = blockManager

		self.rowImage = pygame.transform.smoothscale(helpers.loadPNG('horizExplosion'), \
														(self.blockManager.blockSize*self.blockManager.gridWidth, self.blockManager.blockSize))

		self.xPos = 0
		self.yPos = 0

	def compute(self):
		self.xPos, self.yPos = self.main.mousePos
		self.gridY = self.blockManager.mouseYToGridY(self.yPos)
		if self.gridY == 'badPos':
			if self.yPos < self.blockManager.indentY:
				self.gridY = 0
			else:
				self.gridY = self.blockManager.gridHeight - 1
		if self.main.mouseLeftDown or self.main.mouseRightDown:
			self.explode()

	def draw(self,surface):
		surface.blit(self.rowImage,(self.blockManager.indentX, self.blockManager.indentY+self.blockManager.blockSize*self.gridY))

	def explode(self):
		y = self.gridY
		for x in xrange(self.blockManager.gridWidth):
			self.blockManager.destroyPoint(x,y)
			#No points. :(
		self.dead = 1
		self.main.hasItem = 0
		self.main.cursor.bombOn = 0

		self.sound = helpers.loadOGG('bomb')
		self.sound.set_volume(self.main.normSoundVolume)
		self.sound.play()

class ScoreBonus:
	def __init__(self,main,blockManager):
		self.main = main
		self.blockManager = blockManager
		#This item works instantly.
		self.blockManager.scorer.getBonus(10)
		self.sound = helpers.loadOGG('+10')
		self.sound.set_volume(self.main.normSoundVolume)
		self.sound.play()
		self.dead = 1
	def compute(self):
		pass
	def draw(self,surface):
		pass

class Star:
	def __init__(self,main,blockManager):
		#Decreases the number of blocks needed to destroy them by 1
		self.main = main
		self.blockManager = blockManager
		self.timeLeft = self.main.movementSwitchK * 3 #Lasts for one full round.

		self.twinkleMinSize = 8
		self.twinkleMaxSize = 64
		self.twinkleMinTime = 8
		self.twinkleMaxTime = 24
		#Use a colorkey and non-smooth scaling to greatly increase efficiency!
		self.twinkleImage = pygame.transform.scale(helpers.loadImage('starTwinkle.png',(0,0,0)),(self.twinkleMaxSize*2,self.twinkleMaxSize*2))
		self.twinkles = []
		self.numTwinkles = 64
		for x in xrange(0,self.numTwinkles):
			t = Twinkle(self)
			self.twinkles.append(t)
			self.main.objects.append(t)

		#This item makes it so you only need 3 adjacent blocks.
		self.blockManager.neededAdjacents -= 1
		self.blockManager.setAllRecentlyMoved()

		if self.main.training:
			self.main.stopMusic()
		elif self.main.monis:
			self.main.movementSwitcher.turnOffMusic()
		self.music = helpers.loadOGG('star')
		self.music.set_volume(1)
		self.music.play(-1)

	def compute(self):
		for twinkle in self.twinkles:
			if twinkle.dead:
				self.twinkles.remove(twinkle)
				#Make a new one!
				t = Twinkle(self)
				self.twinkles.append(t)
				self.main.objects.append(t)

		self.timeLeft -= 1
		if self.timeLeft == 0:
			self.dead = 1
			self.music.stop()
			if self.main.training:
				self.main.loopMusic()
			elif self.main.monis:
				self.main.movementSwitcher.turnOnMusic()
			self.blockManager.neededAdjacents += 1

	def draw(self,surface):
		pass

class Twinkle:
	def __init__(self,star):
		self.star = star
		self.size = random.randint(self.star.twinkleMinSize,self.star.twinkleMaxSize)
		self.time = random.randint(self.star.twinkleMinTime,self.star.twinkleMaxTime)
		self.x = random.randint(-self.size,self.star.main.SCREEN_WIDTH)
		self.y = random.randint(-self.size,self.star.main.SCREEN_HEIGHT)
		self.frame = 0.0
		self.dead = 0
	def compute(self):
		self.frame += 1
		a = self.frame/self.time
		if a <= .5:
			self.alpha = a*2*255
		else:
			self.alpha = (1 - a)*2*255
		if self.frame == self.time:
			self.dead = 1
	def draw(self,surface):
		img = pygame.transform.scale(self.star.twinkleImage,(self.size,self.size)) #For much greater speed, no smoothscale. Colorkey + alpha.
		img.set_alpha(self.alpha)
		surface.blit(img,(self.x,self.y))

class Pause:
	def __init__(self,main):
		self.main = main
		self.bg = self.main.screen.copy()
		foregroundImage = pygame.transform.smoothscale(helpers.loadPNG('pauseForeground'),(self.main.SCREEN_WIDTH,self.main.SCREEN_HEIGHT))
		self.mixFGBG = self.bg.copy()
		self.mixFGBG.blit(foregroundImage,(0,0)) #foregroundImage has alphas in it, take care of them now!
		self.fgAlpha = 0
		self.fgAlphaInc = 1
		self.fps1 = 60 #Different than self.main.fps
		self.fps2 = 5
		self.fps = self.fps1
		self.pause()

		#compute and draw are called by me, not main!

	def pause(self):
		fadeOutTime = 1000/self.main.FPS*255/self.fgAlphaInc #milliseconds
		if self.main.training:
			self.main.fadeOutMusic(fadeOutTime)
		elif self.main.monis:
			self.main.movementSwitcher.fadeOutMusic(fadeOutTime)
		else:
			assert False
		for o in self.main.objects:
			if isinstance(o,Star):
				o.music.fadeout(fadeOutTime)

		self.done = 0

		while not self.done:
			self.compute()
			self.draw()
			self.checkInput()
			self.main.clock.tick(self.fps)

		self.dead = 1

		if self.main.training:
			self.main.loopMusic()

	def compute(self):
		if self.fgAlpha < 255:
			self.fgAlpha += self.fgAlphaInc
		else:
			self.fps = self.fps2

	def draw(self):
		self.main.screen.blit(self.bg,(0,0))
		self.mixFGBG.set_alpha(self.fgAlpha)
		self.main.screen.blit(self.mixFGBG,(0,0))
		pygame.display.flip()

	def checkInput(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
				self.done = 1
