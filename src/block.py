import random

class Block:
	def __init__(self,blockManager,xPos,yPos,col):
		self.blockManager = blockManager
		self.size = self.blockManager.blockSize
		self.xPos = xPos
		self.yPos = yPos
		self.col = col #A number
		self.image = self.blockManager.images[col]

		self.recentlyMoved = 1

	def compute(self):
		pass

	def draw(self,surface):
		surface.blit(self.image,(self.xPos*self.size + self.blockManager.indentX,self.yPos*self.size + self.blockManager.indentY))
