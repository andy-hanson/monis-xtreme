import pygame
import random

import helpers

from circle_bounce import CircleBounce
from mango_bounce import MangoBounce
from memory import Memory
from mouse_in_circle import MouseInCircle
from shake import Shake
#from simple_q import SimpleQ TODO: Bring back
from timed_shoot import TimedShoot
from trace import Trace


class MinigameManager:
	def __init__(self,main):
		self.main = main
		self.SCREEN_WIDTH = self.main.SCREEN_WIDTH
		self.SCREEN_HEIGHT = self.main.SCREEN_HEIGHT
		self.FPS = 40

		self.prob = 0 #The probability after each round that a minigame will appear.
		self.difficulty = 1 #Range 1-6

	def getNewMovementType(self):
		if random.random() < self.prob:
			self.initGame()
			self.go()

	def initGame(self,game=None):
		if game is not None: #Used by the separate 'Minigames' mode.
			r = game
		else:
			r = random.randint(1,7)
		#if r == 0:
		#	self.game = SimpleQ(self)
		if r == 1:
			self.game = MouseInCircle(self)
		elif r == 2:
			self.game = Shake(self)
		elif r == 3:
			self.game = Trace(self)
		elif r == 4:
			self.game = Memory(self)
		elif r == 5:
			self.game = CircleBounce(self)
		elif r == 6:
			self.game = TimedShoot(self)
		else:
			assert r == 7
			self.game = MangoBounce(self)


	def go(self):
		#Play one minigame
		self.done = 0
		while not self.done:
			self.getInput()
			self.game.compute()
			if not self.main.minigameMode:
				self.main.sillinessManager.compute()
			self.game.draw(self.main.screen)
			if not self.main.minigameMode:
				self.main.sillinessManager.draw(self.main.screen)
			self.main.clock.tick(self.FPS)
			pygame.display.flip()

	def getInput(self):
		#Mouse bottons are assumed to be released the frame after they are pressed down.
		self.mouseUpDown = 0
		self.mouseLeftDown = 0
		self.mouseMiddleDown = 0
		self.mouseRightDown = 0
		self.mouseDownDown = 0

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.lose()

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					self.mouseLeftDown = 1
				elif event.button == 2:
					self.mouseMiddleDown = 2
				elif event.button == 3:
					self.mouseRightDown = 1
				elif event.button == 4:
					self.mouseUpDown = 1
				elif event.button == 5:
					self.mouseDownDown = 1

		self.mousePos = pygame.mouse.get_pos()
		self.main.mousePos = self.mousePos #For silliness' Ball class.

	def win(self):
		if not self.main.minigameMode:
			self.main.itemManager.getBonus(2)
		try:
			self.game.music.stop()
		except AttributeError:
			pass
		self.done = 1 #This minigame is over

		helpers.playSound('winMinigame')

	def lose(self):
		if not self.main.minigameMode:
			self.main.itemManager.getBonus(-2)
		try:
			self.game.music.stop()
		except AttributeError:
			pass
		self.done = 1 #This minigame is over

		helpers.playSound('loseMinigame')


	def displayImage(self,image,text):
		font = helpers.randomFont(self.fontSize)

		k = float(image.get_width())/image.get_height()
		if k < float(self.SCREEN_WIDTH)/self.SCREEN_HEIGHT:
			#It's tall.
			scale = float(self.SCREEN_HEIGHT)/image.get_height()
			image = pygame.transform.smoothscale(image,(int(round(image.get_width()*scale)),int(round(image.get_height()*scale))))
		else:
			#It's wide.
			scale = float(self.SCREEN_WIDTH)/image.get_width()
			image = pygame.transform.smoothscale(image,(int(round(image.get_width()*scale)),int(round(image.get_height()*scale))))



		frames = 100
		while frames > 0:
			self.main.screen.fill((255,255,255))
			self.main.screen.blit(image,image.get_rect(centerx=self.SCREEN_WIDTH/2,centery=self.SCREEN_HEIGHT/2))

			textImg = font.render(text,1,(255,255,255))
			blitX = -random.randint(0,self.textColorer.get_width()-textImg.get_width())
			blitY = -random.randint(0,self.textColorer.get_height()-textImg.get_height())
			textImg.blit(self.textColorer,(blitX,blitY),None,pygame.BLEND_MULT)
			textPos = textImg.get_rect(centerx=self.SCREEN_WIDTH/2,centery=self.SCREEN_HEIGHT/2)
			s2 = self.main.screen.copy()
			s2.blit(textImg,textPos,None)
			s2.set_alpha(192)
			self.main.screen.blit(s2,(0,0))

			pygame.display.flip()
			pygame.event.get()
			self.main.clock.tick(self.FPS)
			frames -= 1
