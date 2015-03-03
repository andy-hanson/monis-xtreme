import math
import os
import pygame
import random

def addFunc(num):
	#1,3,6,10,15...
	r = 0
	for x in xrange(num+1):
		r += x
	return r

def angleDifference(a,b):
	#Returns the angle between two angles
	return min(abs(b-a),2*math.pi-abs(b-a))

def blitShrunk(surface,blitted,size):
	surface.blit(pygame.transform.scale(blitted,size))

class Circle:
	'''Used for collision.'''
	def __init__(self,x,y,rad,image=None):
		self.x = x
		self.y = y
		self.rad = rad
		self.image = image
	def collideCircle(self,other):
		return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2) <= self.rad + other.rad
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
				return above
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

			if dist <= self.rad and touchesSegment:
				above = self.y < intersectY #Greater y value means go down
				return above
			return 0

	def draw(self,surface):
		if self.image:
			surface.blit(self.image,(self.x-self.rad,self.y-self.rad))

	def update(self,x,y):
		self.x = x
		self.y = y
	def __str__(self):
		return 'Circle: ' + str(self.x) + ',' + str(self.y) + ',' + str(self.rad)


def copyList(l1):
	l2 = []
	for entry in l1:
		try:
			entry[0] #It's another list!
			l2.append(copyList(entry))
		except TypeError:
			l2.append(entry)
	return l2

def equalLists(lista,listb):
	'''Ignores order of elements.'''
	if len(lista) != len(listb):
		return 0
	for element in lista:
		if listb.count(element) != lista.count(element):
			return 0
	return 1

def equalMatrices(m1,m2):
	#Assume equal size
	for x in xrange(len(m1)):
		for y in xrange(len(m1[0])):
			if m2[x][y] != m1[x][y]:
				return 0
	return 1

def getText(name):
	fullname = os.path.join('data',name)
	in_file = open(fullname,'rU')
	text = in_file.read()
	in_file.close()
	text = removeCharFromString(text, '\r')
	return text

def loadImage(name, colorkey=None):
	image = pygame.image.load(os.path.join('data', 'images', name)).convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, pygame.RLEACCEL)
	return image

def loadOGG(name):
	path = os.path.join('data', 'sounds', name + '.ogg')
	assert os.path.exists(path)
	return pygame.mixer.Sound(path)

def playSound(name):
	sound = loadOGG(name)
	sound.set_volume(1)
	sound.play()

def loadPNG(name,autoPath=1):
	'''Loads a PNG with alpha values. For completely opaque PNGs, use loadImage.'''
	if autoPath:
		fullname = os.path.join('data', 'images', name + '.png')
	else:
		fullname = os.path.join('data', name + '.png')
	return pygame.image.load(fullname).convert_alpha()

def loadPNGNoAlpha(name):
	fullname = os.path.join('data','images',name + '.png')
	image = pygame.image.load(fullname)
	#image.convert()
	return image

'''def loadWAV(name):
	return pygame.mixer.Sound(os.path.join('data','sounds',name + '.wav'))'''

def hardScale(image,scale):
	return pygame.transform.scale(image,(scale*image.get_width(),scale*image.get_height()))

def randomFont(size):
	fonts = split(getText(os.path.join('fonts','list.txt')))
	font = fonts[random.randint(0,len(fonts)-1)]
	return pygame.font.Font(os.path.join('data','fonts',font + '.ttf'),size)

def removeCharFromString(string, removechar):
	'''Returns a string that is the original without any removechar'''
	rs = ''
	for character in string:
		if character != removechar:
			rs += character
	return rs

def removeRepeats(list1):
	'''Removes repeats from a list. Non-destructive.'''
	list2 = []
	for element in list1:
		if list2.count(element) == 0:
			list2.append(element)
	return list2

def split(string):
	'''Turns a string into a list of strings, breaking it at each \n'''
	r = []
	this = ''
	for char in string:
		if char == '\n':
			r.append(this)
			this = ''
		else:
			this += char
	if this != '':
		r.append(this)
	return r

def writeToFile(name,text):
	fullname = os.path.join('data',name)
	outFile = open(fullname,'w')
	outFile.write(text)
	outFile.close()
