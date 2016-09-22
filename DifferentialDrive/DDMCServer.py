
#DDMC=Differential Drive Motor Control

# This file was created by Ryan Cooper in 2016
# This class starts a server to listen to an xbox controller which is plugged into a 
# client computer that can connect to the robot
import socket
import time
import struct
import sys

class DDMCServer:
	serversocket = None 
	clientsocket = None
	motorController = None			# This should be set by RoboSunia.shareClasses()
	starter = None					# This shoudl be set by RoboSunia.shareClasses()
	go = True

	def __init__(self):
		self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
	    	motorController.mPowers[self.motorController.LEFT] = 0;
	    	motorController.mPowers[self.motorController.LEFT] = 0;
	    	if(self.clientSocket != None):
	    		self.clientSocket.close()
    		self.clientsocket = None
    		if waitForReconnect:
    			self.waitForConnection()

    	def main(self):
    		self.waitForConnection()
    		while self.go:
    			try:
    				data = self.clientsocket.recv(16)
    				if len(data) == 0:
    					self.resetClient()
					self.motorController.direction[self.motorController.LEFT] = struct.unpack('i', data[0:4])[0]
					self.motorController.mPowers[self.motorController.LEFT] = struct.unpack('i', data[4:8])[0]
					rightDirTemp = struct.unpack('i', data[8:12])[0]
					self.motorController.direction[self.motorController.RIGHT] = 0 if rightDirTemp == 1 else 1
					self.motorController.mPowers[self.motorController.RIGHT] = struct.unpack('i', data[12:16])[0]
			except Exception as msg:
				if "Errno 104" in msg:
					self.resetClient()	
				else:
					print msg
	    	self.closeConnections()

	def closeConnections(self):
			self.resetClient(False)
	    	if self.serversocket:
    			self.serversocket.close()

