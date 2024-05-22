from threading import Thread
class Custom_Thread(Thread):
    def __init__(self,callback1,arg1,callback2,arg2):
        Thread.__init__(self)
        self.callback1=callback1
        self.callback2=callback2
        self.arg1=arg1
        self.arg2=arg2
    
    def run(self):
        cb1_failed = self.callback1(self.arg1)
        if not cb1_failed:
            self.callback2(self.arg2)