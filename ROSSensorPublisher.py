import rospy
from sensor_msgs import LaserScan

class LaserScanProducer: #TODO make it its own process

	# CONSTANTS
	NUM_SAMPLES = 10 
	STEPS_PER_ROTATION = 64
	SECONDS_PER_ROTATION = 1.0

	adc = ADCCommunicator()
	stepperController = None	# passed in by starter TODO
	publisher = rospy.Publisher('scan', LaserScan, queue_size = 50)

	def init(self, stepperController):
		self.stepperController = stepperController
		rospy.init_node('laser_scan_publisher', anonymous = True)

	def produceLaserScan(self):
		scan = LaserScan()
		scan.header.stamp = rospy.Time.now()
		scan.header.frame_id = "laser_frame"
		scan.angle_min = 0.0
		scan.angle_max = 0.0
		# 5.625 deg/step = 0.0981747704246809 rad/step
		scan.angle_increment = 0.0981747704246809
		scan.time_increment = SECONDS_PER_ROTATION/STEPS_PER_ROTATION # TODO seconds
		scan.range_min = 0.0 # TODO
		scan.range_max = 100.0 # TODO
		scan.ranges = self.getLaserScanRanges()
		scan.intensities = list()
		self.publisher.publish(scan)

	def takeSensorReading(self): # TODO needs to convert adc signals to distance
		sensorAve = 0
		for i in range(0, self.NUM_SAMPLES):
			sensorAve += adc.askADC(0)
		return sensorAve/self.NUM_SAMPLES

	def convertReadingToDistance(self, reading):
		pass #TODO

	def getLaserScanRanges(self):
		ranges = list()
		for i in range(0, STEPS_PER_ROTATION):
			ranges.append(self.convertReadingToDistance(self.takeSensorReading()))
			self.stepperController.step()
		return ranges

	def run(self):
		rate = rospy.Rate(10) #Hertz TODO determine the right number to work with the scanner
		while not rospy.is_shutdown():
			self.produceLaserScan()
			rate.sleep()