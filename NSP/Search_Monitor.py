import time
import sys
import Search
import gentic
import numpy as np

def get_time_cp():
    return time.process_time() if sys.version_info[0] >= 3 else time.clock()
def get_time_el():
    return time.perf_counter() if sys.version_info[1] >=3 else time.clock() if sys.platform[:3] == 'win' else time.time()

NOT_BEGUN = 0
STARTED = 1
INITIALIZED =2
ITE_CHANGED = 3
ENDED = 4

class Search_Timer(Search.ab_Search):
    def _diff_cp(self):
        return get_time_cp() - self.prev_time_cp
    def _diff_el(self):
        return get_time_el() - self.prev_time_el
    def on_start(self,ite=0,nsp=None,*args,**kwargs):
        self.start_time_cp = get_time_cp()
        self.start_time_el = get_time_el()
        self.prev_time_cp = get_time_cp()
        self.prev_time_el = get_time_el()
        self.timer_state = STARTED
    def on_initialized(self,ite=0,nsp=None,*args,**kwargs):
        self.prev_dur_cp = self._diff_cp()
        self.prev_dur_el = self._diff_el()
        self.init_cp = self.prev_dur_cp
        self.init_el = self.prev_dur_el
        self.prev_time_cp = get_time_cp() 
        self.prev_time_el = get_time_el()
        self.timer_state = INITIALIZED
    def b4_ite_changed(self,ite=0,nsp=None,*args,**kwargs):
        self.prev_dur_cp = self._diff_cp()
        self.prev_dur_el = self._diff_el()
        self.time_cp += self.prev_dur_cp
        self.time_el += self.prev_dur_el
        if not (ite <=1):
            if not ite:
                raise AttributeError()
            else:
                self.timer_state = ITE_CHANGED 
    def aft_ite_changed(self,ite=0,nsp=None,*args,**kwargs):
        self.prev_time_cp = get_time_cp() 
        self.prev_time_el = get_time_el()
    def on_ended(self,ite=0,nsp=None,*args,**kwargs):
        self.timer_state = ENDED

    def get_last_ite_el_dur(self):
        return self.prev_dur_el
    def get_last_ite_cp_dur(self):
        return self.prev_dur_cp
    def get_curr_time_cp(self):
        return get_time_cp() - self.start_time_cp
    def get_curr_time_el(self):
        return get_time_el() - self.start_time_el
    def get_curr_search_time_el(self):
        return self.init_el + self.time_el
    def get_curr_search_time_cp(self):
        return self.init_cp + self.time_cp
    def get_time_remaining_cp(self):
        if self.timer_state == INITIALIZED:
            return self.init_cp*self.get_maxiter()
        elif self.timer_state == ITE_CHANGED or self.timer_state == ENDED:
            return self.time_cp/self.get_ite() * (self.get_maxiter() - self.get_ite())
        else:
            return 0
    def get_time_remaining_el(self):
        if self.timer_state == INITIALIZED:
            return self.init_el*self.get_maxiter()
        elif self.timer_state == ITE_CHANGED or self.timer_state == ENDED:
            return self.time_el/self.get_ite() * (self.get_maxiter() - self.get_ite())
        else:
            return 0
    def get_ite(self):
        return self._search_obj.ite
    def get_maxiter(self):
        return self._search_obj.maxite   
    
    def BEGIN(self):
        return self._search_obj.BEGIN()
    def EXTEND(self,value):
        return self._search_obj.EXTEND(value)
    def PAUSE(self):
        return self._search_obj.PAUSE()
    def PLAY(self):
        return self._search_obj.PLAY()
    def STOP(self):
        return self._search_obj.STOP()
    
    def can_stop(self):
        return self._search_obj.can_stop()
    def can_pause(self):
        return self._search_obj.can_pause()
    def can_play(self):
        return self._search_obj.can_play()
    def playable(self):
        return self._search_obj.playable()
    def can_extend(self):
        return self._search_obj.can_extend()    

    def is_started(self):
        return self._search_obj.is_started()
    def has_ended(self):
        return self._search_obj.has_ended()
    def get_fitt(self):
        '''
        This gives the Fitness function cached by the Super Class "part_Holder"
        '''
        return self._search_obj.get_fitt()
    def get_fit_args(self):
        return self._search_obj.get_fit_args()
    def get_no_of_days(self):
        return self._search_obj.get_no_of_days()
    def get_nurses_no(self):
        return self._search_obj.get_nurses_no()
    def get_particles(self):
        return self._search_obj.get_particles()
    
    def set_b4stop(self,func):
        self._search_obj.set_b4stop(func)

    def add_on_start(self,func):
        self._search_obj.on_start.append(func)
    def add_on_initialized(self,func):
        self._search_obj.on_initialized.append(func)
    def add_on_ite_changed(self,func):
        self._search_obj.on_ite_changed.append(func)
    def add_on_pause(self,func):
        self._search_obj.on_pause.append(func)
    def add_on_play(self,func):
        self._search_obj.on_play.append(func)
    def add_on_extended(self,func):
        self._search_obj.on_extended.append(func)
    def add_on_new_best(self,func):
        self._search_obj.on_new_best.append(func)
    def add_on_error(self,func):
        self._search_obj.on_error.append(func)
    def add_on_ended(self,func):
        self._search_obj.on_ended.append(func)

    def __init__(self,Search_Object):
        from Search import Search
        if isinstance(Search_Object,Search):
            if Search_Object.is_fresh():
                self._search_obj = Search_Object
            else:
                raise TypeError('Any search object to be used by the search monitor must still be fresh')
        else:
            raise TypeError('Search_Object must be a valid instance of a "Search" object')

        self._search_obj.on_b4_ite_changed.append(self.b4_ite_changed)
        self._search_obj.on_aft_ite_changed.append(self.aft_ite_changed)
        self._search_obj.on_ended.append(self.on_ended)
        self._search_obj.on_start.append(self.on_start)
        self._search_obj.on_initialized.append(self.on_initialized)
        self.time_cp, self.time_el =0,0 
        self.init_cp, self.init_el = 0,0 
        self.prev_dur_cp, self.prev_dur_el = 0,0
        self.prev_time_cp, self.prev_time_el =0,0 
        self.timer_state = NOT_BEGUN
