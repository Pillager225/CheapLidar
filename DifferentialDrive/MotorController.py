#!/usr/bin/env python

# This file was created by Ryan Cooper in 2016 for a Raspberry Pi
# This class controls the motors for the robot which are configured as 
# a differential drive
import RPi.GPIO as GPIO
import time
import sys

from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Pipe

class MotorController(Process):
	LEFT = 0
	RIGHT = 1

	pwmPin = [38, 37]
	# assuming you're using a L298n and a rpi
	dirPin = [[31,32], [35,33]]

	pwmObj = [None, None]
	# flag for motors pwmObj is started
	pwmStarted = [False, False]
	freq = 60#Hertz
	maxDC = 100
	minDC = 25
	mPowers = [0, 0]
	direction = [0, 0]	# forward or backward
	# set by time.time(), used to stop bot when dced
	lastQueue = 0
	go = True
	# only consumes the queue
	encQueue = None
	controllerQueue = None
	# used to shut the process down
	pipe = None

	def __init__(self, *args, **kwargs):
		super(MotorController, self).__init__()
		for key in kwargs:
			if key == 'encQueue':
				self.encQueue = kwargs[key]
			elif key == 'pipe':
				self.pipe = kwargs[key]
			elif key == 'controllerQueue':
				self.controllerQueue = kwargs[key]
		self.setupPins()
		self.initializePWM()

	def setupPins(self):
		GPIO.setmode(GPIO.BOARD)
		GPIO.setwarnings(False)
		for i in range(0, 2):
			GPIO.setup(self.pwmPin[i], GPIO.OUT)
			for j in range(0, 2):
				GPIO.setup(self.dirPin[j][i], GPIO.OUT)

	def initializePWM(self):
		for i in range(0 ,2):
			self.setDirections()
		for i in range(0, 2):
			self.pwmObj[i] = GPIO.PWM(self.pwmPin[i], self.freq)
			self.pwmStarted[i] = False

	def setDirections(self):
		for i in range(0, 2):
			if self.direction[i]:
				GPIO.output(self.dirPin[i][0], GPIO.HIGH)
				GPIO.output(self.dirPin[i][1], GPIO.LOW)
			else:
				GPIO.output(self.dirPin[i][0], GPIO.LOW)
				GPIO.output(self.dirPin[i][1], GPIO.HIGH)

	def clampToRange(self, x, lower, upper):
		if x < lower:
			return lower
		elif x > upper:
			return upper
		else:
			return x

	def setDC(self):
		for i in range(0 ,2):
			self.setDirections()
		for i in range(0, 2):
			if self.mPowers[i] == 0:
				self.pwmObj[i].stop()
				self.pwmStarted[i] = False
			else:
				if self.pwmStarted[i]:
					self.pwmObj[i].ChangeDutyCycle(self.mPowers[i])
				else:
					self.pwmObj[i].start(self.mPowers[i])
					self.pwmStarted[i] = True

	# maps x which is in the range of in_min to in_max to x's corresponding
        # value between out_min and out_max
        def transform(self, x, in_min, in_max, out_min, out_max):
            return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


	def endGracefully(self):
		for i in range(0, 2):
			if self.pwmObj[i]:
				self.pwmObj[i].ChangeDutyCycle(0)
				self.pwmObj[i].stop()
		GPIO.cleanup()
		self.go = False

	def handleQueues(self):
		if time.time()-self.lastQueue > .5 and self.controllerQueue.empty():
			self.direction = [0, 0]
			self.mPowers = [0, 0]
			self.lastQueue = time.time()
		else:
			while not self.controllerQueue.empty():
				good = True
				try:
					data = self.controllerQueue.get_nowait()
				except Queue.Empty as msg:
					good = False
				if good:
					if data[0] == 1: # recieved motor level commands
						mL = data[1]
						mR = data[2]
						if mL > 1500:
							self.direction[self.LEFT] = 1
							self.mPowers[self.LEFT] = self.clampToRange(self.transform(mL, 1500, 2000, 0, 100), 0, self.maxDC)
						else:
							self.direction[self.LEFT] = 0
							self.mPowers[self.LEFT] = self.clampToRange(self.transform(mL, 1500, 1000, 0, 100), 0, self.maxDC)
						if self.mPowers[self.LEFT] < self.minDC:
							self.mPowers[self.LEFT] = 0
						if mR > 1500:
							self.direction[self.RIGHT] = 0
							self.mPowers[self.RIGHT] = self.clampToRange(self.transform(mR, 1500, 2000, 0, 100), 0, self.maxDC)
						else :
							self.direction[self.RIGHT] = 1
							self.mPowers[self.RIGHT] = self.clampToRange(self.transform(mR, 1500, 1000, 0, 100), 0, self.maxDC)
						if self.mPowers[self.RIGHT] < self.minDC:
							self.mPowers[self.RIGHT] = 0
					elif data[0] == 2: # recieved joystick information (throttle, steering)
						pass
				self.lastQueue = time.time()

	def checkIfShouldStop(self):
		if self.pipe.poll():
			data = self.pipe.recv()
			if 'stop' in data:
				self.go = False
				self.pipe.close()

	def run(self):
		self.go = True
		try:
			while self.go:
			#	print self.mPowers
			#	print self.direction
				self.handleQueues()
				self.setDC()
				#TODO handle queue info which has encoder stuff in it
				self.checkIfShouldStop()
				time.sleep(.01)
			self.endGracefully()
		except Exception as msg:
			print msg
