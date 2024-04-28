#!/usr/bin/env python
# Written by Liam Jackson based on code by  Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain
import time
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
DEBUG = 1

# change these as desired
clockpin = 22
misopin = 24
mosipin = 25
cspin = 23
holdpin = 27
wppin = 26


# read SPI data from chip
# cmd hex command to send
# cmdlen number of bits in cmd
# readlen number of bits to read back
# sleeptime time to sleep between write & read
def spicmd(cmd, cmdlen, readlen, sleeptime=0):
    GPIO.output(cspin, True)
    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low

    if(cmdlen != 0):
        commandout = cmd
        for i in range(cmdlen):
            if (commandout & (1 << (cmdlen - 1))):
                GPIO.output(mosipin, True)
            else:
                GPIO.output(mosipin, False)

            commandout <<= 1
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)
    #end if cmdlen != 0

    if(sleeptime != 0):
        time.sleep(sleeptime)

    chipout = 0
    if(readlen != 0):
        # read in bits on clk high
        for i in range(readlen):
            GPIO.output(clockpin, True)
            chipout <<= 1
            if (GPIO.input(misopin)):
                chipout |= 0x1
            GPIO.output(clockpin, False)
    #end if readlen != 0

    GPIO.output(cspin, True) # bring CS high to end
    return chipout
#end function

# set up the SPI interface pins
GPIO.setup(mosipin, GPIO.OUT)
GPIO.setup(misopin, GPIO.IN)
GPIO.setup(clockpin, GPIO.OUT)
GPIO.setup(cspin, GPIO.OUT)

#Shouldn't need to set these up for now.
#GPIO.setup(SPIHOLD, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(SPIWP, GPIO.IN, pull_up_down=GPIO.PUD_UP)


#Read the ID/wakeup register
value = spicmd(0xAB, 8, 64, 0.5)

if((value & 0xff) != ((value >> 8)& 0xff)):
        print ("Chip ID read didn't go well")

id = value & 0xff
print ("RES ID ", format(id, '02x'))

if((id < 0x01) or (id > 0x40)):
    print ("ID is suspect, perhaps comms not working?")

time.sleep(0.5)
#Read the ID/wakeup register
value = spicmd(0x9F, 8, 24, 0.5)


id = value & 0xff
print ("RDID MFG id", format(id, '02x'))
did = value >> 8
print ("RDID Device id", format(did, '04x'))

time.sleep(0.5)


# read the status register
sreg1 = spicmd(0x05, 8, 8)  
print ("RDSR Status reg ", format(sreg1, '02x'))
if(sreg1 & 0x40):
    print ("QE Enabled!")
else:
    print ("QE Disabled!")


sreg2 = spicmd(0x15, 8, 8)  
print ("RDCR config reg ", format(sreg2, '02x'))

#verify
sreg2b = spicmd(0x15, 8, 8)  
if(sreg2 != sreg2b):
    print ("Veritication of RDCR config register failed!")
    print ("RDCR config reg", format(sreg2b, '02x'))




# hang out and do nothing for a half second
time.sleep(0.5)
GPIO.cleanup()
print ("Done!")
