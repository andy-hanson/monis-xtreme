import math
import pygame

#Settings A: rad=160, b**=12, if 31.0/32 > rad2/rad < 1: b = 1.0/12, s3.set_alpha(28)
imageName = 'sample.png'


rad = 160

s3 = pygame.display.set_mode((rad*2-1,rad*2-1))

s = pygame.image.load(imageName)#pygame.transform.scale(pygame.image.load(imageName),(2400,2400))
w = s.get_width()
h = s.get_height()


circleImage = pygame.Surface((rad*2-1,rad*2-1)).convert_alpha()
circleImage.set_colorkey((0,0,0))
for x in xrange(0,rad*2-1):
    for y in xrange(0,rad*2-1):
        rad2 = math.sqrt((x-rad+1)**2 + (y-rad+1)**2)
        b = 1 - rad2/rad
        b **= 16
        if 31.0/32 < rad2/rad < 1:
            b = 1.0/16#1.0/8
        if b < 0:
            b = 0
        circleImage.set_at((x,y),(255,255,255,b*255))

pygame.image.save(circleImage,'circle.png')

s2 = pygame.Surface(s.get_size())
#s3 = pygame.Surface(circleImage.get_size())

space = 2 #NECESSARY!

for x in xrange(w):
    for y in xrange(h):
        if x % space == 0 and y % space == 0:
            if s.get_at((x,y))[0]:
                rect = pygame.Rect(x-rad,y-rad,rad*2-1,rad*2-1)
                blitX = x - rad
                blitY = y - rad
                circBlitX = 0
                circBlitY = 0
                if rect.x < 0:
                    circBlitX = rect.x
                    right = rect.right
                    rect.x = 0
                    rect.width = right
                    blitX = 0
                if rect.y < 0:
                    circBlitX = rect.y
                    bot = rect.bottom
                    rect.y = 0
                    rect.height = bot
                    blitY = 0
                if rect.right >= w:
                    rect.width = w - rect.x
                '''if rect.bottom >= h:
                    y = rect.y
                    rect.height = h - y'''
                try:
                    s3.blit(s2.subsurface(rect),(0,0))
                except ValueError:
                    s3.fill((0,0,0))
                s3.blit(circleImage,(circBlitX,circBlitY))
                s3.set_alpha(32)
                s2.blit(s3,(blitX,blitY))
                pygame.display.flip()
                
    pygame.display.set_caption(str(int(round(float(x)/w*100))))
    pygame.event.get()

#Now sharpen the image

maxB = 0
for x in xrange(0,s2.get_width()):
    for y in xrange(0,s2.get_height()):
        maxB = max(s2.get_at((x,y))[0],maxB)
    pygame.display.set_caption(str(x/2) + '/' + str(s.get_width()))
    pygame.event.get()
maxB /= 255.0
multiplier = 1/maxB
for x in xrange(0,s2.get_width()):
    for y in xrange(0,s2.get_height()):
        b = s2.get_at((x,y))[0]/255.0
        b *= multiplier
        b2 = int(round(b*255))
        s2.set_at((x,y),(b2,b2,b2))
    pygame.display.set_caption(str(x/2 + s2.get_width()/2) + '/' + str(s2.get_width()))
    pygame.event.get()

pygame.quit()

pygame.image.save(s2,'rhodiumized.png')

