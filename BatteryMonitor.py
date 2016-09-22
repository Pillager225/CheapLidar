#!/usr/bin/env python

from ADCCommunicator import ADCCommunicator

class BatteryMonitor:
	adc = None

	def init(self):
		self.adc = ADCCommunicator()
		self.main()

	def main(self):
		while(True) {
			bat = adc.askADC(1)
			print bat
		}
		#TODO map voltages to adc values and monitor voltage so that if it dips too low, rpi will shut off

if __name__ = "__main__":
	bc = BatteryMonitor()