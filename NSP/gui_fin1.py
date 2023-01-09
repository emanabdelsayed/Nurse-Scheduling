from tkinter import *
from tkinter.ttk import Progressbar
import tkinter.messagebox as p
import numpy as np
import Prob
import Fit as f
import r_gui as re
import gui_small_class as gg
import Search_Monitor as Sear_Moni
import gentic as gene

class window(Frame):
    def __init__(self,master=None):
        Frame.__init__(self,master)        
        self.prob_conf = Button(self,text='Click to configure the nursing schedule problem',bg='#9FA8FF',padx=50,pady=50, command=self.prob_configure)
        self.prob_conf.pack(side=LEFT,expand=NO)
        self.isconfig=False

    def prob_configure(self):        
        arg_dict = dict(no_of_days=14,nurses_no=10,experienced_nurses_no=4,max_night_per_nurse='3/14',preference='4,2,2,2',min_experienced_nurse_per_shift=1,min_night_per_nurse='3/14')
        arg_err  = dict(no_of_days=int,nurses_no=int,experienced_nurses_no=int,max_night_per_nurse=float,preference=(tuple,int),min_experienced_nurse_per_shift=int,min_night_per_nurse=float)
        arg_descrp = dict(no_of_days='This is the number of days the schedule is expected to cover (int)',nurses_no='This is the total number of nurses in the hospital (int)',experienced_nurses_no='This is the number of experienced nurses in the hospital. It must be less than "nurses_no" (int)',max_night_per_nurse='This sets the maximum number of night shifts each nurses could be given. It is a hard constraint. It must be expressed as e.g. 3/14 which implies a maximum of 3 night shift in 2 weeks (14 days).(float)',preference='This is the minimum preference for each day. e.g. "4,2,2,2" will mean a minimum of 4 nurses on OFF, 2 on MORNING, 2 on EVENING and 2 on NIGHT shifts must be met for each of the schedule days - (tuple, ints)',min_experienced_nurse_per_shift='This sets the minimum number of experienced nurses that should be available for each of the "WORKING" shifts which are the Morning(M), Evening (E) and Night(N) shifts',min_night_per_nurse='This sets the minimum number of night shifts expected to be allocated to each of the nurses')
        w = get_dict(a,defaut=arg_dict,types=arg_err,description=arg_descrp)
        arg_dict = w.result
        
        if arg_dict:
            self.prob_conf.pack_forget()            
            r = Prob.NSP(**arg_dict)
            
            self.top = Top(self,r)
            self.bot = Bottom(self,r)

            #I set this ordering to make sure that the bottom widget is always visible
            self.bot.pack(side=BOTTOM,expand=NO,fill=X)
            self.top.pack(side=TOP,expand=YES,fill=BOTH)
            
            dis = self.top.disp
            p =r.particles.copy().popitem()[1]
            dis.set_particle(p)
            dis.set_violation(r.H3.viol_fxn(p,*r.get_fitness_args()),r.H3.viol_Type)
            dis.create_screen()
            #dis.pack(side=TOP,expand=YES,fill=BOTH)

class Top(Frame):
    def new_search(self,searchable=None,**kwargs):
        if isinstance(searchable,Sear_Moni.Search_Timer):
            s = searchable
            s.add_on_new_best(self.new_search)
        
        #To avoid all the cross thread errors I am experiencing
        self.after(2,self.t_new_search)
        
    def t_new_search(self):
        self.left.fit_view.reset_fitness_lst()
        self.left.part_select.on_part_holder_reset()

    def __init__(self,master,nsp):
        if not isinstance(nsp,Prob.NSP):
            raise TypeError('"nsp"must be of type Prob.NSP')
        Frame.__init__(self,master)
        
        self.disp = re.particle_display(self,nsp)
        self.nsp = nsp
        self.left = Left(self,nsp)       
        
        #event handling
        self.nsp.add_event_on_new_search(self.new_search)

        #packing
        self.left.pack(side=LEFT,expand=NO,fill=Y)
        self.disp.pack(side=RIGHT,expand=YES,fill=BOTH)

        #binding
        self.set4 = gg.fitview_set_by_viol_sel(self.left.viol_select,self.left.fit_view)
        self.set1 = gg.part_disp_set_viol(self.disp,self.left.viol_select,nsp,self.set4)        
        self.left.viol_select.bind(self.left.viol_select.selection_changed,self.set1)
        

        #self.left.part_select.bind(self.left.part_select.part_sel_changed,self.set1)# to enforce redrawing of the screen on partdisplay

        #self.set2 = gg.part_disp_set_viol(self.disp,self.left.viol_select,nsp)
        self.left.viol_select.bind(self.left.viol_select.show_viol_changed,self.set1)

        self.set3 =gg.fitview_sel_part_set(self.left.part_select,self.left.fit_view,self.disp,self.set1)
        self.left.part_select.bind(self.left.part_select.part_sel_changed,self.set3)

