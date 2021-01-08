 # from sympy import *
from sympy.geometry import *
# import math
import random
import operator
import statistics

import pygame
from pygame.locals import *
from sys import exit

from math import *

# availableParts = [name, LINE, length]
# availableParts = [name, CURVE, radius, angle]
availableParts = []

# C8236: 78mm
# C8200: 87mm
# C8207: 175mm
# C8205: 350mm
# C8246: 350mm (side swipe)
# C7036: 525mm (line change)
# availableParts.append(["C8236", "LINE", 78])
# availableParts.append(["C8200", "LINE", 87])
availableParts.append(["C8207", "LINE", 175])
# availableParts.append(["C8205", "LINE", 350])
# availableParts.append(["C8246", "LINE", 350])
# availableParts.append(["C8200", "LINE", 525])

# R1: 58 - 214, center 136, C8278 (22.5), C8202 (45), C8201 (90, closed tracks)
# availableParts.append(["C8278", "CURVE", 136, 22.5])
# availableParts.append(["C8202", "CURVE", 136, 45])
# availableParts.append(["C8201", "CURVE", 136, 90])

# R2: 214 - 370, center 292, C8234 (22.5), C8206 (45), C8203 (90, line change)
# availableParts.append(["C8234", "CURVE", 292, 22.5])
# availableParts.append(["C8206", "CURVE", 292, 45])
availableParts.append(["C8203", "CURVE", 292, 90])

# R3: 370 - 526, center 448, C8204 (22.5)
# availableParts.append(["C8204", "CURVE", 448, 22.5])

# R4: 526 - 682, center 604, C8235 (22.5)
# availableParts.append(["C8235", "CURVE", 604, 22.5])

# We need this if we want to be able to specify our
#  arc in degrees instead of radians
def degreesToRadians(deg):
    return deg/180.0 * pi

# Draw an arc that is a portion of a circle.
# We pass in screen and color,
# followed by a tuple (x,y) that is the center of the circle, and the radius.
# Next comes the start and ending angle on the "unit circle" (0 to 360)
#  of the circle we want to draw, and finally the thickness in pixels
def drawCircleArc(screen,pCenter,sCenter,scale,color,center,radius,startDeg,endDeg,thickness):
	xCenter, yCenter = pCenter
	xSCenter, ySCenter = sCenter
	center = (xSCenter + scale * (center[0] - xCenter), ySCenter - scale * (center[1] - yCenter))
	radius = scale * radius
	(x,y) = center
	rect = (x-radius,y-radius,radius*2,radius*2)
	startRad = degreesToRadians(startDeg)
	endRad = degreesToRadians(endDeg)

	pygame.draw.arc(screen,color,rect,startRad,endRad,thickness)


class Part:
	def __init__(self, pIn = (0, 0), angleIn = 0):
		self.pIn = pIn
		self.angleIn = angleIn
		
		self.pOut = pIn
		self.angleOut = angleIn

	def draw(self, screen, shift, sCenter, scale, color):
		print("Must be defined in child class")
	
	def computePointOut(self):
		print("Must be defined in child class")
	
	def translateCoord():
		pass

class Line(Part):
	def __init__(self, pIn = (0, 0), angleIn = 0, length = 1):
		super().__init__(pIn, angleIn)
		
		self.length = length
	
	def computePointOut(self):
		angleInR = degreesToRadians(self.angleIn)
		tmp = (self.length * cos(angleInR), self.length * sin(angleInR))
		self.pOut = tuple(map(operator.add, self.pIn, tmp))
		self.angleOut = self.angleIn
	
	def draw(self, screen, pCenter, sCenter, scale, color):
		xCenter, yCenter = pCenter
		xSCenter, ySCenter = sCenter
		pygame.draw.line(screen,color,
			(xSCenter + scale * (self.pIn[0]  - xCenter), ySCenter - scale * (self.pIn[1]  - yCenter)),
			(xSCenter + scale * (self.pOut[0] - xCenter), ySCenter - scale * (self.pOut[1] - yCenter)), 1)

class Curve(Part):
	def __init__(self, pIn = (0, 0), angleIn = 0, radius = 1, angle = 45, direction = "left"):
		super().__init__(pIn, angleIn)
		
		self.radius = radius
		self.angle = angle
		
		self.center = self.pIn
		self.direction = direction

	def computePointOut(self):
		angleInR = degreesToRadians(self.angleIn)
		angleR = degreesToRadians(self.angle)
		
		coeff = 1 if self.direction == "left" else -1

		tmp1 = (-coeff * self.radius * sin(angleInR), coeff * self.radius * cos(angleInR))
		self.center = tuple(map(operator.add, self.pIn, tmp1))
		
		tmp2 = (coeff * self.radius * sin(angleInR + coeff * angleR), -coeff * self.radius * cos(angleInR + coeff * angleR))
		
		self.pOut = tuple(map(operator.add, self.center, tmp2))
		self.angleOut = (self.angleIn + coeff * self.angle) % 360

	def draw(self, screen, pCenter, sCenter, scale, color):
		if self.direction == "left":
			startAngle = self.angleIn - 90
			stopAngle = self.angleIn - 90 + self.angle
			# print("left -> startAngle=" + str(startAngle) + " stopAngle=" + str(stopAngle))
			drawCircleArc(screen, pCenter, sCenter, scale, color, self.center, self.radius, startAngle, stopAngle,1)
		else:
			startAngle = self.angleIn + 90 - self.angle
			stopAngle = self.angleIn + 90
			# print("right -> startAngle=" + str(startAngle) + " stopAngle=" + str(stopAngle))
			drawCircleArc(screen, pCenter, sCenter, scale, color, self.center, self.radius, startAngle, stopAngle,1)

