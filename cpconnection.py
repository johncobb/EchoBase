
import threading
import time
import Queue

class CpConnection(threading.Thread):
    

    
    
    def __init__(self, *args):
        self._target = self.connection_handler
        self._args = args
        self.__lock = threading.Lock()
        self.closing = False # A flag to indicate thread shutdown
        #self.taskMgr = taskMgr
        #self.modem = modem
        threading.Thread.__init__(self)
        self.state_func = {}
        self.func_index = 0
        self.func_timeout = 0
        self.init_functions()
        self.STATEFUNC = 0
        
    def run(self):
        self._target(*self._args)
    
    def shutdown_thread(self):
        print 'shutting down CpConsole...'
        self.taskMgr.shutdown_thread()
        self.modem.shutdown_thread()
        
        while(self.taskMgr.isAlive()):
            print 'waiting for CpTaskManager shutdown isAlive=', self.taskMgr.isAlive()
            time.sleep(.5)
        while(self.modem.isAlive()):
            print 'waiting for CpModem shutdown isAlive=', self.modem.isAlive()
            time.sleep(.5)
        
        print 'waiting for CpTaskManager shutdown isAlive=', self.taskMgr.isAlive()
        print 'waiting for CpModem shutdown isAlive=', self.modem.isAlive()
        self.__lock.acquire()
        self.closing = True
        self.__lock.release()
        
    def connection_handler(self):
        
        self.connection_enter_state(self.connect, 5)
        while not self.closing:
            '''
            self.state_func[self.func_index]()
            time.sleep(.5)
            self.func_index +=1
            
            if(self.func_index >= 2):
                self.func_index = 0
            '''
            
            self.STATEFUNC()
            time.sleep(self.func_timeout)
            time.sleep(.0001)
            
                
                
    def connection_enter_state(self, new_state_func, timeout):
        self.STATEFUNC = new_state_func
        self.func_timeout = timeout
        
        
            

    

                    
    def init_functions(self):
        self.state_func = { 0:self.connect, 1:self.disconnect}
        
    
    def connect(self):
        print 'connect called'
    def disconnect(self):
        print 'disconnect called'

        
        
    
if __name__ == '__main__':

    connectThread = CpConnection()
    connectThread.start()