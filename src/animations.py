import pygame
import math
import os
import random

import graphics
import helpers

def combo(main,num):
	r = random.randint(0,3)
	surface = main.screen
	words = ['gnarly', 'tubular', 'way cool', 'awesome', 'mondo', 'groovy', 'outrageous', 'funky']
	word = words[random.randint(0,len(words)-1)]
	fontSize = 160
	font = helpers.randomFont(fontSize)
	text = font.render(word,1,(255,255,255))
	font2 = helpers.randomFont(80)
	numText = font2.render(str(num),1,(0,0,0))
	time = 128
	jiggleRad = 64

	numberImages = []
	digitWidth = 400
	digitHeight = 500
	for n in xrange(10):
		img = pygame.transform.smoothscale(helpers.loadPNG('num' + str(n)),(digitWidth,digitHeight))
		numberImages.append(img)
	#Cut down on needed memory
	ones = num%10
	tens = num%100/10
	onesImage = numberImages[ones]
	tensImage = numberImages[tens]
	del numberImages
	'''xSize = (digitWidth + digitSpace)*6
	ySize = self.digitHeight*2'''

	stars = []

	for i in xrange(time):
		bgCol = pygame.Color(0,0,0)
		h = random.random()*360
		bgCol.hsva= (h,100,100,100)
		surface.fill(bgCol)


		surface.blit(tensImage,tensImage.get_rect(right=surface.get_width()/2,centery=surface.get_height()/2))
		surface.blit(onesImage,onesImage.get_rect(left=surface.get_width()/2,centery=surface.get_height()/2))

		jiggleAng = random.random()*2*math.pi
		thisJiggleRad = random.random()*jiggleRad
		centerx = surface.get_width()/2 + thisJiggleRad*math.cos(jiggleAng)
		centery = surface.get_height()/2 + thisJiggleRad*math.sin(jiggleAng)
		surface.blit(text,text.get_rect(center=(centerx,centery)))

		for i in xrange(4):
			ang = (random.random()*2-1)*math.pi/2
			scale = random.random()
			r = pygame.transform.rotozoom(numText,ang,scale)
			surface.blit(r,(random.randint(0,surface.get_width()-1),random.randint(0,surface.get_height()-1)))


		x = random.randint(0,surface.get_width()-1)
		y = random.randint(0,surface.get_height()-1)
		stars.append(graphics.Star(None,x,y)) #Give it None for blockManager.
		x = random.randint(0,surface.get_width()-1)
		y = random.randint(0,surface.get_height()-1)
		stars.append(graphics.Star(None,x,y)) #Give it None for blockManager.

		i = 0
		while i < len(stars):
			stars[i].compute()
			stars[i].draw(surface)
			try:
				if stars[i].dead:
					del stars[i]
					i -= 1
			except AttributeError: #No variable 'dead' yet
				pass
			i += 1

		pygame.display.flip()
		main.clock.tick(main.FPS)
		main.setCaption()
		pygame.event.get()

def countDown(main):
	surface = main.screen
	imgs = []
	for x in xrange(3,0,-1):
		imgs.append(helpers.loadPNG(os.path.join('intro',str(x))))

	numTime = 64

	clock = pygame.time.Clock()

	for i in xrange(3):
		img = imgs[i]

		for time in xrange(numTime):
			scale = 1.0/4*math.e**(4*float((time) - numTime/2)/(numTime/2))
			if scale > 1:
				neededSize = img.get_width()/scale + 2 #The area that will be scaled. Don't waste time scaling stuff that will be outside the screen!
				sub = img.subsurface(pygame.Rect(img.get_width()/2-neededSize/2,img.get_height()/2-neededSize/2,neededSize,neededSize))
			else:
				sub = img
			scaled = pygame.transform.smoothscale(sub,(int(round(sub.get_width()*scale)),int(round(sub.get_height()*scale))))
			surface.fill((0,0,0))
			surface.blit(scaled,((surface.get_width()-scaled.get_width())/2, (surface.get_height()-scaled.get_height())/2))
			main.clock.tick(main.FPS)
			pygame.display.flip()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return
			main.setCaption()

def logo(main):
	surface = main.screen
	text = helpers.loadPNG(os.path.join('logo','text'))
	line = helpers.loadPNG(os.path.join('logo','line'))

	surface.blit(text,(0,0))

	time = 256
	for i in xrange(time+1):
		x = int(round(line.get_width()*(1 - float(i)/time)))
		surface.blit(line.subsurface(x,0,line.get_width()-x,line.get_height()),(x,0))
		pygame.display.flip()
		main.clock.tick(main.FPS)
		main.setCaption()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				k

def monis3(main):
	#Displays the Monis 3 logo.
	surface = main.screen
	grid = helpers.loadPNG('MONIS3grid')
	w = grid.get_width()
	h = grid.get_height()
	#surface.fill((128,128,128))
	reachY = 0
	reachX = 0
	time = 256
	for i in xrange(time):
		reachY = int(round(float(h)*i/time))
		reachX = int(round(w*(float(i)%(float(time)/h))/(float(time)/h)))

		for y in xrange(reachY):
			for x in xrange(reachX):
				if grid.get_at((x,y)) == (255,255,255,255):
					color = (random.randint(0,1)*255,random.randint(0,1)*255,random.randint(0,1)*255)
					rect = pygame.rect.Rect(x*surface.get_width()/w,y*surface.get_height()/h,surface.get_width()/w,surface.get_height()/h)
					pygame.draw.rect(surface,color,rect)

		pygame.display.flip()
		main.clock.tick(main.FPS)
		main.setCaption()
		pygame.event.get()
