import threading
from threading import Thread

class ReadThread(threading.Thread):
    class CallbackEvent:
        def __init__(self,event,callbackFunc):
            """The purpose of the class to group in together the event and the callable function into a pair. 
            
            Parameters
            ----------
            event : threading.Event/multiprocessing.Event
                The event to synchronize two thread or process.
            callbackFunc : callable
                The function which will be applied. It's usable in the multithread system.
            """
            self.event=event
            self.callbackFunc=callbackFunc

    def __init__(self,f_theadID,f_serialCon,f_fileHandler):
        """ The role of this thread is to receive the messages from the micro-controller and to redirectionate to the other processes or modules. 
        
        Parameters
        ----------
        f_theadID : int
            The ID number of the thread
        f_serialCon : serial.Serial
           The serial connection between the two device. 
        f_fileHandler : FileHandler
            The log file handler object for saving the received messages.
        """
        threading.Thread.__init__(self)
        self.ThreadID=f_theadID
        self.serialCon=f_serialCon
        self.fileHandler=f_fileHandler
        self.Run=False
        self.buff=""
        self.isResponse=False
        # self.printOut=f_printOut
        self.Responses=[]
        self.Waiters={}
        self.baudrate = baudrate
    
    def run(self):
        """ It's represent the activity of the read thread, to read the messages.
        """
        # print("Time sleep:",180/self.baudrate)
        
        while(self.Run):

            read_chr=self.serialCon.read()
            try:
                read_chr=(read_chr.decode("ascii"))
                if read_chr=='@':
                    self.isResponse=True
                    if len(self.buff)!=0:
                        self.checkWaiters(self.buff)
                    self.buff=""
                elif read_chr=='\r':
                    self.isResponse=False
                    if len(self.buff)!=0:
                        self.checkWaiters(self.buff)
                    self.buff=""
                if self.isResponse:
                    self.buff+=read_chr
                # self.fileHandler.write(read_chr)    
                # if self.printOut:
                #     sys.stdout.write(read_chr)
            except UnicodeDecodeError:
                pass
            
    def checkWaiters(self,f_response):
        """ Checking the list of the waiting object to redirectionate the message to them. 
        
        Parameters
        ----------
        f_response : string
            The response received from the other device without the key. 
        """
        l_key=f_response[1:5]
        if l_key in self.Waiters:
            l_waiters=self.Waiters[l_key]
            for eventCallback in l_waiters:
                eventCallback.event.set()
                if not eventCallback.callbackFunc==None:
                    eventCallback.callbackFunc(f_response[6:-2])

    def addWaiter(self,f_key,f_objEvent,callbackFunction=None):
        """Adding a new waiting object to the list. 
        
        Parameters
        ----------
        f_key : string
            The key of the message
        f_objEvent : threading.Event/multiprocessing.Event
            The event object to synchronize the two independent thread or process. 
        callbackFunction : callable, optional
            The callable function after the receiving message, by default None
        """
        l_evc=ReadThread.CallbackEvent(f_objEvent,callbackFunction)
        if f_key in self.Waiters:
            obj_events_a=self.Waiters[f_key]
            obj_events_a.append(l_evc)
        else:
            obj_events_a=[l_evc]
            self.Waiters[f_key]=obj_events_a

    def deleteWaiter(self,f_key,f_objEvent):
        """ To delete the waiting object from the list. 
        
        Parameters
        ----------
        f_key : string
            The key of the message
        f_objEvent : threading.Event/multiprocessing.Event
            The event object, which has role to synchronize the threads/ processes. 
        """
        if f_key in self.Waiters:
            l_obj_events_a=self.Waiters[f_key]
            for callbackEventObj in l_obj_events_a:
                if callbackEventObj.event==f_objEvent:
                    l_obj_events_a.remove(callbackEventObj)            

    def stop(self):
        """Stoping the thread
        """
        self.Run=False

    def start(self):
        """Starting the thread. 
        """
        self.Run=True
        super(ReadThread,self).start()