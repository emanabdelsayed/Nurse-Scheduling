from tkinter import *
import Prob
import numpy as np

def getspline(x1,y1,x2,y2,r):
    a = (x1,y1)
    b = (x2,y1) 
    c = (x2,y2)
    d = (x1,y2)

    a1,d2=(x1+r,y1),(x1,y1+r)
    b1,a2=(x2,y1+r),(x2-r,y1)
    c1,b2=(x2-r,y2),(x2,y2-r)
    d1,c2=(x1,y2-r),(x1+r,y2)

    return a1[0],a1[1],a2[0],a2[1],a2[0],a2[1],b1[0],b1[1],b2[0],b2[1],b2[0],b2[1],c1[0],c1[1],c2[0],c2[1],c2[0],c2[1],d1[0],d1[1],d2[0],d2[1],d2[0],d2[1]#,a1[0],a1[1]


class part_display(Canvas):
    def __init__(self,master,nsp,x=None):
        if isinstance(nsp,Prob.NSP):
            self.problem = nsp
        Canvas.__init__(self,master)
        self.mast = master
        self.__started = False 
        self.rect_dim = (40,40)
        self.init_rect = (20,20) 
        self.pader = 5
        if isinstance(x,np.ndarray):
            self._Show(x)
    
    def _Show(self,x):
        xx = np.reshape(x,(self.problem.get_nurses_no(),self.problem.get_no_of_days()))
        xx = np.transpose(xx)

        if not self.__started:
            for i in range(xx.shape[0]): #no of days
                for j in range(xx.shape[1]): #nurses no
                    x,y = self.get_location(i,j)
                    x1,y1 = x+self.rect_dim[0], y+self.rect_dim[1]
                    colm='white'
                    if j < self.problem.get_experienced_nurses_no():
                        colm='orange'
                    self.create_polygon(getspline(x,y,x1,y1,8),smooth=TRUE,splinesteps=50, outline='black', fill=colm,tags='all')
                    
                    te = self.pader

                    mu = (self.rect_dim[0]/2,self.rect_dim[1]/2)

                    self.create_oval(x+te,y+te,x1-te,y1-te,fill='green',outline='white',width=3,tags=('all','ovals'))

                    
                    self.create_text(x+mu[0],y+mu[1],fill='white',font=('Times New Roman',12,'bold'),text='%s'%part_display.conv(xx[i,j]))
            
            werq = self.bbox('all')
            t = (0,0,werq[2]-werq[0] + 2*self.init_rect[0],werq[3]-werq[1] + 2*self.init_rect[1])
            self.configure(scrollregion=t, bg='white')            
            xsroll= Scrollbar(self.mast,orient=HORIZONTAL,command=self.xview)
            xsroll.pack(side=TOP,expand=NO,fill=X)
            ysroll= Scrollbar(self.mast,orient=VERTICAL,command=self.yview)
            ysroll.pack(side=LEFT,expand=NO,fill=Y)
            self.configure(xscrollcommand=xsroll.set,yscrollcommand=ysroll.set)
            self.pack(side=TOP,expand=YES,fill=BOTH)
            self.__started = True
            
        else:
            pass
        
    def conv(x):
        if x==0:
            return 'O'
        elif x==1:
            return 'M'
        elif x==2:
            return 'E'
        elif x==3:
            return 'N'
        else:
            assert False,'Invalid input'
    
    def get_location(self,i,j):
        return self.init_rect[0] + self.rect_dim[0]*j,self.init_rect[1] + self.rect_dim[1]*i


    def draw_particle(self,particle):
        assert False,'Not implemented'

root = Tk()
e = Prob.NSP()
m = part_display(root,e,e.particles.copy().popitem()[1])
root.mainloop()