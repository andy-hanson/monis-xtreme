import math
import os
import pygame

import animations
import blockManager
import difficulty
import fx
import graphics
import helpers
import items
from minigames.MinigameManager import MinigameManager
import scorer
import silliness

INCLUDE_INTRO = True

class Main:
	def __init__(self):
		pass

	def setup(self):
		#PYGAME STUFF
		self.SCREEN_WIDTH = 800
		self.SCREEN_HEIGHT = 800
		self.screen = pygame.display.set_mode((self.SCREEN_WIDTH,self.SCREEN_HEIGHT))

		self.PRINT_INFO = True

		self.clock = pygame.time.Clock()
		self.normalFPS = 40
		self.FPS = self.normalFPS

		pygame.init()

		self.normMusicVolume = .25
		self.normSoundVolume = .75

		#COMPUTING STUFF
		self.objects = []

		self.upKey = 0
		self.leftKey = 0
		self.rightKey = 0
		self.downKey = 0
		self.mouseUpDown = 0
		self.mouseLeftDown = 0
		self.mouseMiddleDown = 0
		self.mouseRightDown = 0
		self.mouseDownDown = 0
		self.mousePos = (0,0)

		pygame.mouse.set_visible(False)
		self.cursor = graphics.Cursor(self)
		self.minigameMode = False
		self.training = False
		self.monis = False
		self.canFlip = True #Turned off during the intro in runMonis()

	def setupMonis(self):
		self.monis = 1
		self.movementSwitchK = 512
		#The order objects are appended determines drawing order!
		bm = blockManager.BlockManager(self)
		self.blockManager = bm
		self.movementSwitcher = bm.movementSwitcher
		self.objects.append(graphics.Background(self))
		itm = items.ItemManager(self,bm)
		self.objects.append(itm)
		self.objects.append(graphics.GridBackground(bm))
		self.objects.append(bm)
		self.objects.append(graphics.GridForeground(bm))
		scr = scorer.Scorer(bm,itm)
		bm.scorer = scr
		self.scorer = scr
		self.objects.append(bm.scorer)
		#self.blockManager = bm #For easy reference
		self.itemManager = itm
		self.objects.append(self.cursor)

		#KNOW THE DIFFERENCE!
		self.itemOn = 0 #When the big bomb is going off or you need to select a spot to blow up, you can't do stuff.
		self.hasItem = 0 #Whether any item is in use or not. Prevents using more than one item at once.

		self.fxManager = fx.FXManager(self)
		self.minigameManager = MinigameManager(self)
		self.sillinessManager = silliness.SillinessManager(self)
		self.difficultyManager = difficulty.DifficultyManager(self)

	def runMonis(self):
		#Run the normal game. This comes after menu.

		#A short intro
		animations.countDown(self)
		#Go from white to the screen.
		t = 128
		self.canFlip = 0
		for i in xrange(t):
			self.getInput()
			self.cursor.compute()
			self.draw() #Will not flip yet because self.canFlip is off.
			s = self.screen.copy()
			self.screen.fill((255,255,255))
			s.set_alpha(255.0*i/t)
			self.screen.blit(s,(0,0))
			pygame.display.flip()
			self.clock.tick(self.FPS)
			self.setCaption()
		self.canFlip = 1
		#End intro

		self.gameRunning = 1
		self.won = 0
		self.lost = 0

		while self.gameRunning:
			self.clock.tick(self.FPS)
			self.getInput()
			self.compute()
			self.draw()

			if self.lost or self.sDown:
				self.lose()
			if self.won or self.aDown:
				self.win()

		self.movementSwitcher.stopMusic()
		scoreIndex = self.saveScore(self.scorer.score)
		self.displayScores(scoreIndex)

	def setupTraining(self):
		#The order objects are appended determines drawing order!
		self.training = 1
		self.movementSwitchK = 256*3
		bm = blockManager.BlockManager(self)
		self.blockManager = bm
		self.movementSwitcher = bm.movementSwitcher
		self.objects.append(graphics.Background(self))
		self.objects.append(graphics.GridBackground(bm))
		itm = items.ItemManager(self,bm)
		self.itemManager = itm
		self.objects.append(itm)
		self.objects.append(bm)
		self.objects.append(graphics.GridForeground(bm))
		scr = scorer.Scorer(bm,itm)
		bm.scorer = scr
		self.scorer = scr
		self.objects.append(bm.scorer)
		#self.blockManager = bm #For easy reference
		self.objects.append(self.cursor)

		#KNOW THE DIFFERENCE!
		self.itemOn = 0 #When the big bomb is going off or you need to select a spot to blow up, you can't do stuff.
		self.hasItem = 0 #Whether any item is in use or not. Prevents using more than one item at once.
		#Replace difficultyManager with:
		self.blockManager.maxTimeTillFall = 16
		self.blockManager.maxTimeTillNewBlock = 32

	def runTraining(self):
		self.music = helpers.loadOGG(os.path.join('mainMusics','training'))
		self.music.set_volume(self.normMusicVolume)
		self.music.play(-1)

		self.gameRunning = 1
		self.lost = 0

		while self.gameRunning:
			self.clock.tick(self.FPS)
			self.getInput()
			self.itemManager.getBonus(.01) #So trainees don't have to wait long to use items
			self.compute()
			self.draw()

			if self.lost:
				self.gameRunning = 0
			#Self.won is impossible. No difficultyManager

		self.music.stop()


	def getInput(self):
		#Mouse bottons are assumed to be released the frame after they are pressed down.
		self.mouseUpDown = 0
		self.mouseLeftDown = 0
		self.mouseMiddleDown = 0
		self.mouseRightDown = 0
		self.mouseDownDown = 0
		#Following used during testing.
		self.aDown = 0 #Instant win
		self.sDown = 0 #Instant lose

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.gameRunning = 0
				self.menuOn = 0

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					self.mouseLeftDown = 1
				elif event.button == 2:
					self.mouseMiddleDown = 1 #In testing, this gave me free points.
				elif event.button == 3:
					self.mouseRightDown = 1
				elif event.button == 4:
					self.mouseUpDown = 1
				elif event.button == 5:
					self.mouseDownDown = 1

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_a:
					self.aDown = 0#1 In testing, this was an instant win.
				elif event.key == pygame.K_s:
					self.sDown = 0#1 In testing, this was an instant lose.

		self.mousePos = pygame.mouse.get_pos()

	def compute(self):
		if not self.training:
			self.fxManager.compute()
			#Note: self.minigameManger has no compute function. When it is active, it takes over with its go function.
			self.sillinessManager.compute()
			self.difficultyManager.compute()

		index = 0
		while index < len(self.objects):
			self.objects[index].compute()
			#When you want to destroy an object, just give it a new variable, "dead", and set it to true.
			try:
				if self.objects[index].dead:
					self.objects.remove(self.objects[index])
					index -= 1
			except AttributeError:
				pass #There's no variable "dead" yet. So let the object stay.
			index += 1


	def draw(self):
		#self.screen.fill((255,255,255))
		self.screen.unlock()
		for o in self.objects:
			try:
				o.drawPriority
			except AttributeError:
				o.draw(self.screen)
		for o in self.objects:
			try:
				if o.drawPriority == 1:
					o.draw(self.screen)
			except AttributeError:
				pass
		for o in self.objects:
			try:
				if o.drawPriority == 2:
					o.draw(self.screen)
			except AttributeError:
				pass

		if not self.training:
			self.fxManager.draw(self.screen)
			self.sillinessManager.draw(self.screen)

		if self.canFlip:
			pygame.display.flip()
		self.setCaption()

	def getItem(self,item):
		self.objects.append(item)


	def lose(self):
		self.gameRunning = 0
		self.fadeToImage(helpers.loadPNG('lose'), 512)

	def win(self):
		self.gameRunning = 0
		self.fadeToImage(helpers.loadPNG('win'), 512)

	def fadeToImage(self,image,fadeTime):
		scr = self.screen.copy()

		if self.monis:
			self.movementSwitcher.fadeOutMusic(fadeTime)

		for time in xrange(fadeTime):
			a = int(round(255*  (float(time)/fadeTime)**4 ))
			s2 = scr.copy()
			s2.blit(image,(0,0))
			s2.set_alpha(a)
			self.screen.blit(s2,(0,0))
			pygame.display.flip()
			self.clock.tick(self.FPS)
			self.setCaption()
			self.getInput()


	def menu(self):
		monis = helpers.loadPNG(os.path.join('menu','MONIS'))
		monisCol = helpers.loadPNG(os.path.join('menu','MONIScol'))
		monisRect = pygame.rect.Rect(100,0,600,600*monis.get_height()/monis.get_width())
		#monis.get_rect(centerx=self.SCREEN_WIDTH/2,y=0)
		training = helpers.loadPNG(os.path.join('menu','Training'))
		trainingCol = helpers.loadPNG(os.path.join('menu','Trainingcol'))
		trainingRect = pygame.rect.Rect(0,200,800,800*training.get_height()/training.get_width())
		#training.get_rect(centerx=self.SCREEN_WIDTH/2,centery=self.SCREEN_HEIGHT/2)
		minigames = helpers.loadPNG(os.path.join('menu','Minigames'))
		minigamesCol = helpers.loadPNG(os.path.join('menu','Minigamescol'))
		minigamesRect = pygame.rect.Rect(0,420,800,800*minigames.get_height()/minigames.get_width())
		#minigames.get_rect(centerx=self.SCREEN_WIDTH/2,centery=self.SCREEN_HEIGHT*3/4)
		scores = helpers.loadPNG(os.path.join('menu','Scores'))
		scoresCol = helpers.loadPNG(os.path.join('menu','Scorescol'))
		scoresRect = pygame.rect.Rect(100,600,600,600*scores.get_height()/scores.get_width())
		choice = ''

		self.menuOn = 1
		while 1:
			self.getInput()
			if monisRect.collidepoint(self.mousePos):
				choice = 'monis'
			elif trainingRect.collidepoint(self.mousePos):
				choice = 'training'
			elif minigamesRect.collidepoint(self.mousePos):
				choice = 'minigames'
			elif scoresRect.collidepoint(self.mousePos):
				choice = 'scores'
			if self.mouseLeftDown or self.mouseRightDown and self.choice:
				#Do a short animation.
				if choice == 'monis':
					img = monisCol
					center = monisRect.center
					rect = monisRect
				elif choice == 'training':
					img = trainingCol
					center = trainingRect.center
					rect = trainingRect
				elif choice == 'minigames':
					img = minigamesCol
					center = minigamesRect.center
					rect = minigamesRect
				elif choice == 'scores':
					img = scoresCol
					center = scoresRect.center
					rect = scoresRect

				choiceZoomTime = 80

				if choice != 'scores':
					#Fade out the music over the course of the animation.
					#For scores, the music keeps playing.
					self.menuMusic.fadeout(choiceZoomTime*1000/self.FPS)

				for time in xrange(choiceZoomTime):
					scale = float(rect.height)/img.get_height() * math.e**(2.0*time/choiceZoomTime)
					if 0:#scale > 1:
						neededSize = img.get_height()*scale + 2 #The area that will be scaled. Don't waste time scaling stuff that will be outside the screen!
						minY = img.get_height()/2-neededSize/2
						if minY < 0: minY = 0
						maxY = img.get_height()/2+neededSize/2
						if maxY >= img.get_height(): maxY = img.get_height() - 1
						sub = img.subsurface(pygame.Rect(img.get_width()/2-neededSize/2,minY,neededSize,maxY-minY))
					else:
						sub = img

					scaled = pygame.transform.smoothscale(sub,(int(round(sub.get_width()*scale)),int(round(sub.get_height()*scale))))
					self.screen.fill((0,0,0))
					self.screen.blit(scaled,scaled.get_rect(center=center))
					self.clock.tick(self.FPS)
					self.setCaption()
					pygame.display.flip()
				return choice
			#Animation over.


			self.screen.fill((0,0,0))
			if choice == 'monis':
				self.screen.blit(pygame.transform.smoothscale(monisCol,monisRect.size),monisRect.topleft)
			else:
				self.screen.blit(pygame.transform.smoothscale(monis,monisRect.size),monisRect.topleft)
			if choice == 'training':
				self.screen.blit(pygame.transform.smoothscale(trainingCol,trainingRect.size),trainingRect.topleft)
			else:
				self.screen.blit(pygame.transform.smoothscale(training,trainingRect.size),trainingRect.topleft)
			if choice == 'minigames':
				self.screen.blit(pygame.transform.smoothscale(minigamesCol,minigamesRect.size),minigamesRect.topleft)
			else:
				self.screen.blit(pygame.transform.smoothscale(minigames,minigamesRect.size),minigamesRect.topleft)
			if choice == 'scores':
				self.screen.blit(pygame.transform.smoothscale(scoresCol,scoresRect.size),scoresRect.topleft)
			else:
				self.screen.blit(pygame.transform.smoothscale(scores,scoresRect.size),scoresRect.topleft)
			if not self.menuOn:
				pygame.quit()
				return ''
			self.cursor.compute()
			self.cursor.draw(self.screen)
			pygame.display.flip()

	def minigamesMenu(self):
		self.minigameDifficulty = 1
		self.minigameMode = 1
		self.minigameManager = MinigameManager(self)
		choices = [
			# 'Quick Quiz',
			'Circle of Spikes',
			'Shake Shake',
			'Mouse Trace',
			'Memory Dots',
			'Circle Bounce',
			'Space Shooter',
			'Mango Bounce',
			'Difficulty: ' + str(self.minigameDifficulty)
		]
		nChoices = 7

		#font = pygame.font.Font(os.path.join('data','CRYSRG__.TTF'),80)
		fonts = []
		for c in choices:
			fonts.append(helpers.randomFont(80))

		self.music = helpers.loadOGG('minigames')
		self.music.set_volume(self.normMusicVolume)
		self.music.play(-1)

		self.menuOn = 1
		self.mouseLeftDown = 0
		self.mouseRightDown = 0
		while self.menuOn:
			self.cursor.compute()
			choice = self.mousePos[1] * (nChoices + 1) / self.SCREEN_HEIGHT

			if self.mouseLeftDown or self.mouseRightDown:
				if choice < nChoices:
					self.music.stop()
					self.minigameManager.initGame(choice + 1) # TODO: Remove + 1 when SimpleQ is back
					self.minigameManager.go()
				else:
					self.minigameDifficulty += 1
					if self.minigameDifficulty > 6:
						self.minigameDifficulty = 1
					choices[nChoices] = 'Difficulty: ' + str(self.minigameDifficulty)
					self.minigameManager.difficulty = self.minigameDifficulty
				self.mouseLeftDown = 0
				self.mouseRightDown = 0

			self.screen.fill((0,0,0))
			for i in xrange(len(choices)):
				if i == choice:
					text = fonts[i].render(choices[i],1,(255,255,192))
				else:
					text = fonts[i].render(choices[i],1,(192,192,255))
				self.screen.blit(text,text.get_rect(centerx=self.SCREEN_WIDTH/2,y=i*self.SCREEN_HEIGHT/len(choices)))#centery=(i+1)*self.SCREEN_HEIGHT/(len(choices)+1)))
			self.cursor.draw(self.screen)

			pygame.display.flip()
			self.getInput()
			self.clock.tick(40)
			self.setCaption()

		self.music.stop()

	def displayScores(self,highlightedScore=None):
		#When a new high score has just been gained, it will be highlighted.
		scores = helpers.split(helpers.getText('scores.dat'))

		if highlightedScore is not None: #If you're not just looking at old scores:
			if highlightedScore == 0:
				sound = helpers.loadOGG('applause')
				sound.set_volume(1)
				sound.play()

		self.startMenuMusic()

		digitWidth = 40
		digitHeight = 50
		digitSpace = 10
		numberImages = []
		for num in xrange(10):
			img = pygame.transform.smoothscale(helpers.loadPNG('num' + str(num)),(digitWidth,digitHeight))
			numberImages.append(img)

		background = helpers.loadPNG('background')
		xSize = (digitWidth + digitSpace)*6
		ySize = digitHeight*2
		backgroundImage = pygame.transform.smoothscale(helpers.loadPNG('scoreBackground'),(xSize,ySize))
		foregroundImage = pygame.transform.smoothscale(helpers.loadPNG('scoreForeground'),(xSize,ySize))
		highlighterImage = pygame.transform.smoothscale(helpers.loadPNG('scoreHighlighter'),(xSize,ySize))
		#For highlighting color:
		colorTime = 0
		colorPhase = 64

		self.cursor = graphics.Cursor(self)

		self.menuOn = 1
		while self.menuOn:
			self.getInput()
			self.cursor.compute()

			self.screen.blit(background,(0,0))

			for i in xrange(len(scores)):
				score = int(scores[i])
				score *= 100

				ones = score%10
				tens = score%100/10
				huns = score%1000/100
				thos = score%10000/1000
				tths = score%100000/10000

				blitX = self.SCREEN_WIDTH/2
				blitY = i*100 + 50

				pos = backgroundImage.get_rect(centerx=blitX,centery=blitY)
				self.screen.blit(backgroundImage,pos)
				self.screen.blit(numberImages[tths],(blitX-2*(digitWidth+digitSpace)-digitWidth/2,blitY - digitHeight/2))
				self.screen.blit(numberImages[thos],(blitX-1*(digitWidth+digitSpace)-digitWidth/2,blitY - digitHeight/2))
				self.screen.blit(numberImages[huns],(blitX+0*(digitWidth+digitSpace)-digitWidth/2,blitY - digitHeight/2))
				self.screen.blit(numberImages[tens],(blitX+1*(digitWidth+digitSpace)-digitWidth/2,blitY - digitHeight/2))
				self.screen.blit(numberImages[ones],(blitX+2*(digitWidth+digitSpace)-digitWidth/2,blitY - digitHeight/2))

				if i == highlightedScore:
					img = highlighterImage.copy()
					#Fill it with a color.
					colorTime += 1
					H = 360 * float(colorTime)/colorPhase
					while H >= 360:
						H -= 360
					S = 100
					V = 100
					A = 100
					col = pygame.Color(0,0,0)
					col.hsva = (H,S,V,A)
					s = img.copy()
					s.fill(col)
					img.blit(s,(0,0),None,pygame.BLEND_MULT)
					self.screen.blit(img,pos)#,None,pygame.BLEND_ADD)

				self.screen.blit(foregroundImage,pos)

			self.cursor.draw(self.screen)

			pygame.display.flip()
			self.clock.tick(self.FPS)
			self.setCaption()

	def reset(self):
		#Performs NECESSARY resetting.
		self.objects = []
		self.cursor.bombOn = False
		self.monis = False
		self.training = False
		self.minigamesMode = False

		if not self.menuMusic:
			pygame.mixer.init()
			pygame.mixer.stop()

		self.startMenuMusic()

	def setCaption(self):
		pygame.display.set_caption('Monis Xtreme') # Framerate: ' + str(int(self.clock.get_fps())) + '/' + str(self.FPS))

	def saveScore(self,score):
		scores = helpers.split(helpers.getText('scores.dat'))

		for i in xrange(len(scores)):
			scores[i] = int(scores[i])
		scores.append(score)
		scores.sort()
		scores.reverse()
		text = ''
		scoreIndex = None
		#In case there are 2 of the same score, we want the lowest index possible, to make the player feel good about theirself.
		#In other words, if they match their own old high score, their new one will be highlighted as above the old one.
		for i in xrange(len(scores) - 1):#Don't include the last element.
			#If score is not a new high score, it is the last element. If score is a new high score, the lowest score will be deleted.
			text += str(scores[i]) + '\n'
			if scoreIndex is None:
				if scores[i] == score:
					scoreIndex = i
		helpers.writeToFile('scores.dat',text)

		return scoreIndex #To be used in displayScores

	def startMenuMusic(self):
		#Get ready for menu
		if not self.menuMusic: #MenuMusic plays on both the main menu and on the scores menu. If you were just on the scores menu, it's already there and playing.
			#Otherwise, it's set to None by self.stopMenuMusic()
			self.menuMusic = helpers.loadOGG('titleThemeQuickBegin')
			self.menuMusic.set_volume(self.normMusicVolume)
			self.menuMusic.play(-1)

	def stopMenuMusic(self):
		self.menuMusic.stop()
		self.menuMusic = None


	def playMusic(self):
		self.music.play()
	def loopMusic(self):
		self.music.play(-1)
	def stopMusic(self):
		self.music.stop()
	def fadeOutMusic(self, fadeOutTime):
		self.music.fadeout(fadeOutTime)



#Actually run it.
m = Main()
m.setup()

m.menuMusic = helpers.loadOGG('titleTheme')
m.menuMusic.set_volume(m.normMusicVolume)
m.menuMusic.play(-1)


if INCLUDE_INTRO:
	#Introduction. It's in tune with the music (assuming full FPS).
	animations.logo(m)
	m.fadeToImage(helpers.loadPNG('Monis3bg'),128)
	animations.monis3(m)

done = 0
while not done:
	choice = m.menu()
	if choice == 'monis':
		m.stopMenuMusic()
		m.setupMonis()
		m.runMonis()
	elif choice == 'training':
		m.stopMenuMusic()
		m.setupTraining()
		m.runTraining()
	elif choice == 'minigames':
		m.stopMenuMusic()
		m.minigamesMenu()
	elif choice == 'scores':
		m.displayScores()
	elif choice == '':
		#Exited the menu.
		#So end everything.
		done = 1
	else:
		error
	m.reset()