class Left(Frame):
    def __init__(self,master,nsp):
        if isinstance(nsp,Prob.NSP):
            self.nsp = nsp
        Frame.__init__(self,master)
        
        self.part_select = re.particle_selector(self,nsp)
        self.viol_select = re.const_fxn_selector(self,list(self.nsp.get_all_constraint_fxn_obj().items()))
        self.fit_view = re.fit_viewer(self,nsp)
    
        #packing

        self.part_select.pack(side=TOP,expand=NO,fill=X)
        self.viol_select.pack(side=TOP, expand=NO,fill=X)
        self.fit_view.pack(side=BOTTOM, expand=NO, fill=X)

DANGLING = 'dangling'
DORMANT = 'dormant'
OKAY = 'active'

class Bottom(Frame):
    def clear_canv(self):
        self.canv.delete('all')       
        pass
    def check_check(self):
        self.draw_canvas()
        self.set_show_s()

        self.gid = self.after(100,self.check_check)
        pass
    def draw_canvas(self):
        if self.state != DANGLING:
            self.clear_canv()
            x_len = 140
            y_len = 30
            font = ('Times New Roman',12)
            a =2
            a00 = a,a,a+x_len,a + y_len
            a10=a,a+y_len,a +x_len,a+ 2*y_len
            a01 = a+x_len,a,a+2*x_len,a+ y_len
            a11 = a+x_len,a+y_len,a+2*x_len,a+2*y_len
            a20 = a,a+2*y_len,a+x_len,a+3*y_len
            a21 = a+x_len,a+2*y_len,a+2*x_len,a+3*y_len

            t1 = Sear_Moni.tost(self.sem.get_curr_search_time_cp(),show_milli=True)#'00:10 33.158' #cpu time
            t2 = Sear_Moni.tost(self.sem.get_curr_time_el(),True)#'00:14 49.058' #wall time
            t3 = Sear_Moni.tost(self.sem.get_time_remaining_cp(),True)#'00:20 22.498'#cpu time rem
            t4 = Sear_Moni.tost(self.sem.get_time_remaining_el(),True)#'00:23 45.358' #wall time rem

            self.canv.create_rectangle(*a00,tags=('all','rect'))
            self.canv.create_rectangle(*a10,fill='green',tags=('all','rect'))
            self.canv.create_rectangle(*a01,tags=('all','rect'))
            self.canv.create_rectangle(*a11,fill='green',tags=('all','rect'))
            self.canv.create_rectangle(*a20,fill='red',tags=('all','rect'))
            self.canv.create_rectangle(*a21,fill='red',tags=('all','rect'))   

            self.canv.create_text(a00[0] +x_len/2, a00[1]+y_len/2,text='CPU Time',tags=('all','text'))
            self.canv.create_text(a01[0] +x_len/2, a01[1] + y_len/2,text='Wall Time',tags=('all','text'))

            self.canv.create_text(a10[0]+x_len/2, a10[1]+y_len/2,font = font,text='%s'%t1,fill='white',tags=('all','text'))
            self.canv.create_text(a11[0]+x_len/2, a11[1]+y_len/2,font = font,text='%s'%t2,fill='white',tags=('all','text'))

            self.canv.create_text(a20[0]+x_len/2, a20[1]+y_len/2,font = font,text='%s'%t3,fill='white',tags=('all','text'))
            self.canv.create_text(a21[0]+x_len/2, a21[1]+y_len/2,font = font,text='%s'%t4,fill='white',tags=('all','text'))   
    
    def set_show_s(self):
        if self.state != DANGLING:
            it=self.sem.get_ite()#ite
            maxit=self.sem.get_maxiter()#maximum iteration
            mean_x=self.sem.get_mean_fx()
            mean_p =self.sem.get_mean_fp()
            fg = self.sem._search_obj.fg

            self.it.set('%d'%it)        
            self.maxit.set('%d'%maxit)
            
            if mean_x:
                self.mean_x.set('%.7f'%mean_x)
            else:
                self.mean_x.set('Not_Set')
            if mean_p:
                self.mean_p.set('%.7f'%mean_p)
            else:
                self.mean_p.set('Not_Set')
            if fg:
                self.fg_s.set('%.7f'%fg)
            else:
                self.fg_s.set('Not_Set')

            perc= self.sem.get_percent_complete()
            timeRem = self.sem.get_time_remaining_el()

            if self.state != DORMANT:
                self.prog.configure(maximum=maxit,value=it)#progress_bar            
                self.percent.set('%d%%'%int(perc))
                self.timeRem.set('%s Remaining'%Sear_Moni.tost(timeRem))

                kker = {'pl':self.sem.playable,'pa':self.sem.can_pause,'st':self.sem.can_stop,'pr':self.sem.can_extend,'ne':self.sem.can_extend}
                for but in self.taaa:
                    if kker[but]():
                        self.buttons[but]['state'] = NORMAL
                    else:
                        self.buttons[but]['state'] = DISABLED

            stat= self.sem.get_curr_message()
        else:
            stat = ''        
        
        self.status.set('%s'%stat)

    def PLAY(self):
        self.sem.PLAY()
    def PAUSE(self):
        self.sem.PAUSE()
    def STOP(self):
        self.sem.STOP()
    def next_extend_maxite(self):
        m =self.get_extent()
        if m:
            self.sem.EXTEND(m)
    def prev_reduce_maxite(self):
        m = self.get_extent()
        if m:
            self.sem.EXTEND(-1*m)
    def get_extent(self):
        m = self.__extends.get()
        try:
            m = int(m)
        except (ValueError, TypeError):
                self.sem._search_obj.new_msg(self.sem.get_ite(),'error','extend variable must be a valid integer')
        else:
            self.__extends.set('')
            return m
    def create_genetic_regenerate(self):
        res = PSO_search(self.nsp,self)
        res.default = {'search name':'Un-named R-GA','population size':10, 'maximum iteration':500, 'mutation rate':0.01, 'Fitness_fxn':res.newWeight}
        res.description ={'search name':'The name you want your search to be called',
        'population size':'This is the number of particles you want to use to carry out the search', 
        'maximum iteration':'This is the number of times you want the search routine to be carried out',
        'mutation rate':'This is the NORMALIZED PROBABILITY of mutation (how frequent you want mutation of genes of particles) occurring when creating the child',
        'Fitness_fxn':"This controls the weight of soft constraints for evaluation the fitness of particles during the particle's run"}
        res('Configure a regenerating-Genetic algorithm search')
        if res.result:
            storing = res.result
            pop,maxite,mut_rate = storing['population size'],storing['maximum iteration'],storing['mutation rate']
            name = res.name
            newWeight = res.newWeight
            fit_txt = res.Fit_txt()           

            f_fxn = f.Fitness_Fxn(self.nsp,"This is type of Fitness fxn for a regenerating genetic algorithm (%s), whose fitness is obtained from the wieghted mean of other fitness fxns, %s"%(name,fit_txt),const_fxns=self.nsp.soft_con_dict,weights=newWeight)
            tuy = self.nsp.create_regenerate_genetic_search(pop,mut_rate,maxite,f_fxn)
            self.attach_new_search(Sear_Moni.Search_Monitor(tuy,name))

    def create_genetic_search(self):
        res = PSO_search(self.nsp,self)
        res.default = {'search name':'Un-named AQ-GA','population size':10, 'maximum iteration':500, 'mutation rate':0.01,'allowance quota':0.1, 'Fitness_fxn':res.newWeight}
        res.description ={'search name':'The name you want your search to be called',
        'population size':'This is the number of particles you want to use to carry out the search', 
        'maximum iteration':'This is the number of times you want the search routine to be carried out',
        'mutation rate':'This is the NORMALIZED PROBABILITY of mutation (how frequent you want mutation of genes of particles) occurring when creating the child',
        'allowance quota':'This is how much quota you want to reserve for exceptionally good particles violating hard constraints for a chance to atleast reproduce. \n 10 percent (0.1) is a nice value',
        'Fitness_fxn':"This controls the weight of soft constraints for evaluation the fitness of particles during the particle's run"}
        res('Configure a Genetic algorithm, allowance quota based search')

        if res.result:
            storing = res.result
            pop,maxite,mut_rate,all_prob = storing['population size'],storing['maximum iteration'],storing['mutation rate'],storing['allowance quota']
            name = res.name
            newWeight = res.newWeight
            fit_txt = res.Fit_txt()           

            f_fxn = f.Fitness_Fxn(self.nsp,"This is type of Fitness fxn for an allowance quota based genetic algorithm (%s), whose fitness is obtained from the wieghted mean of other fitness fxns, %s"%(name,fit_txt),const_fxns=self.nsp.soft_con_dict,weights=newWeight)
            regen_init = p.askyesno('Choose initial regenerate or not','Do you want to the initialization to be regenerated')
            tuy = self.nsp.create_genetic_search(pop,mut_rate,maxite,f_fxn,allow_prob=all_prob,regen_init=regen_init)
            self.attach_new_search(Sear_Moni.Search_Monitor(tuy,name))

    def create_pso_search(self):
        
        res = PSO_search(self.nsp,self)
        res.result = None
        res()        
        if res.result:
            storing = res.result
            pop,maxite,w,c1,c2 = storing['population size'],storing['maximum iteration'],storing['omega'],storing['phip'],storing['phig']
            name = res.name
            newWeight = res.newWeight
            fit_txt = res.Fit_txt()           

            f_fxn = f.Fitness_Fxn(self.nsp,"This is type of Fitness fxn for a Particle Swarm Optimization (%s) whose fitness is obtained from the wieghted mean of other fitness fxns, %s"%(name,fit_txt),const_fxns=self.nsp.soft_con_dict,weights=newWeight)
            tuy = self.nsp.create_PSO_search(pop,maxite,w,c1,c2,Fitness_fxn=f_fxn)
            self.attach_new_search(Sear_Moni.Search_Monitor(tuy,name))
    
    def pack_first_requestor(self):
        pass
    
    def unpack_first_requestor(self):
        self.fir_req.pack_forget()

    def attach_new_search(self,sea_Moni):
        self.sem = sea_Moni
        self.nsp.start_new_search(sea_Moni)
        self.bind_sem()
        
        if (self.state == DORMANT) or (self.state == DANGLING):
            if self.state == DORMANT:
                self.state = ACTIVE
                self.unpack_requestor()
                self.pack_intern()
                pass
            elif self.state == DANGLING:
                self.state = ACTIVE
                self.unpack_first_requestor()
                self.start_create_n_pack()

    def bind_sem(self):
        self.sem.add_on_ended(self.on_search_end)
    
    def on_search_end(self,*args,**kwargs):
        self.state = DORMANT
        self.unpack_intern()
        self.pack_requestor()

    def __init__(self,master,nsp):
        if isinstance(nsp,Prob.NSP):
            self.nsp = nsp
        else: raise TypeError()
        self.state = DANGLING 
        Frame.__init__(self,master)
        self.Removable = Frame(self)
        self.pack_first_requestor()
        self.status = StringVar()
        Label(self,bg='#002299',fg='white',textvariable=self.status,justify=LEFT).pack(side=BOTTOM,expand=YES,fill=X,ipady=2)
        self.Removable.pack(side=LEFT,expand=YES,fill=BOTH)
        # Button(self,text='Halstead Metrics',command=self.metrics).pack(side=RIGHT,expand=NO)
        self.check_check()
    
    def metrics(self):
        import tkinter.filedialog as fd
        import radon.metrics as met
        
        fd.Open()

    def pack_requestor(self):
        self.req =Button(self.cover,text='',font=('Times New Roman', 20),bg='white',fg='white')
        self.req.pack(side=LEFT,expand=YES,fill=BOTH)

    def unpack_requestor(self):
        self.req.pack_forget()

    def unpack_intern(self):
        self.prog.pack_forget()        
        self._wrap.pack_forget()
        self.l2.pack_forget()
        self.l1.pack_forget()

    def pack_intern(self):
        self.prog.pack(side=TOP,expand=NO,fill=X)        
        self._wrap.pack(side=BOTTOM,expand=NO,fill=X)
        self.l2.pack(side=RIGHT,expand=NO,padx=5)
        self.l1.pack(side=LEFT,expand=NO,padx=5)
    
    def start_create_n_pack(self):
        '''
        It is called after all the search objects are already attached first time after the Bottom widget's creation
        Creates all the full widget set and packs them
        '''
        #section 1
        self.cover = Frame(self.Removable)
        self.prog = Progressbar(self.cover,mode='determinate',maximum=1000,value=100)
        
        self._wrap = Frame(self.cover)
        self.photos = {'pl':PhotoImage(file='icons/play.png'),'pa':PhotoImage(file='icons/pause.png'),'st':PhotoImage(file='icons/stop.png'),'pr':PhotoImage(file='icons/prev.png'),'ne':PhotoImage(file='icons/next.png')}
        self.taaa = ('pl','pa','st','pr','ne')
        descrp = {'pl':'To begin a Search or Play after a Pause','pa':'To pause an ongoing search','st':'To stop an ongoing search','pr':'This is to reduce the maximum iteration of the search by the number entered here','ne':'To extend the maximum iteration of the search by whatever number entered here'}
        command = {'pl':self.PLAY,'pa':self.PAUSE,'st':self.STOP,'pr':self.prev_reduce_maxite,'ne':self.next_extend_maxite}
        self.__extends=StringVar()
        self.__extends.set('')
        self.buttons ={}
        for but in self.taaa:
            t = Button(self._wrap,image=self.photos[but],command=command[but])
            t.pack(side=LEFT,expand=NO,ipadx=3,ipady=3)
            gg.CreateToolTip(t,descrp[but],wrap_length=1000)
            self.buttons[but]=t
            if but=='pr':
                Entry(self._wrap,width=8,textvariable=self.__extends).pack(side=LEFT,expand=NO,ipadx=3,ipady=3)
        #Section 2
        self.canv = Canvas(self.Removable)
        self.canv.configure(width=284,height=100)
        self.draw_canvas()
        
        #Section 3
        self.show_s = Frame(self.Removable)
        self.it = StringVar()
        self.maxit= StringVar()
        self.mean_x = StringVar()
        self.mean_p = StringVar()
        self.fg_s = StringVar()
        Label(self.show_s,text='Iteration: ',font=('Verdana',11)).grid(row=0,column=0,sticky=E)
        Label(self.show_s,text='Max iteration: ').grid(row=1,column=0,sticky=E)
        Label(self.show_s,text='Population Mean: ').grid(row=2,column=0,sticky=E)
        Label(self.show_s,text='P_Best Mean: ').grid(row=3,column=0,sticky=E)
        Label(self.show_s,text='G_Best: ').grid(row=4,column=0,sticky=E)

        Label(self.show_s,textvariable=self.it).grid(row=0,column=1,sticky=W)
        Label(self.show_s,textvariable=self.maxit).grid(row=1,column=1,sticky=W)
        Label(self.show_s,textvariable=self.mean_x).grid(row=2,column=1,sticky=W)
        Label(self.show_s,textvariable=self.mean_p).grid(row=3,column=1,sticky=W)
        Label(self.show_s,textvariable=self.fg_s).grid(row=4,column=1,sticky=W)
        
        self.percent = StringVar()
        self.l1 =Label(self.cover,textvariable=self.percent)
        self.timeRem = StringVar()
        self.l2 = Label(self.cover,textvariable=self.timeRem)
        self.pack_intern()
        
        #'23 hours, 4 minutes, 15 seconds remaining'

        self.cover.pack(side=LEFT,expand=YES,fill=BOTH)
        self.show_s.pack(side=RIGHT,expand=NO,padx=4)
        self.canv.pack(side=RIGHT,expand=NO,padx=4)

