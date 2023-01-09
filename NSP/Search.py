from queue import Queue
import time
import numpy as np
#import Fit
from threading import Thread
#from Prob import NSP,part_Holder
class part_Holder:
    def transform_to_int(x):
        if isinstance(x,np.ndarray):
            y = x.copy()
            if y.dtype == float:
                o = np.logical_and(y>=0, y<1)
                y[o] = 0
                m = np.logical_and(y>=1, y<2)
                y[m] =1
                e = np.logical_and(y>=2, y<=3)
                y[e] =2
                n = np.logical_and(y>3, y<=4)
                y[n] = 3
            elif y.dtype == int:
                pass
            else:
                raise ValueError()
        else:
            raise TypeError()
        return np.array(y,dtype=int)# absence of this explicit conversion to int must have been the cause of most of my error since morning why H2,H3 and C5 's record no error checkable occurrence even though the fitness fxn value of C5 says

    def extr_aggreg_nurse(x,nurses_no,no_of_days):
        return part_Holder.extr_aggreg(x,1,nurses_no,no_of_days)
    
    def extr_aggreg_days(x,nurses_no,no_of_days,experienced_nurses=None):
        return part_Holder.extr_aggreg(x,0,nurses_no,no_of_days,experienced_nurses)
    
    def extr_aggreg(x,a,nurses_no,no_of_days,experienced=None):
        r = np.reshape(x,(nurses_no,no_of_days))
        
        if experienced:
            if a:
                raise TypeError('You cant isolate experienced nurses from others in this kind of case')
            else:
                r = r[:experienced,:]

        if a not in (0,1):
            raise ValueError('parameter a must be either 0 or 1')
        if x.dtype == int:
            o = (r==0).sum(axis=a)
            m = (r==1).sum(axis=a)
            e = (r==2).sum(axis=a)
            n = (r==3).sum(axis=a)
        elif x.dtype == float:
            o = np.logical_and(r>=0, r<1).sum(axis=a)
            m = np.logical_and(r>=1, r<2).sum(axis=a)
            e = np.logical_and(r>=2, r<=3).sum(axis=a)
            n = np.logical_and(r>3, r<=4).sum(axis=a)
        else:
            raise TypeError('The input must be an ndarry of type float or int')

        return np.transpose(np.vstack((o,m,e,n)))
    
    def get_obj_fxn(self):
        return self.fitt.obj_fxn
    def get_particles(self):
        return self.particles
    
    def __init__(self,Fitness,particles={}):
        
        from Fit import Fitness as F
        if isinstance(Fitness,F):
            self.fitt = Fitness
        else:
            raise TypeError('"Fitness" must be a valid instance of "Fitness"')
        self.particles = particles
        
class ab_Search():
    def BEGIN(self):
        assert False,'abstract method, must be implemented in class'
    def EXTEND(self):
        assert False,'abstract method, must be implemented in class'
    def STOP(self):
        assert False,'abstract method, must be implemented in class'
    def PAUSE(self):
        assert False,'abstract method, must be implemented in class'
    def PLAY(self):
        assert False,'abstract method, must be implemented in class'
    
    def set_b4stop(self):
        assert False,'abstract method, must be implemented in class'
    
    def can_extend(self):
        assert False,'abstract method, must be implemented in class'
    def can_pause(self):
        assert False,'abstract method, must be implemented in class'
    def can_stop(self):
        assert False,'abstract method, must be implemented in class'
    def can_play(self):
        assert False,'abstract method, must be implemented in class'
    
    def has_ended(self):
        assert False,'abstract method, must be implemented in class'
    def is_started(self):
        assert False,'abstract method, must be implemented in class'
    
    def get_ite(self):
        assert False,'abstract method, must be implemented in class'
    def get_maxiter(self):
        assert False, 'abstract method, must be implemented in class'
    def get_fit_args(self):
        assert False,'abstract method, must be implemented in class'
    def get_no_of_days(self):
        assert False,'abstract method, must be implemented in class'
    def get_nurses_no(self):
        assert False,'abstract method, must be implemented in class'
    def get_particles(self):
        assert False,'abstract method, must be implemented in class'
    def get_fitt(self):
        assert False, 'abstract method, must be implememted in class'

