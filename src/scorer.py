import pygame

import animations
import helpers

class Scorer:
	def __init__(self,blockManager,itemManager):
		self.blockManager = blockManager
		self.itemManager = itemManager
		self.main = self.blockManager.main
		self.score = 0
		self.digitWidth = 40
		self.digitHeight = 50
		self.digitSpace = 10
		self.blitX = self.main.SCREEN_WIDTH*3/4 + 20#The center
		self.blitY = self.main.SCREEN_HEIGHT/2 #The center

		self.numberImages = []
		for num in xrange(10):
			img = pygame.transform.smoothscale(helpers.loadPNG('num' + str(num)),(self.digitWidth,self.digitHeight))
			self.numberImages.append(img)
		xSize = (self.digitWidth + self.digitSpace)*6
		ySize = self.digitHeight*2
		self.backgroundImage = pygame.transform.smoothscale(helpers.loadPNG('scoreBackground'),(xSize,ySize))
		self.foregroundImage = pygame.transform.smoothscale(helpers.loadPNG('scoreForeground'),(xSize,ySize))

		self.combo = 1
		self.comboLastTime = self.blockManager.maxTimeTillNewBlock * self.blockManager.neededAdjacents * 3 / 2
		self.comboTimeLeft = 0

		self.comboTimeCounting = 1 #Turned off by BigBomb

	def compute(self):
		self.comboLastTime = self.blockManager.maxTimeTillNewBlock * self.blockManager.neededAdjacents * 3 / 2
		if self.comboTimeLeft and self.comboTimeCounting:
			self.comboTimeLeft -= 1
			if self.comboTimeLeft == 0:
				if self.main.PRINT_INFO: print 'lost combo'
				if self.combo > 6: animations.combo(self.main,self.combo)
				self.combo = 1

		#CHEATING:
		if self.main.mouseMiddleDown:
			self.getPoints(5)

	def draw(self,surface):
		pos = self.backgroundImage.get_rect(centerx = self.blitX,centery = self.blitY) #A rectangle
		surface.blit(self.backgroundImage,pos)

		self.score *= 100

		ones = self.score%10
		tens = self.score%100/10
		huns = self.score%1000/100
		thos = self.score%10000/1000
		tths = self.score%100000/10000

		surface.blit(self.numberImages[tths],(self.blitX-2*(self.digitWidth+self.digitSpace)-self.digitWidth/2,self.blitY - self.digitHeight/2))
		surface.blit(self.numberImages[thos],(self.blitX-1*(self.digitWidth+self.digitSpace)-self.digitWidth/2,self.blitY - self.digitHeight/2))
		surface.blit(self.numberImages[huns],(self.blitX+0*(self.digitWidth+self.digitSpace)-self.digitWidth/2,self.blitY - self.digitHeight/2))
		surface.blit(self.numberImages[tens],(self.blitX+1*(self.digitWidth+self.digitSpace)-self.digitWidth/2,self.blitY - self.digitHeight/2))
		surface.blit(self.numberImages[ones],(self.blitX+2*(self.digitWidth+self.digitSpace)-self.digitWidth/2,self.blitY - self.digitHeight/2))

		self.score /= 100

		surface.blit(self.foregroundImage,pos) #Same pos because: same size, same position

	def getPoints(self, num):
		'''Num is of blocks; points calculated in this function.'''
		k = num-self.blockManager.neededAdjacents
		#Sequence 1,3,6,10,15,21, etc.
		scorePlus = 0
		for x in xrange(k+1): #Includes 0 to k.
			scorePlus += x + 1
		self.score += self.combo * scorePlus
		self.itemManager.getScore()

		self.combo += 1
		self.comboTimeLeft = self.comboLastTime

		combo = self.combo
		if combo > 25: #Only 25 sounds
			combo = 25
		sound = helpers.loadOGG('destroyBlocks' + str(combo))
		sound.play()

	def getBonus(self,amount):
		self.score += amount
