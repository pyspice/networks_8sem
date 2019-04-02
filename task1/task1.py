import sys
from multiprocessing import cpu_count
from time import time, sleep
from random import random, randint
from threading import Thread

class Station(Thread):
    '''
    Single CDMA/CD station
    
    Attributes:
        frameBuffer        Shared frame buffer
        frameTemplate      Default frame message template
        interframeGap      Minimal pause between network frames, in seconds
        isMediumIdle       True if no other station is transmitting, false otherwise
        maxAttemptCount    Max unsucessful transmission attempts count
        msgDelimeter       Trace message delimeter
    '''

    frameBuffer = ''
    frameTemplate = 'Station {}. Frame {}.\n'    
    interframeGap = 5e-1
    isMediumIdle = True
    maxAttemptCount = 15
    msgDelimeter = '-' * 20
    
    def __init__(self, name, frameCount):
        '''
        Station initialization
        '''
        
        Thread.__init__(self)
        
        self.name = name
        
        self.frameCount = frameCount
        self.transmittedCount = 0
        
        self.attemptNumber = 1
        
    def __str__(self):
        '''
        String representation of Station object
        '''
        
        return f'Station({self.name})'    
        
    def run(self):
        '''
        Station launch
        '''
        
        self.printMsg('Running started')
        
        while self.transmittedCount < self.frameCount:            
            while not Station.isMediumIdle:
                sleep(Station.interframeGap + random())
                
            self.printMsg(f'Starting transmission. Attempt {self.attemptNumber}')  
            Station.isMediumIdle = False              
            frame = Station.frameTemplate.format(self.name, self.transmittedCount)
            
            Station.frameBuffer = frame
            sleep(Station.interframeGap)
            
            if self.isCollisionDetected(frame):
                self.printMsg('Collision detected. Attempt {self.attemptNumber}')
                if self.attemptNumber > Station.maxAttemptCount:      
                    self.printMsg('Max unseccessful attempt count reached. Stop.')                    
                    break
                
                backoffPeriod = self.getBackoffPeriod()
                self.printMsg(f'Waiting for backoff period: {backoffPeriod}. Attempt {self.attemptNumber}')
                sleep(backoffPeriod)
                self.attemptNumber += 1
                
            else:
                self.transmittedCount += 1
                self.attemptNumber = 1
                Station.isMediumIdle = True
                self.printMsg('Transmission successful')
        
        self.printMsg('Running ended') 

    def getTransmittedCountMsg(self):
        return f'{self.transmittedCount} frames successfully transmitted'
  
    def getMsgDelimeter(self):
        return '-' * 20
 
    def printMsg(self, msg):
        print(f'''{Station.msgDelimeter}
        {self}
        Msg: {msg}
        Frames successfully transmitted: {self.transmittedCount}
        Timestamp: {time()}
        {Station.msgDelimeter}
        ''')    
  
    def isCollisionDetected(self, frame):
        return frame != Station.frameBuffer
    
    def getBackoffPeriod(self):
        return Station.interframeGap + 9.6e-6 * randint(0, 2 ** self.attemptNumber)
    
    
def runSession(stationCount):
    print('Starting session')
    
    stations = [Station(f'Apollo{i}', i + 1) for i in range(stationCount)]
    
    for station in stations:
        station.start()
        
    for station in stations:
        station.join()
        
    print('Session ended')
    
if __name__ == '__main__':
    argv = sys.argv
    usageMsg = '''
    Usage: python3 task1.py <stationCount>
    '''
    
    if len(argv) != 2:
        print(usageMsg)
        
    else:
        try:
            stationCount = int(argv[1])
            if (stationCount > cpu_count()):
                print('Station count is greater than CPU count')
            elif (stationCount < 1):
                print('Enter positive station count')
            else:
                runSession(stationCount)
        except ValueError:
            print('Station count is not a number')