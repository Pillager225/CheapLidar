#!/usr/bin/env python

from ADCCommunicator import ADCCommunicator
import subprocess
import time
import sys

# 5v is 188, danger zone below 195

class BatteryMonitor:
	adc = None
	qSize = 5
	batVals = [-1]*qSize
	batValIndex = 0

	def __init__(self):
		self.adc = ADCCommunicator()
		self.main()

	def getAverageBatVal(self):
		ave = 0
		i = 0
		for i in range(0, qSize):
			if self.batVals[i] == -1:
				break
			else:
				ave += self.batVals[i]
		if i < 3:
			return -1
		else:
			return ave/(i+1)

	def main(self):
		while(True): 
			self.batVals[self.batValIndex] = self.adc.askADC(1)
			self.batValIndex = (self.batValIndex+1)%self.qSize
			v = self.getAverageBatVal()
			if v != -1 and v <= 210:
				subprocess.call(['sudo', 'shutdown', '-h', 'now'])
				sys.exit(0)	
			time.sleep(5)
		
if __name__ == '__main__':
	bc = BatteryMonitor()