class MyDialog(Toplevel):
    def __init__(self,parent,title=None):
        Toplevel.__init__(self,parent)
        self.transient(parent)
        if title:
            self.wm_title(title)
        self.par = parent
        self.result = None
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5,pady=5)
        self.buttonbox()
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.wm_protocol('WM_DELETE_WINDOW',self.cancel)
        self.initial_focus.focus_set()
        self.wait_window(self)
    def body(self,master):
        pass
    def cancel(self):
        self.par.focus_set()
        self.destroy()

    def buttonbox(self):
        box = Frame(self)
        w = Button(box,text='OK',width=10,command=self.ok,default=ACTIVE)
        w.pack(side=LEFT,padx=5,pady=5)
        w = Button(box,text="Cancel",width=10,command=self.cancel)
        w.pack(side=LEFT,padx=5,pady=5)
        self.bind('<Return>',self.ok)
        self.bind('<Escape>',self.cancel)
        box.pack()
    
    def ok(self,event=None):
        if not self.validate():
            self.initial_focus.focus_set()
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()
    
    def validate(self):
        return 1
    
    def apply(self):
        pass

class get_dict(MyDialog):
    def __init__(self,parent,title ="Parameters for the Nursing Schedule Problem", defaut=dict(),types=dict(),description=dict()):
        self.defaut = defaut
        self.description= description
        self.types = types
        self.storing ={}
        self.stori={}
        MyDialog.__init__(self,parent,title=title)
        
        
    def body(self,master):
        k={}
        for i,(item,value) in enumerate(self.defaut.items()):
            f =Label(master,text = item)
            f.grid(row=i,column=0)
            l = StringVar()
            l.set(value)
            if self.description:
                gg.CreateToolTip(f,self.description[item],wait_time=10)
            Entry(master,textvariable=l).grid(row=i,column=1)
            k[item]= l
        self.stori = k
    
    def validate(self):
        
        for item,value in self.stori.items():
            frm = self.types[item]
            try:
                if type(frm)==tuple:
                    frm = frm[1]
                    iu = ()
                    for x in value.get().split(sep=',',):
                        iu = iu + (frm(x),)
                    self.storing[item] = iu
                else:
                    self.storing[item]=frm(eval(value.get()))         
            except ValueError as qi:
                p.showerror('Invalid input','"%s" must be in "%s" format'%(item,frm))
                return 0
        return 1
    
    def apply(self):
        self.result = self.storing

