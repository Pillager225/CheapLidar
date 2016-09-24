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
from multiprocessing import Pipe
from multiprocessing import Queue
from multiprocessing import Manager

from MotorController import MotorController
from DDMCServer import DDMCServer
from Encoder import Encoder

class DDStarter:
	# encQueue in makeClasses() is filled by both Lencoder and Rencoder, and is consumed by motorController
	#	the array in encQueue is of the form [pin, count, timeSinceLast]
	# controllerQueue in makeClasses is filled by DDMCServer, and is consumed by motorController
	#	commands in the queue come from a DDMCClient
	# a manager creates Queues that are safe to share between processes
	motorController = None
	# Differential Drive Motor Controller (DDMC)
	controlServer = None
	Lencoder = None
	Rencoder = None
	# pipes are used to terminate processes
	ePipeLeft = None
	ePipeRight = None
	motorPipe = None
	controllerPipe = None

	def __init__(self):
		self.makeClasses()
		self.startProcesses()
		# Catch SIGINT from ctrl-c when run interactively.
		signal.signal(signal.SIGINT, self.signal_handler)
		# Catch SIGTERM from kill when running as a daemon.
		signal.signal(signal.SIGTERM, self.signal_handler)
		# This thread of execution will sit here until a signal is caught
		signal.pause()

	def makeClasses(self):
		manager = Manager()
		self.ePipeLeft, eLeft = Pipe() 
		self.ePipeRight, eRight = Pipe()
		self.motorPipe, m = Pipe() 
		self.controllerPipe , c = Pipe()
		encQueue = manager.Queue()
		controllerQueue = manager.Queue()
		self.motorController = MotorController(encQueue=encQueue, controllerQueue=controllerQueue, pipe=m)
		self.controlServer = DDMCServer(queue=controllerQueue, pipe=c)
		self.Lencoder = Encoder(queue=encQueue, pin=11, pipe=eLeft)
		self.Rencoder = Encoder(queue=encQueue, pin=12, pipe=eRight)

	def startProcesses(self):
		self.Lencoder.start()
		self.Rencoder.start()
		self.motorController.start()
		self.controlServer.start()

	def signal_handler(self, signal, frame):
		self.exitGracefully()

	def exitGracefully(self):
		try:
			print "Program was asked to terminate."
			if self.motorController:
				self.motorPipe.send('stop')	
			if self.controlServer:
				self.controlServer.send('stop')
			if self.encoders[0]:
				self.ePipeLeft.send('stop')
			if self.encoders[1]:
				self.ePipeRight.send('stop')
			sys.stdout.write("Waiting for threads to exit...")
			sys.stdout.flush()
			self.motorController.join()
			self.controlServer.join()
			self.Lencoders.join()
			self.Rencoders.join()
			print "Done"
			sys.exit(0)
		except Exception as msg:
			print "An exception occured while trying to terminate"
			print msg
			sys.exit(1)

if '__main__' ==  __name__:
	r = DDStarter()
