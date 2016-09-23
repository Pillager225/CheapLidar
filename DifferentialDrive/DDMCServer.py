
#DDMC=Differential Drive Motor Control

# This file was created by Ryan Cooper in 2016
# This class starts a server to listen to an xbox controller which is plugged into a 
# client computer that can connect to the robot
import socket
import time
import struct
import sys

from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Pipe

class DDMCServer(Process):
	serversocket = None 
	clientsocket = None
	motorController = None			# This should be set by RoboSunia.shareClasses()
	# sends motor control signals to motor controller
	driverQueue = None
	# sused to shut the process down
	pipe = None
	go = True

	def __init__(self, *args, **kwargs):
		super(DDMCServer, self).__init__()
		for key in kwargs:
			if key == 'queue':
				self.driverQueue = kwargs[key]
			elif key == 'pipe':
				self.pipe = kwargs[key]
		self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serversocket.bind(('', 12345))
		self.serversocket.listen(1)
		print "DDMC server started"

	def waitForConnection(self):
        	if self.clientsocket == None:
            		connected = False
            	while not connected:
                	try:
                    	    sys.stdout.write('Waiting for DDMCClient connection... ')
	                    sys.stdout.flush()
        	            (self.clientsocket, address) = self.serversocket.accept()
                	    connected = True
	                    print 'DDMC controller connected'
        	        except Exception as msg:
                	    print 'Client connection failed with message:'
	                    print msg
        	            print 'I will retry connecting in one second.'
                	    time.sleep(1)

	def resetClient(self, waitForReconnect = True):
	    	print "DDMC controller disconnected!"
	    	self.driverQueue.put([0,0,0,0,0])
	    	if(self.clientsocket != None):
	    		self.clientsocket.close()
    		self.clientsocket = None
    		if waitForReconnect:
    			self.waitForConnection()

    	def handleData(self):
		try:
    			data = self.clientsocket.recv(20)
			if len(data) == 0:
				self.resetClient()
			else:
				leftDir = struct.unpack('i', data[4:8])[0], # left motor dir
				leftDir = 0 if leftDir[0] == -1 else leftDir[0]
				leftPower = struct.unpack('i', data[8:12])[0], # left motor power
				leftPower = 0 if leftPower[0] == -1 else leftPower[0]
				rightDir = struct.unpack('i', data[12:16])[0]
				rightDir = 0 if rightDir == -1 else rightDir
				rightDir = 0 if rightDir == 1 else 1, # right motor dir
				rightPower = struct.unpack('i', data[16:20])[0] 	# right motor power
				rightPower = 0 if rightPower == -1 else rightPower
				self.driverQueue.put([
					struct.unpack('i', data[0:4])[0], # control scheme
					leftDir,
					leftPower,
					rightDir[0],
					rightPower])
					
		except Exception as msg:
			if "Errno 104" in msg:
				self.resetClient()
			else:
				print "DDMCServer"
				print msg

	def checkIfShouldStop(self):
		if self.pipe.poll():
			data = self.pipe.recv()
			if 'stop' in data:
				self.go = False
				self.pipe.close()

	def run(self):
		self.go = True
		self.waitForConnection()
		while self.go:
			self.handleData()
			self.checkIfShouldStop()
			time.sleep(.01)
    		self.closeConnections()

	def closeConnections(self):
		self.resetClient(False)
	    	if self.serversocket:
    			self.serversocket.close()