class PSO_search(MyDialog):
    def Fit_txt(self):
        kam=''
        for item,val in self.newWeight.items():
            kam += '%s %s, '%(item,val)
        return kam
    
    def __call__(self,title='Configure a PSO Search'):
        MyDialog.__init__(self,self.parent,title=title)


    def __init__(self,nsp,parent):

        if isinstance(nsp,Prob.NSP):
            self.nsp = nsp
        self.newWeight = dict(C1=4,C2A=4,C2A1=0,C2B=0,C2B1=0,C3=1,C4=0,C4B=1,C5=1,C6=1)
        #lst = ('search name','population size','maximum iteration','omega','phip','phig','Fitness fxn')
        self.default = {'search name':'Un-named PSO','population size':100, 'maximum iteration':500, 'omega':0.5, 'phip':0.5, 'phig':0.5, 'Fitness_fxn':self.newWeight}
        self.description ={'search name':'The name you want your search to be called',
        'population size':'This is the number of particles you want to use to carry out the search', 
        'maximum iteration':'This is the number of times you want the search routine to be carried out',
        'omega':"This controls the weight and influence of the particle's velocity on its next position",
        'phip':"This controls the weight and influence of the partcle's personal best position on its next position", 
        'phig':"This controls the weight and influence of the search's global best position on its next position",
        'Fitness_fxn':"This controls the weight of soft constraints for evaluation the fitness of particles during the particle's run"}

        self.parent = parent
        
        
    def set_weight(self):
        descri = {'C1':self.nsp.C1.description,'C2A':self.nsp.C2A.description,
        'C2A1':self.nsp.C2A1.description,'C2B':self.nsp.C2B.description,
        'C2B1':self.nsp.C2B1.description,'C3':self.nsp.C3.description,'C4':self.nsp.C4.description,
        'C4B':self.nsp.C4B.description,'C5':self.nsp.C5.description,'C6':self.nsp.C6.description}
        ttypes = {'C1':int,'C2A':int,'C2A1':int,'C2B':int,'C2B1':int,'C3':int,'C4':int,'C4B':int,'C5':int,'C6':int}
        s = get_dict(self,title='getting fitness function weights',defaut=self.newWeight,types=ttypes,description=descri)
        self.newWeight = s.result
        self.fit_l.set(self.Fit_txt())

    def body(self,master):
        k={}
        for i,(item,value) in enumerate(self.default.items()):
            f =Label(master,text = item)
            f.grid(row=i,column=0)
            l = StringVar()
            l.set(value)
            if self.description:
                gg.CreateToolTip(f,self.description[item],wait_time=10)
            if item == 'Fitness_fxn':
                l.set(self.Fit_txt())
                Entry(master,textvariable=l).grid(row=i,column=1)
                Button(master,text='Adjust Fitness Weights',command=self.set_weight).grid(row=i,column=2)
                self.fit_l = l
            else:
                Entry(master,textvariable=l).grid(row=i,column=1)
                k[item]= l
        self.stori = k

    def validate(self):
        tie = ''
        self.storing = {}
        for item,value in self.default.items():
            try:
                if type(value) == int:
                    tie = 'integer'
                    er = int(self.stori[item].get())
                    self.storing[item] = er
                elif type(value) == float:
                    tie = 'integer'
                    er = float(self.stori[item].get())
                    self.storing[item] = er
            except ValueError as qi:
                p.showerror('Invalid Value Entered','%s must be in %s format'%(item,tie))
                return 0
                
        return 1
                
    def apply(self):
        f_fxn = f.Fitness_Fxn(self.nsp,"""This is type of Fitness fxn whose fitness is 
        obtained from the wieghted mean of other fitness fxns,%s"""%self.Fit_txt(),
        const_fxns=self.nsp.soft_con_dict,weights=self.newWeight)
        self.result = self.storing
        self.name = self.stori['search name'].get()

