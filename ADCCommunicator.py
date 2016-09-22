#!/usr/bin/env python
# based on code found at https://gist.github.com/HeinrichHartmann/27f33798d12317575c6c
#
# Analog Input with ADC0832 chip, on a breakout board found https://www.amazon.com/gp/product/B013SMDGNY
#
# Datasheet: http://www.ti.com/lit/ds/symlink/adc0838-n.pdf

import time
import os
import RPi.GPIO as GPIO

class ADCCommunicator:
        PIN_CLK = 18
        PIN_IO  = 22
        PIN_CS  = 17

        def init(self):
                GPIO.setmode(GPIO.BCM)
                # set up the SPI interface pins
                GPIO.setup(self.PIN_CLK, GPIO.OUT)
                GPIO.setup(self.PIN_CS,  GPIO.OUT, initial=GPIO.HIGH)

        # read SPI data from ADC8032
        def askADC(self, channel):
        	# 1. CS LOW.
                GPIO.output(self.PIN_CS, GPIO.LOW)     # bring CS low

        	# 2. Start cloc
                GPIO.output(self.PIN_CLK, GPIO.LOW)  # start clock low

        	# 3. Input MUX address
                func = GPIO.gpio_function(self.PIN_IO)
                if(func != GPIO.OUT):
                        if(func != GPIO.UNKNOWN):
                                GPIO.cleanup(self.PIN_IO)
                        GPIO.setup(self.PIN_IO, GPIO.OUT)
                for i in [1,1,channel]: # start bit + mux assignment
                        if (i == 1):
                                GPIO.output(self.PIN_IO, GPIO.HIGH)
                        else:
                                GPIO.output(self.PIN_IO, GPIO.LOW)
                        GPIO.output(self.PIN_CLK, GPIO.HIGH)
                        GPIO.output(self.PIN_CLK, GPIO.LOW)

                # 4. read 8 ADC bits
                ad = 0
                GPIO.cleanup(self.PIN_IO) # self.PIN_IO is setup to be GPIO.OUT right now
                GPIO.setup(self.PIN_IO, GPIO.IN)
                for i in range(8):
                        GPIO.output(self.PIN_CLK, GPIO.HIGH)
                        GPIO.output(self.PIN_CLK, GPIO.LOW)
                        ad <<= 1 # shift bit
                        if (GPIO.input(self.PIN_IO)):
                                ad |= 0x1 # set first bit

                # 5. reset
                GPIO.output(self.PIN_CS, GPIO.HIGH)

                return ad

        def cleanup(self):
                GPIO.cleanup()

if __name__ == "__main__":
        a = ADCCommunicator()
        while True:
                print "ADC[0]: {}\t ADC[1]: {}".format(a.askADC(0), a.askADC(1))
                time.sleep(1)