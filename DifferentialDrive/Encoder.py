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
	pSize = 10
	periods = [-1.0]*pSize
	periodIndex = 0
	diameterOfWheel = 65.087 # millimeters
	circumferenceOfWheel = 204.476841044199 # millimeters
	stateChangesPerRevolution = 40 # there are 20 slots, but 40 state changes

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

	def resetPeriod(self):
		self.periods = [0]*10
		self.periodIndex = 0

	def getAveragePeriodBetweenBlips(self):
		ave = 0.0
		for i in range(0, pSize):
			if periods[i] == -1:
				break
			else:
				ave += periods[i]
		return ave/pSize

	def testingCode(self):
		GPIO.setmode(GPIO.BOARD)
		GPIO.setwarnings(False)
		GPIO.setup(31, GPIO.OUT)
		GPIO.setup(32, GPIO.OUT)
		GPIO.setup(38, GPIO.OUT)
		GPIO.output(31, GPIO.LOW)
		GPIO.output(32, GPIO.HIGH)
		pwmObj = GPIO.PWM(38, 60)
		pwmObj.start(50)

	def run(self):
		self.go = True
		while self.go:
			starttime = time.time()
			val = GPIO.wait_for_edge(self.pin, GPIO.BOTH, timeout=500)
			if val is None:		#Stall occured
				#TODO handle stall
				self.count = 0
			else:
				self.count += 1
			periods[periodIndex] = time.time()-starttime
			if periodIndex+1 == pSize:
				periodIndex = 0
			else:
				periodIndex += 1
			self.driverQueue.put([self.pin ,self.count, self.getAveragePeriodBetweenBlips()])
			self.checkIfShouldStop()
		GPIO.cleanup()

if __name__ == '__main__':
	driver_queue = Queue()
	control_pipe, enc_pipe = Pipe()
	e = Encoder(queue=driver_queue, pipe=enc_pipe, pin=11)
	e.testingCode()
	e.start()
	while True:
		while not driver_queue.empty():
			good = True
			try: 
				data = driver_queue.get()
			except Queue.Empty as msg:
				# realistically this should never happen because we check to see that the queue is not empty
				# but it is shared memory, and who knows?
				good = False
			if good:
				print data