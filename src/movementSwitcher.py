import math
import os
import pygame
import random

import helpers

class MovementSwitcher:
	def __init__(self,blockManager):
		self.blockManager = blockManager
		self.main = self.blockManager.main
		k = self.main.movementSwitchK
		self.maxValue = 3 * k
		self.originalTime = 0
		self.hSliderTime = 1 * k
		self.vSliderTime = 2 * k
		self.value = 0

		self.pointerSize = 340#240 #Length of one side of the square surrounding the circle formed by the pointer spinning.
		self.pointerImage = pygame.transform.smoothscale(helpers.loadPNG('movementPointer'),(self.pointerSize,self.pointerSize))
		self.pointerCenterX = self.main.SCREEN_WIDTH*3/4 + 20
		self.pointerCenterY = self.main.SCREEN_HEIGHT/2 + 30 + (self.main.SCREEN_HEIGHT/2 - 30)/2#self.main.SCREEN_HEIGHT*3/4 + 50/4

		self.backgroundImage = pygame.transform.smoothscale(helpers.loadPNG('movementSwitcherBackground'),(self.pointerSize,self.pointerSize))
		#The big image has an extro 80 pixels compared to the background's 1600.
		self.borderTab = self.pointerSize*40/1600
		size = self.pointerSize + self.borderTab*2
		self.borderImage = pygame.transform.smoothscale(helpers.loadPNG('movementSwitcherForeground'),(size,size))

		self.canMusic = True #Turned off by class Star in items.py

	def compute(self):
		if self.blockManager.running:
			if self.value == self.originalTime:
				self.blockManager.movementType = 'original'
				self.switch()
			elif self.value == self.hSliderTime:
				self.blockManager.movementType = 'hSlider'
				self.switch()
			elif self.value == self.vSliderTime:
				self.blockManager.movementType = 'vSlider'
				self.switch()
			self.value += 1
			if self.value == self.maxValue:
				self.value = 0

	def draw(self,surface):
		#The clock in the bottom right
		surface.blit(self.backgroundImage,(self.pointerCenterX-self.pointerSize/2, self.pointerCenterY-self.pointerSize/2))

		ang = 2*math.pi*self.value/self.maxValue
		rotatedImage = pygame.transform.rotozoom(self.pointerImage,-ang*180/math.pi,1)
		blitX = self.pointerCenterX - self.pointerSize/2 - (rotatedImage.get_width() - self.pointerSize)/2
		blitY = self.pointerCenterY - self.pointerSize/2 - (rotatedImage.get_height() - self.pointerSize)/2
		surface.blit(rotatedImage,(blitX,blitY))

		surface.blit(self.borderImage,(self.pointerCenterX-self.pointerSize/2-self.borderTab, self.pointerCenterY-self.pointerSize/2-self.borderTab))

	def switch(self):
		if not self.main.training:
			self.main.minigameManager.getNewMovementType()
			self.main.fxManager.getNewMovementType()

			if self.canMusic:
				#New music
				pass
				#music = random.randint(0,7)
				#self.music = helpers.loadOGG(os.path.join('mainMusics',str(music)))
				#self.music.set_volume(self.main.normMusicVolume)
				#self.music.play()

	def stopMusic(self):
		pass # self.music.stop()

	def setMusicVolume(self, vol):
		pass #self.music.set_volume(vol)

	def turnOffMusic(self):
		self.music.stop()
		self.canMusic = 0

	def turnOnMusic(self):
		self.canMusic = 1

	def fadeOutMusic(self, fadeTime):
		pass #self.music.fadeout(int(round(fadeTime*1000/self.main.FPS)))