class Search(part_Holder,ab_Search):
    def events(fxn_lst,*args,**kwargs):
        for f in fxn_lst:
            f(*args,**kwargs)

    def ite_changed(self,ite,maxite,fx,x=[],p=[],fp=[],g=[],fg=np.inf):
        if self.on_b4_ite_changed:
            Search.events(self.on_b4_ite_changed,ite=ite,nsp=self.nsp,x=x,fx=fx,p=p,fp=fp)
        
        self.ite = ite
        self.maxite = maxite
        if not self.playState:
            self.d_pause(ite)
                
        if self.__extend <= self.ite -self.maxite or self.__stop:
            self.__extend = self.ite - self.maxite
            self.__extend += self.__b4stop(ite=ite,maxite=maxite,nsp=self.nsp,x=x,fx=fx,p=p,fp=fp) if self.__b4stop else 0
            if self.__extend > self.ite -self.maxite and self.__stop:
                self.__stop = False


        tmp=0
        if self.__extend :
            if self.__extend > self.ite -self.maxite:
                tmp = self.__extend
                self.__extend = 0
            else:
                self.__extend = 0
                self.__stop = True

        if self.__stop:
            tmp = self.ite - self.maxite
            self.maxite = self.ite # this is because there is no way the system is going to update  the maxite again after this iteration
        elif self.ite == self.maxite:
            self.__stop = True
        if tmp:
            if self.on_extended:
                Search.events(self.on_extended,ite=ite,nsp=self.nsp,extension=tmp)
        if self.on_ite_changed:
            Search.events(self.on_ite_changed,ite=ite,nsp=self.nsp,x=x,fx=fx,p=p,fp=fp)
        if self.on_aft_ite_changed:
            Search.events(self.on_aft_ite_changed,ite=ite,nsp=self.nsp,x=x,fx=fx,p=p,fp=fp)
        return tmp
    
    def new_msg(self,ite,typee,msg):
        if typee.lower() == 'initialized':
            if self.on_initialized:
                Search.events(self.on_initialized,ite=ite,nsp=self.nsp, msg=msg)
        elif typee.lower() == 'ended':
            if self.on_ended:
                Search.events(self.on_ended,ite=ite,nsp=self.nsp,msg=msg)
        elif typee.lower() == 'error':
            if self.on_error:
                Search.events(self.on_error,ite=ite,nsp=self.nsp,msg=msg)
        else:
            self.new_msg(ite,'error', 'Unknown type: %s msg: %s' %(typee,msg) )
    
    def new_best(self,ite,g,fg):
        self.particles['g_best @ ite: %d Obj_fxn: %.4f'%(self.ite,fg)] = g
        self.g = g
        self.fg = fg
        if self.on_new_best:
            Search.events(self.on_new_best,ite=ite,nsp=self.nsp,g=g, fg=fg)
    
    def after_ended(self):
        self.ended = True

    def start(self):
        while not self.started:
            time.sleep(self.__delay_time)
        if self.on_start:
            Search.events(self.on_start,ite=-1,nsp=self.nsp)

    def BEGIN(self):
        if not self.started:
            self.started = True
        else:
            self.new_msg(self.ite,'error','you can only BEGIN once')

    def d_pause(self,ite):
        if self.on_pause:
            Search.events(self.on_pause,ite=ite,nsp=self.nsp)
        while not self.playState:
            time.sleep(self.__delay_time)
        if self.on_play:
            Search.events(self.on_play,ite=ite,nsp=self.nsp)
    
    def STOP(self):
        if self.can_stop():
            self.__stop = True
            self.playState = True
        else:
            self.new_msg(self.ite,'error','a search can only be STOP once')
    
    def EXTEND(self,value):
        if self.can_extend():
            self.__extend = value
            self.playState = True
        else:
            self.new_msg(self.ite,'error','cannot EXTEND b4 implementation')

    def PAUSE(self):
        if self.can_pause():
            self.playState = False
        else:
            self.new_msg(self.ite,'error','cannot PAUSE when already paused')

    def PLAY(self):
        if self.can_play():
            self.playState = True
        elif not self.is_started():
            self.BEGIN()
        else:
            self.new_msg(self.ite,'error','cannot PLAY when already played')

    def can_extend(self):
        return self.started and not(self.__extend or self.__stop)
    def can_stop(self):
        return self.started and (not self.__stop)
    def can_pause(self):
        return self.started and self.playState and (not self.__stop)
    def can_play(self):
        return self.started and not (self.playState or self.__stop)
    
    def playable(self):
        return not self.is_started() or self.can_play()

    def is_fresh(self):
        return not (self.started or self.__b4stop  or self.on_start or self.on_new_best or self.on_initialized or self.on_b4_ite_changed or self.on_ite_changed or self.on_aft_ite_changed or self.on_pause or self.on_play or self.on_error or self.on_ended)
    def is_started(self):
        return self.started
    def has_ended(self):
        return self.ended

    def set_b4stop(self,func):
        if not self.__b4stop:
            self.__b4stop = func
        else: raise TypeError('b4stop cannot be multiply assigned')

    def get_ite(self):
        return self.ite
    def get_maxiter(self):
        return self.maxite
    def get_fitt(self):
        return self.fitt    
    def get_particles(self):
        return self.particles
    def get_fit_args(self):
        return self.nsp.get_fitness_args()
    def get_nurses_no(self):
        return self.nsp.get_nurses_no()
    def get_no_of_days(self):
        return self.nsp.get_no_of_days()    
    def D(self):
        return self.nsp.get_vect_len()
    def getfitt(self):
        return self.fitt

    def __init__(self,maxite,Fitness,nsp):
        part_Holder.__init__(self,Fitness=Fitness,particles={})
        self.maxite = maxite
        from Prob import NSP
        if isinstance(nsp, NSP):
            self.nsp = nsp
        else:
            raise TypeError('"nsp" must be a valid instance of "NSP"')
        self.ite=0
        self.started = False
        self.ended = False
        self.playState = True
        self.__extend =0
        self.__stop = False
        self.__delay_time = 0.5
        self.__b4stop = None
        self.on_b4_ite_changed=[]
        self.on_ite_changed=[]
        self.on_aft_ite_changed=[] 
        self.on_new_best=[]
        self.on_initialized=[]
        self.on_error=[]
        self.on_extended=[]
        self.on_ended=[]
        self.on_pause=[]
        self.on_play=[]
        self.on_start=[]
        self.g =[]
        self.fg =[]
        self.threadd = Thread(target=self.start)
        self.threadd.daemon = True
        self.threadd.start()