class NSP_search_select(MyDialog):
    def __init__(self,parent,sch_ls = {'Genetic':'Genetic algorithm with Regeneration','PSO':'Particle Swarm Optimization',}):
        
        self.sch_ls = list(sch_ls.items())
        MyDialog.__init__(self,parent,title='Select the Search Type')
    def body(self,master):        
        self.lst  = Listbox(master)
        self.fill_list()
        self.prevsel = (0,)
        self.prevsel1 = 0
        self.lst.selection_set(0)
        tr = Button(master,text='show Description')
        self.tooltip = gg.CreateToolTip(tr,list(self.sch_ls[0])[1],True)
        self.lst.configure(height=len(self.sch_ls) + 2)
        tr.pack(side=TOP,expand=NO,padx=3,pady=3)
        self.lst.pack(side=TOP,expand=NO,padx=3,pady=3)
        self.check_sel()
    def fill_list(self):
        self.lst.delete(0,END)
        for i,(key,val) in enumerate(self.sch_ls):
            self.lst.insert(i,key)
    def on_sel_change(self):
        m = self.prevsel1
        self.tooltip.set_text(list(self.sch_ls[m])[1])
    def check_sel(self):
        k = self.lst.curselection()
        if k != self.prevsel:
            if k:                
                self.prevsel1 = k[0]
                self.on_sel_change()
            self.prevsel = k
        self.after(300,self.check_sel)
    def apply(self):
        self.result  = list(self.sch_ls[self.prevsel1])[0]

a = Tk()
a.wm_title('Nursing Schedule Problem')
w = window(a)
w.pack(side=LEFT,expand=YES,fill=BOTH)
a.mainloop()