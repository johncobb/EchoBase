import threading
import time
import Queue
import socket
import sys
from cpdefs import CpDefs
from datetime import datetime
#import Adafruit_BBIO.UART as UART
#import Adafruit_BBIO.GPIO as GPIO

class CpInetResultCode:
    RESULT_UNKNOWN = 0
    RESULT_OK = 1
    RESULT_ERROR = 2
    RESULT_CONNECT = 3
    RESULT_TIMEOUT = 4
    
class CpInetResponses:
    TOKEN_HTTPOK = "HTTP/1.1 200 OK"
    TOKEN_HTTPERROR = "ERROR"
    TOKEN_HTTPCONNECT = "CONNECT"
    
      
    
class CpInetDefs:
    
    INET_HOST = 'appserver05.cphandheld.com'
    INET_PORT = 1337
    INET_ROUTE = "/pings"
    INET_HTTPPOST = "POST %s HTTP/1.1\r\ncontent-type:application/json\r\nhost: %s\r\ncontent-length:%d\r\n\r\n%s"


class CpInetResult:
    ResultCode = 0
    Data = ""
    
    
class CpInet(threading.Thread):
    
    def __init__(self, inetResponseCallbackFunc=None, *args):
        self._target = self.inet_handler
        self._args = args
        self.__lock = threading.Lock()
        self.closing = False # A flag to indicate thread shutdown
        self.commands = Queue.Queue(5)
        self.data_buffer = Queue.Queue(128)
        self.inet_timeout = 0
        self.inetResponseCallbackFunc = inetResponseCallbackFunc
        self.inetBusy = False
        self.inetResult = CpInetResult()
        self.inetToken = ""
        self.host = CpInetDefs.INET_HOST
        self.port = CpInetDefs.INET_PORT
        self.route = CpInetDefs.INET_ROUTE
        self.sock = None
        self.remoteIp = None
        self.init_socket()
        #self.data_buffer = ""
        threading.Thread.__init__(self)
    
    def init_socket(self):
        '''
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print 'Failed to create socket'
            return 0
        '''
        try:
            self.remoteIp = socket.gethostbyname(self.host)
            print "RemoteIp %s" % self.remoteIp
        except socket.gaierror:
            print 'Hostname could not be resolved. Exiting'
            return 0
            #sys.exit()
        
    
    def run(self):
        self._target(*self._args)
        
    def shutdown_thread(self):
        print 'shutting down CpInet...'
        self.__lock.acquire()
        self.closing = True
        self.__lock.release()
    
    def inet_send(self, packet):
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print 'Failed to create socket'
            return 0
        
        postData = CpInetDefs.INET_HTTPPOST % (CpInetDefs.INET_ROUTE, CpInetDefs.INET_HOST, len(packet), packet)
        print "RemoteIp %s" % self.remoteIp
        print "Port %d" % self.port
        
        self.sock.connect((self.remoteIp, self.port))

        print 'sending inet data ', postData
        
        try:
            byteCount = self.sock.send(postData)
        except socket.error:
            print 'Send failed'
        
        print 'Packet sent successfully %d' % byteCount    
        reply = self.sock.recv(4096)
        
        print 'Server reply: %s' % reply
        
        result = CpInetResultCode()
        
        result = self.inet_parse_result(reply)
        
        if (result.ResultCode == CpInetResultCode.RESULT_OK):
            print 'ResultCode=CpInetResultCode.RESULT_OK'
        elif (result.ResultCode == CpInetResultCode.RESULT_ERROR):
            print 'ResultCode=CpInetResultCode.RESULT_ERROR'
        else:
            print 'ResultCode=CpInetResultCode.RESULT_UNKNOWN'
            
        
        
            
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        
    
    
    def inet_handler(self):
        tmp_buffer = ""
        
        while not self.closing:
            
            if (self.commands.qsize() > 0):
                print 'Command found'
                packet = self.commands.get(True)
                self.commands.task_done()
                self.inet_send(packet)
                continue
            
            
            time.sleep(2)

                    
    def enqueue_packet(self, packet):
        try:
            #self.inetBusy = True
            self.commands.put(packet, block=True, timeout=1)
        except:
            self.__lock.acquire()
            print "The Rf queue is full"
            self.__release()

    def set_timeout(self, timeout):
        self.inet_timeout = datetime.now() + timeout
    
    def is_timeout(self):
        if(datetime.now() >= self.rf_timeout):
            return True
        else:
            return False
    '''
    def is_error(self, token):        
        if(token.find(CpInetResponses.TOKEN_HTTPERROR) > -1):
            return True
        else:
            return False
    '''
        
    def inet_parse_result(self, result):
        
        inet_result = CpInetResult()
        
        if(result.find(CpInetResponses.TOKEN_HTTPOK) > -1):
            inet_result.Data = result
            inet_result.ResultCode = CpInetResultCode.RESULT_OK
        elif(result.find(CpInetResponses.TOKEN_HTTPERROR) > -1):
            inet_result.Data = result
            inet_result.ResultCode = CpInetResultCode.RESULT_ERROR
        else:
            inet_result.Data = result
            inet_result.ResultCode = CpInetResultCode.RESULT_UNKNOWN
                
        return inet_result
            
