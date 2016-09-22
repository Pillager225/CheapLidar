#!/usr/bin/env python 

# This file was created by Ryan Cooper in 2016
# to control a raspberry pi that is hooked up to motor controls
# that control motors that create a differential drive
# it can be controlled by keyboard or by an controlServer controller (possibly any HCI controller)
import RPi.GPIO as GPIO
import time
import thread
import signal
import sys

from MotorController import MotorController
from DDMCServer import DDMCServer

class DDStarter:
	# class that controls motors
	motorController = None
	controlServer = None

	def __init__(self):
		self.makeClasses()
		self.shareClasses()
		self.startThreads()
		# Catch SIGINT from ctrl-c when run interactively.
		signal.signal(signal.SIGINT, self.signal_handler)
		# Catch SIGTERM from kill when running as a daemon.
		signal.signal(signal.SIGTERM, self.signal_handler)
		# This thread of execution will sit here until a signal is caught
		signal.pause()

	def makeClasses(self):
		self.motorController = MotorController()
		self.controlServer = DDMCServer()

	def shareClasses(self):
		self.controlServer.motorController = self.motorController
		self.controlServer.starter = self

	def startThreads(self):
		thread.start_new_thread(self.motorController.main, ())
		thread.start_new_thread(self.controlServer.main, ())
		
	def signal_handler(self, signal, frame):
		self.exitGracefully()

	def exitGracefully(self):
		try:
			print "Program was asked to terminate."
			if self.motorController:
				self.motorController.go = False	
			if self.controlServer:
				self.controlServer.go = False
			sys.stdout.write("Waiting for threads to exit...")
			sys.stdout.flush()
			time.sleep(1)
			print "Done"
			sys.exit(0)
		except Exception as msg:
			print "An exception occured while trying to terminate"
			print msg
			sys.exit(1)

if '__main__' ==  __name__:
	r = DDStarter()
