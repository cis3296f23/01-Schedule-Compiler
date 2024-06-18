from threading import Thread
class Custom_Thread(Thread):
    def __init__(self,callback1,callback2):
        Thread.__init__(self)
        self.callback1=callback1
        self.callback2=callback2
    
    def run(self):
        cb1_res = self.callback1()
        if cb1_res:
            self.callback2(cb1_res)