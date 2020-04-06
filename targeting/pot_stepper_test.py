from gpiozero import MCP3008
import time
import RPi.GPIO as GPIO
import numpy as np
import math
import sys

xPot = MCP3008(channel=1)
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

time = 0.00075
scale = 0.2

x_pins = [18, 23, 24, 25]
y_pins = [17, 27, 22, 4]

for pin in x_pins:
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, False)

for pin in y_pins:
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, False)

StepCount1 = 8

Seq = [[],[],[],[],[],[],[],[]]
#Seq = range(0, StepCount1)
Seq[0] = [1, 0, 0, 0]
Seq[1] = [1, 1, 0, 0]
Seq[2] = [0, 1, 0, 0]
Seq[3] = [0, 1, 1, 0]
Seq[4] = [0, 0, 1, 0]
Seq[5] = [0, 0, 1, 1]
Seq[6] = [0, 0, 0, 1]
Seq[7] = [1, 0, 0, 1]

nSteps = range(0, 2)

def findDirection(difference):
    #positive difference means go negative direction
	if (difference > 0):
		return 2
    #negative difference means go positive direction
	elif (difference < 0):
        return 1
    #no difference means don't move
    else:
        return 0

def takeStep(motor, direction, seqStep):
	if (motor == 1):
        # y motor
		for pin in range(0, 4):
			xpin = y_pins[pin]
			if Seq[seqStep][pin] != 0:
				GPIO.output(xpin, True)
			else:
				GPIO.output(xpin, False)
	elif (motor == 2):
        # x motor
		for pin in range(0,4):
			xpin = x_pins[pin]
			if Seq[seqStep][pin] != 0:
				GPIO.output(xpin, True)
			else:
				GPIO.output(xpin, False)
	sleep(time)

    # move in the positive direction
	if(direction == 1):
		if (seqStep == 7):
			return 0
		else:
			return seqStep + 1
    
    # move in the negative direction
	elif:
		if (seqStep == 0):
			return 7
		else:
			return seqStep - 1

    # if direction = 0, then don't move that motor
    else:
        pass


def main():
    # right now we're only moving the x motor, will add y motor once this works

    # CHANGE THESE POTENTIOMETER VALUES TO GO TOWARDS THAT VALUE
    xPotGoal = .5
    #yPotVal = .5

    # keeps track of where the x motor is in its stepper sequence
    seqStepX = 0

    # current value - goal value
    xDiff = xPot.value - xPotGoal

        # +/- .005 is the tolerance for now, can be changed to better fit the potentiometers
        while (xDiff < .005 and xDiff > -.005):
            seqStepX = takeStep(2, findDirection(xDiff), seqStepX)
            xDiff = xPot.value - xPotGoal

        print("x Pot Goal: ",xPotGoal,'\n', "current x Pot value: ",xPot.value)

if __name__ == "__main__":
	main()