def createPopulation(tablePoly, maxSize=20):
	origin = (0, 10)
	alpha = 0

	# TODO: donner plus de liberte
	firstPart = Line(origin, alpha, 175)
	firstPart.computePointOut()

	track = [firstPart]
	return toto(tablePoly, track, maxSize=maxSize)

def toto(tablePoly, track, segments = [], maxSize=20):
	if len(track) > maxSize:
		return []
	
	x1, y1 = track[0].pIn
	x2, y2 = track[-1].pOut
	dist = sqrt( (x2 - x1)**2 + (y2 - y1)**2 )
	# print(str(len(track)) + " dist: " + str(dist))
	
	if dist < 10:
		a1 = track[0].angleIn
		a2 = track[-1].angleOut
		angle = (a2 - a1) % 360
		# print("angle: " + str(angle))
		
		if angle == 0:
			return [track]
	elif dist > 4000:
		return []
	else:
		# print("track: " + str(track))
		segment = Segment(track[-1].pIn, track[-1].pOut)
		if(len(intersection(segment, tablePoly)) > 0):
			return []
		# print("segments: " + str(segments))
		# print("segment: " + str(segment))
		for s in segments[:-1]:
			# print("s: " + str(s))
			if(len(intersection(segment, s)) > 0):
				return []
		segments = segments + [segment]
	
	result = []
	for part in availableParts:
		if(part[1] == "LINE"):
			p = Line(track[-1].pOut, track[-1].angleOut, length = part[2])
			p.computePointOut()
			result += toto(tablePoly, track + [p], segments, maxSize)
		else:
			for d in ("left", "right"):
				p = Curve(track[-1].pOut, track[-1].angleOut, radius = part[2], angle = part[3], direction = d)
				p.computePointOut()
				result += toto(tablePoly, track + [p], segments, maxSize)
	return result

def drawTable(table, screen, pCenter, sCenter, scale, color):
	xCenter, yCenter = pCenter
	xSCenter, ySCenter = sCenter

	polygon = [(xSCenter + scale * (p[0] - xCenter), ySCenter - scale * (p[1]  - yCenter)) for p in table]
	pygame.draw.polygon(screen, green, polygon, width=1)

table = [(-500,0), (500, 0), (500, 1000), (-500, 1000)]
tablePoly = Polygon(*table)

population = createPopulation(tablePoly, 10)
print("Nombre de circuits valides : " + str(len(population)))


white = (255,255,255);
red = (255,0,0);
green = (0,255,0);
blue = (0,0,255);

pygame.init()
screen = pygame.display.set_mode((800,600), flags=pygame.RESIZABLE)

# random.choice([red, green, blue])
while True:

	# bContinue = True
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit(); exit();
		# if event.type == pygame.KEYUP:
			# if event.key == pygame.K_SPACE:
				# print("============")
				# bContinue = False
	# if bContinue: continue

	screen.fill(white);

	xMin = inf
	yMin = inf
	xMax = -inf
	yMax = -inf
	for parts in population:
		for p in parts:
			x1, y1 = p.pIn
			x2, y2 = p.pOut
			xMin = min(xMin, x1, x2)
			xMax = max(xMax, x1, x2)
			yMin = min(yMin, y1, y2)
			yMax = max(yMax, y1, y2)
	# print(str(xMin) + " " + str(yMin) + " " + str(xMax) + " " + str(yMax))
	width, height = screen.get_size()
	sCenter = (ceil(width / 2), ceil(height / 2))
	xScale = (width - 20) / (xMax - xMin)
	yScale = (height - 20) / (yMax - yMin)
	scale = min(xScale, yScale)
	xCenter = (xMin + xMax) / 2
	yCenter = (yMin + yMax) / 2
	pCenter = (xCenter, yCenter)
	# print(str(screen.get_size()) + " " + str(scale) + " " + str(sCenter) + " " + str(pCenter))
	for parts in population:
		for p in parts:
			p.draw(screen, pCenter, sCenter, scale, blue)
	# parts = random.choice(population)
	# for p in parts:
		# p.draw(screen, pCenter, sCenter, scale, blue)

	drawTable(table, screen, pCenter, sCenter, scale, green)

	pygame.display.update()
	# pygame.time.wait(1000)