def p_d_t(time_s,show_milli=False):
    sec = int(time_s)
    milli = time_s - sec
    milli = milli*1000
    milli = int(milli)
    minu = int(sec/60)
    sec = sec%60  
    hrs = int(minu/60)
    minu = minu%60
    days = int(hrs/24)
    hrs = hrs%24
    if show_milli:
        hrs += days *24
        return hrs,minu,sec,milli
    return days,hrs,minu,sec
def tost(time_s,show_milli=False):
    plate = ('days','hours','minutes','seconds')
    if show_milli:
        win = tuple(p_d_t(time_s,True))
        #print(win)        
        return '%02d:%02d %02d.%03d'%win
    else:
        win = tuple(p_d_t(time_s,False))
        ans = ''
        for k,x in enumerate(win):
            if x:
                ans += '%d %s '%(x,plate[k])
        return ans
def event_trigger(func_list,*args,**kwargs):
    for fxn in func_list:
        fxn(*args,**kwargs)    
class Search_Monitor(Search_Timer):
    def on_init(self,*args,**kwargs):
        self.add_info('%s initialized succesfully'%self.name)

    def on_star(self,*args,**kwargs):
        self.add_info('%s search Begins'%self.name)
        self.__standby_message = '... SEARCH ONGOING ...'

    def on_ended_(self,*args,**kwargs):
        qscp = tost(self.get_curr_search_time_cp())
        qsel = tost(self.get_curr_search_time_el())
        qel = tost(self.get_curr_time_el())
        self.add_info('%s search Ends after %s cpu search time %s elapsed search time and %s wall time '%(self.name,qscp,qsel,qel))
        self.__cur_duration = 30
        self.__standby_message = '... SEARCH UNCONFIGURED ...'
    
    def on_error(self,ite=0,msg='',*args,**kwargs):
        self.add_info('Error: %s found in %s search @ ite %s'%(msg,self.name,ite))
    
    def on_new_best(self,ite=0,fg=0,*args,**kwargs):
        self.add_info('New Best found @ ite: %d with objective fxn value %.3f'%(ite,fg))
    
    def on_pause(self,ite=0,*args,**kwargs):
        self.add_info('%s search paused @ ite %d'%(self.name,ite))
        self.__standby_message = '... SEARCH PAUSED ...'
    
    def on_play(self,ite=0,*args,**kwargs):
        self.add_info('%s search resumes @ ite %d'%(self.name,ite))
        self.__standby_message = '... SEARCH ONGOING ...'
    def on_extended(self,ite=0,extension=0,*args,**kwargs):
        self.add_info('%s search maximum is extended by %d @ ite %d'%(self.name,extension,ite))

    def on_ite_changed(self,ite=0,fx=[],fp=[],*args,**kwargs):        
        if isinstance(fx,np.ndarray):
            self.__fx =fx
        if isinstance(fp,np.ndarray):
            self.__fp=fp

    def get_mean_fx(self):
        m = self.__fx
        if isinstance(m,np.ndarray):
            k = m[np.isfinite(m)]
            if len(k):
                gh = np.mean(k)
                return gh
            else:
                return np.inf

    def get_mean_fp(self):
        m = self.__fp
        if isinstance(m,np.ndarray):
            k = m[np.isfinite(m)]
            if len(k):
                gh = np.mean(k)
                if self._search_obj.fg and gh < self._search_obj.fg:
                    raise ValueError()
                return gh
            else:
                return np.inf
        else:
            return self.get_mean_fx()

    def add_info(self,message=''):
        nsp = self._search_obj.nsp
        time_cp =self.get_curr_search_time_cp()
        time_el =self.get_curr_time_el()
        self.infolist.append('%s @ cpu time:%s @ elapsed time:%s'%(message,tost(time_cp,True),tost(time_el,True)))
        self.set_curr_msg(message)
        nsp.trigger_on_new_info(message=message,time_cp=time_cp,time_el=time_el) 
    def get_percent_complete(self):
        t = self.get_ite()
        m = self.get_maxiter()
        if m:
            return t/m *100
        else:
            return 0
    def trigger_Search_centric_event(self):
        self._search_obj.nsp.trigger_on_search_centric()

    def get_curr_message(self):
        if (get_time_el()-self.__time_cur_set) < self.__cur_duration:
            return self.__curr_message
        else:
            return self.__standby_message
    def set_curr_msg(self,message):
        self.__curr_message = message
        self.__time_cur_set = get_time_el()
            
    def __init__(self,search_obj,name):
        Search_Timer.__init__(self,search_obj)
        self.name = name
        self.infolist =[]
        self.__cur_duration =5
        self.set_curr_msg('__init__ inco')
        self.__standby_message='... SEARCH NOT YET STARTED ...'
        self.__fx=None
        self.__fp=None
        self.add_on_start(self.on_star)
        self.add_on_initialized(self.on_init)
        self.add_on_ite_changed(self.on_ite_changed)
        self.add_on_new_best(self.on_new_best)
        self.add_on_error(self.on_error)
        self.add_on_pause(self.on_pause)
        self.add_on_play(self.on_play)
        self.add_on_ended(self.on_ended_)
        self.add_on_extended(self.on_extended)