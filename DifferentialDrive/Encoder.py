import RPi.GPIO as GPIO
import time
from multiprocessing import Process
from multiprocessing import Queue
#pin should be 11 or 12 #GPIO17,GPIO18

class Encoder(Process):
	pin = None 
	count = 0
	# will only put things into the queue
	driverQueue = None
	# used to shut the process down
	pipe = None
	go = True

	def __init__(self, *args, **kwargs):
		super(Encoder, self).__init__()
		for key in kwargs:
			if key == 'queue':
				self.driverQueue = kwargs[key]
			elif key == 'pipe':
				self.pipe = kwargs[key]
			elif key == 'pin':
				self.pin = kwargs[key]
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

	def checkIfShouldStop(self):
		if self.pipe.poll():
			data = self.pipe.recv()
			if 'stop' in data:
				self.go = False
				self.pipe.close()

	def run(self):
		self.go = True
		while self.go:
			starttime = time.clock()
			val = GPIO.wait_for_edge(self.pin, GPIO.BOTH, timeout=500)
			if val is None:		#Stall occured
				#TODO handle stall
				self.count = 0
			else:
				self.count += 1
			self.driverQueue.put([self.pin ,self.count, starttime-time.clock()])
			self.checkIfShouldStop()
		GPIO.cleanup()

if __name__ == '__main__':
	driver_queue = Queue()
	control_pipe, enc_pipe = Pipe()
	e = Encoder(queue=driver_queue, pipe=enc_pipe, pin=11)
	e.start()
