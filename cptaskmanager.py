import threading
import time
import Queue
import json
import cpcobs

# 43 Byte message structure
#class AppMessage():
class AppMessage(object):
    def __init_(self):
        self.messageType = 0
        self.nodeType = 0
        self.shortAddr = 0
        self.softVersion = 0
        self.channelMask = 0
        self.panId = 0
        self.workingChannel = 0
        self.parentShortAddr = 0
        self.lqi = 0
        self.rssi = 0
        self.type = 0
        self.size = 0
        self.battery = 0
        self.temperature = 0
        self.light = 0
        self.cs = 0
        
# http://stackoverflow.com/questions/1458450/python-serializable-objects-json    
# See also YAML    
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, AppMessage):
            return super(MyEncoder, self).default(obj)
        
        return obj.__dict__

def dataReceived(rf_data):
    pass

def checksum(data):
    cs = 0x00
    
    sentence = data[:-1]
    print 'sentence: ', sentence.encode('hex')
    for s in sentence:
        cs ^= ord(s)
    print 'checksum', cs
    return cs
    

def checksumValid(data):
    cs = checksum(data)
    return (ord(data[len(data)-1]) == cs)
    
class CpTaskManager(threading.Thread):

    def __init__(self, rfThread, inetThread, *args):
        self._target = self.task_handler
        self._args = args
        self.__lock = threading.Lock()
        self.jobs = Queue.Queue(5)
        self.closing = False # A flag to indicate thread shutdown
        self.rfThread = rfThread
        self.inetThread = inetThread
        threading.Thread.__init__(self)
        
    def run(self):
        self._target(*self._args)
        
    def task_handler(self):
        while not self.closing:
            rf_data = self.rfThread.queue_get()
            time.sleep(.0001)
            
            if(len(rf_data) == 43):
            
                data = cpcobs.decode(rf_data)
    
                if (checksumValid(data) == False):
                    print 'Invalid Checksum'
                    continue
                print 'Queued Message Received!!!'
                msg = AppMessage()
                msg.messageType = ord(data[0])
                msg.nodeType = ord(data[1])
                msg.extAddr = (ord(data[2])) + (ord(data[3])<<8) + (ord(data[4])<<16) + (ord(data[5])<<24) + (ord(data[6])<<32) + (ord(data[7])<<40) + (ord(data[8])<<48) + (ord(data[9])<<56)
                msg.shortAddr = (ord(data[10])) + (ord(data[11])<<8)
                msg.softVersion = (ord(data[12])) + (ord(data[13])<<8) + (ord(data[14])<<16) + (ord(data[15])<<24)
                msg.channelMask = (ord(data[16])) + (ord(data[17])<<8) + (ord(data[18])<<16) + (ord(data[19])<<24)
                msg.panId = (ord(data[20])) + (ord(data[21])<<8)
                msg.workingChannel = ord(data[22])
                msg.parentShortAddr = (ord(data[23])) + (ord(data[24])<<8)
                msg.lqi = ord(data[25])
                msg.rssi = ord(data[26])
                msg.type = ord(data[27])
                msg.size = ord(data[28])
                msg.battery = (ord(data[29])) + (ord(data[30])<<8) + (ord(data[31])<<16) + (ord(data[32])<<24)
                msg.temperature = (ord(data[33])) + (ord(data[34])<<8) + (ord(data[35])<<16) + (ord(data[36])<<24)
                msg.light = (ord(data[37])) + (ord(data[38])<<8) + (ord(data[39])<<16) + (ord(data[40])<<24)
                
                packet = json.dumps(msg, cls=MyEncoder)
                self.inetThread.enqueue_packet(packet)
                
        time.sleep(1)
        
    def enqueue_command(self, cmd):
        try:
            self.jobs.put(cmd, block=True, timeout=1)
        except:
            self.__lock.acquire()
            print "The queue is full"
            self.__release()
            
    def shutdown_thread(self):
        print 'shutting down CpTaskManager...'
        self.__lock.acquire()
        self.closing = True
        self.__lock.release()