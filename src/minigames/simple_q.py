import os
import pygame
import random

import helpers
import graphics

class SimpleQ:
	def __init__(self,manager):
		self.manager = manager
		numQs = 8
		self.num = random.randint(0,numQs - 1)
		img0 = helpers.loadPNG(os.path.join('minigames','simpleQ','q'+str(self.num),'0'),0)
		self.image0 = pygame.transform.smoothscale(img0, (self.manager.SCREEN_WIDTH/2, self.manager.SCREEN_HEIGHT))
		img1 = helpers.loadPNG(os.path.join('minigames','simpleQ','q'+str(self.num),'1'),0)
		self.image1 = pygame.transform.smoothscale(img1, (self.manager.SCREEN_WIDTH/2,self.manager.SCREEN_HEIGHT))
		q = helpers.getText(os.path.join('minigames','simpleQ','q'+str(self.num),'q.txt'))
		self.question, self.answer = helpers.split(q)
		self.answer = int(self.answer) #Either 0 or 1
		self.fontSize = 60
		self.font = pygame.font.Font(os.path.join('data','fonts','CRYSRG__.ttf'),self.fontSize)
		self.cursor = graphics.Cursor(self) #SimpleQ will act as Cursor's main.
		self.textColorer = helpers.loadPNG(os.path.join('minigames','simpleQ','qTextColorer'),0)
		self.highlighter = helpers.loadPNG(os.path.join('minigames','simpleQ','qHighlighter'),0)
		self.selected = 0 #0: left image. 1: right image.

		self.timeLeft = 128 - 16*self.manager.difficulty

	def compute(self):
		self.mousePos = self.manager.mousePos
		self.cursor.compute()
		if self.mousePos[0] < self.manager.SCREEN_WIDTH/2:
			self.selected = 0
		else:
			self.selected = 1
		if self.manager.mouseLeftDown or self.manager.mouseRightDown:
			if self.selected == self.answer:
				self.manager.win()
			else:
				self.manager.lose()
		self.timeLeft -= 1
		if self.timeLeft == 0:
			self.manager.lose()

	def draw(self,surface):
		text = self.font.render(self.question,1,(255,255,255))
		blitX = -random.randint(0,self.textColorer.get_width()-text.get_width())
		blitY = -random.randint(0,self.textColorer.get_height()-text.get_height())
		text.blit(self.textColorer,(blitX,blitY),None,pygame.BLEND_MULT)
		textPos = text.get_rect(centerx=self.manager.SCREEN_WIDTH/2,centery=self.manager.SCREEN_HEIGHT/2)
		pos0 = self.image0.get_rect(centerx=self.manager.SCREEN_WIDTH*1/4, centery=self.manager.SCREEN_HEIGHT/2)
		pos1 = self.image1.get_rect(centerx=self.manager.SCREEN_WIDTH*3/4, centery=self.manager.SCREEN_HEIGHT/2)
		surface.blit(self.image0,pos0)
		surface.blit(self.image1,pos1)
		if self.selected == 0:
			surface.blit(self.highlighter,(0,0))
		else:
			surface.blit(self.highlighter,(self.manager.SCREEN_WIDTH/2,0))
		surface.blit(text,textPos)
		self.cursor.draw(surface)
