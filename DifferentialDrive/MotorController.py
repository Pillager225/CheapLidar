#!/usr/bin/env python

# This file was created by Ryan Cooper in 2016
# This class controls the motors for the robot which are configured as 
# a differential drive
import RPi.GPIO as GPIO
import time
import sys

class MotorController:
	LEFT = 0
	RIGHT = 1

	pwmPin = [38, 37]
	dirPin = [[31,32], [35,33]]

	pwmObj = [None, None]
	# flag for motors pwmObj is started
	pwmStarted = [False, False]
	freq = 60#Hertz
	maxDC = 100
	minDC = 10
	mPowers = [0, 0]
	direction = [0, 0]	# forward or backward

	go = True

	def __init__(self):
		self.setupPins()
		self.initializePWM()

	def setupPins(self):
		GPIO.setmode(GPIO.BOARD)
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

	# 0 <= power <= 255
	def setDCByPower(self, power):
		for i in range(0 ,2):
			self.setDirections()
		for i in range(0, 2):
			if power[i] == 0:
				self.pwmObj[i].stop()
				self.pwmStarted[i] = False
			else:
				if self.pwmStarted[i]:
					self.pwmObj[i].ChangeDutyCycle(self.clampToRange(self.transform(power[i], 0, 255, self.minDC, self.maxDC), self.minDC, self.maxDC))
				else:
					self.pwmObj[i].start(self.clampToRange(self.transform(power[i], 0, 255, self.minDC, self.maxDC), self.minDC, self.maxDC))
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

	def main(self):
		try:
			while self.go:
			#	print self.mPowers
			#	print self.direction
				self.setDCByPower(self.mPowers)
				time.sleep(.1)
			self.endGracefully()
		except Exception as msg:
			print msg
