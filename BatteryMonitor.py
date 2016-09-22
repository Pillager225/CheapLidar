#!/usr/bin/env python

from ADCCommunicator import ADCCommunicator
import time

class BatteryMonitor:
	adc = None

	def __init__(self):
		self.adc = ADCCommunicator()
		self.main()

	def main(self):
		while(True): 
			bat = self.adc.askADC(1)
			print bat
			time.sleep(1)
		
		#TODO map voltages to adc values and monitor voltage so that if it dips too low, rpi will shut off

if __name__ == '__main__':
	bc = BatteryMonitor()
