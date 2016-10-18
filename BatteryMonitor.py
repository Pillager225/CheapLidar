#!/usr/bin/env python

from ADCCommunicator import ADCCommunicator
import subprocess
import time
import sys

# 5v is 188, danger zone below 195

class BatteryMonitor:
	adc = None

	def __init__(self):
		self.adc = ADCCommunicator()
		self.main()

	def main(self):
		while(True): 
			bat = self.adc.askADC(1)
			if bat <= 195:
				subprocess.call(['sudo', 'shutdown', '-h', 'now'])
				sys.exit(0)	
			time.sleep(5)
		
if __name__ == '__main__':
	bc = BatteryMonitor()
