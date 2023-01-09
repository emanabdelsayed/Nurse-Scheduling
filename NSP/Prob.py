import numpy as np
import Fit
import Constraints as c
from Search import Search, part_Holder,ab_Search
from gentic import allowance_gen_algo, regen_gen_algo

def event_trigger(func_list,*args,**kwargs):
    for fxn in func_list:
        fxn(*args,**kwargs)    
class NSP(part_Holder):
    def get_max_night_per_nurse(self):

        return self.__arg_const__['max_night_per_nurse']
    def get_no_of_days(self):
        return self.__nsp__['no_of_days']
    def get_nurses_no(self):
        return self.__nsp__['nurses_no']
    def get_preferences(self):
        return self.__arg_const__['preference'] 
    def get_experienced_nurses_no(self):
        return self.__nsp__['experienced_nurses_no']
    def get_min_experienced_nurse_per_wshift(self):
        return self.__arg_const__['min_experienced_nurse_per_shift']
    def get_min_night_per_nurse(self):
        return self.__arg_const__['min_night_per_nurse']
    def get_fitness_args(self):
        return self.get_max_night_per_nurse(),self.get_nurses_no(),self.get_no_of_days(),self.get_preferences(),self.get_experienced_nurses_no(),self.get_min_experienced_nurse_per_wshift(),self.get_min_night_per_nurse()
    def get_Hard_Viol_fxns(self):
        return [x.viol_fxn for x in self.hard_con_dict.values()]
    def get_PSO_Hard_fxn(self):
        return self.H23.obj_fxn
    def get_vect_len(self):
        return self.get_nurses_no()*self.get_no_of_days()
    def can_search(self):
        if self.curr_search:
            if self.curr_search.has_ended():
                return True
        else:
            return True
        return False
    def start_new_search(self,Searchable,begin=False):
        if self.can_search():
            if isinstance(Searchable,ab_Search):
                if self.curr_search:
                    self.prev_searches['%dth search'%len(self.prev_searches)] = self.curr_search                
                self.curr_search = Searchable
                event_trigger(self.__on_new_search,Searchable)
                if begin:
                    Searchable.BEGIN()
            else:
                pass
        else:
            pass
    def create_regenerate_genetic_search(self,pop_size,mutation_prob,maxite,Fitness_fxn='default'):
        if Fitness_fxn=='default':
            tmp = regen_gen_algo(0,4,pop_size,mutation_prob,self,self.fitt,maxite)
        elif isinstance(Fitness_fxn,Fit.Fitness_Fxn):
            tmp = regen_gen_algo(0,4,pop_size,mutation_prob,self,Fitness_fxn,maxite)
        else:
            raise TypeError('Fitness fxn must be of type: %s'%type(Fitness_fxn))
        return tmp
    def create_genetic_search(self,pop_size,mutation_prob,maxite,Fitness_fxn='default',allow_prob=0.1,regen_init=True):
        if Fitness_fxn=='default':
            tmp = allowance_gen_algo(0,4,pop_size,mutation_prob,self,self.fitt,maxite,allow_prob=allow_prob,regen_init=regen_init)
        elif isinstance(Fitness_fxn,Fit.Fitness_Fxn):
            tmp = allowance_gen_algo(0,4,pop_size,mutation_prob,self,Fitness_fxn,maxite,allow_prob=allow_prob, regen_init=regen_init)
        else:
            raise TypeError('Fitness fxn must be of type: %s'%type(Fitness_fxn))
        return tmp
    def is_default(self):
        return True if self.get_no_of_days()==14 and self.get_nurses_no()==10 and self.get_experienced_nurses_no()==4 and self.get_max_night_per_nurse()==3/14 and self.get_preferences()==(4,2,2,2) and self.get_min_experienced_nurse_per_wshift()==1 and self.get_min_night_per_nurse()==3/14 else False
    def dep_get_all_particles(self):
        outp = self.particles
        if self.curr_search:
            outp.update(self.curr_search.get_particles())
        if self.prev_searches:
            for sech in self.prev_searches:
                outp.update(sech.get_particles())
        return outp
    def get_all_part_holder(self):
        n = self.prev_searches.copy()
        n[self.self_name] = self
        if self.curr_search:
            n[self.curr_search_name] = self.curr_search
        return n
    def get_all_constraint_fxn_obj(self):
        mm = self.hard_con_dict.copy()
        mm.update(self.soft_con_dict)
        return mm
    def get_all_fitness(self):
        outp = {}
        for ky,val in self.man_fitt.items():
            outp['M %s'%ky] =val
        for ky,val in self.prev_searches.items():
            outp['P %s'%ky] = val.get_fitt()
        outp['D %s'%self.self_name] = self.fitt
        if self.curr_search:
            outp['D %s'%self.curr_search_name] = self.curr_search.get_fitt()       
        for ky,val in self.get_all_constraint_fxn_obj().items():
            outp['C %s'%ky] = val     
        return outp
    def add_new_man_fit(self,fitness,name=''):
        if isinstance(fitness,Fit.Fitness):
            if name:
                ctt = 1
                nm =name
                while True:
                    try:
                        tete = self.man_fitt[nm]
                    except KeyError:
                        break
                    nm = '%s %d'%(name,ctt)
                    ctt+=1
                self.man_fitt[nm] = fitness
            else:
                self.man_fitt['Unamed Fitness %d'%len(self.man_fitt)] = fitness
    def create_rand_particle(self):
        y = np.random.randint(0,4,self.get_vect_len())
        return y
    def add_event_on_new_info(self,func):
        if func:
            self.__on_new_info.append(func)
    def add_event_on_new_search_centric(self,func):
        if func:
            self.__on_search_centric.append(func)
    def add_event_on_new_search(self,func):
        if func:
            self.__on_new_search.append(func)
    def trigger_on_new_info(self,*args,**kwargs):
        if self.__on_new_info:
            event_trigger(self.__on_new_info,*args,**kwargs)
    def trigger_on_search_centric(self,*args,**kwargs):
        if self.__on_search_centric:
            event_trigger(self.__on_search_centric,*args,**kwargs)
    def __init__(self,no_of_days=14,nurses_no=10,experienced_nurses_no=4,max_night_per_nurse=3/14,preference=(4,2,2,2),min_experienced_nurse_per_shift=1,min_night_per_nurse=3/14):
        self.__on_new_info = []
        self.__on_search_centric =[]
        self.__on_new_search = []
        self.__nsp__ = dict(no_of_days=no_of_days,nurses_no=nurses_no,experienced_nurses_no=experienced_nurses_no)
        self.__arg_const__= dict(max_night_per_nurse=max_night_per_nurse,preference=preference,min_experienced_nurse_per_shift=min_experienced_nurse_per_shift,min_night_per_nurse=min_night_per_nurse)
        self.H2 =  Fit.Const_Fxn(c.H2,self,is_obj_fxn=True,is_Hard=True,viol_Type=(None,),Default_Weight=0,
        Description='''It is violation-showing fitness function that expresses one of the Hard Constraints H2.
    CHECKS: If there is no nurse having a Morning Shift immediately after Night Shift. 
    NORMALIZATION: The result is normalized in the -ve direction over all NIGHT -SHIFTS
    ''')
        self.H3 = Fit.Const_Fxn(c.H3b,self,is_obj_fxn=True,is_Hard=True,viol_Type=(None,),Default_Weight=0,
        Description='''It is a violation-showing fitness function that expresses one of the Hard Constraints H3.
    CHECKS: If the number of night shift every nurse have is not more than MAXIMUM.
    MAXIMUM SET BY:  max_night_per_nurse - e.g. 3/14 means 3 night shifts per two weeks is the MAXIMUM
    NORMALIZATION: The result is normalized (it is not so obvious and may be confusing) in the -ve direction over all NURSES and DAYS
    ''')
        self.C1 = Fit.Const_Fxn(c.C1,self,viol_Type=('N',),Default_Weight=4,
        Description='''It is a violation-showing fitness function that expresses one of the Soft Constraints C1.
    CHECKS: If all nurses has a fair working shift schedule. i.e. How much absence of cheating among all nurses the particle(schedule) achieves.
    NORMALIZATION: The result is normalized over all NURSES
    ''')
        self.C2A = Fit.Const_Fxn(c.C2A,self,viol_Type=('D',),Default_Weight=4,
        Description='''It is a violation-showing fitness function that expresses one of the Soft Constraints C2.
    CHECKS:By how much does the schedule (particle) achieves the Hospital's Minimum Preference i.e. On How many days in the schedule was this achieved
    PREFERENCE SET BY: preference - e.g. (4,2,2,2) means MINIMUM of 4 nurses - OFF, 2 - MORNING, 2-EVENING, 2-NIGHT
    EXTRA: Coarse_grained: checks if all shift type and offs on a day simulataneously satisfy their corresponding requirement.
    NORMALIZATION: The result is normalized over all DAYS
    ''')
        self.C2A1= Fit.Const_Fxn(c.C2A1,self,viol_Type=('D',1,1,1,1), Default_Weight=0,
        Description='''It is a violation-showing fitness function that expresses one of the Soft Constraints C2.
    CHECKS:By how much does the schedule (particle) achieves the Hospital's Minimum Preference i.e. On How many days in the schedule was this achieved
    PREFERENCE SET BY: preference - e.g. (4,2,2,2) means MINIMUM of 4 nurses - OFF, 2 - MORNING, 2-EVENING, 2-NIGHT
    EXTRA: Fine-Grained: Checks if each shift type on each day satisfy their corresponding requirement independently
    NORMALIZATION: The result is normalized over all DAYS and their SHIFTS
    ''')
        self.C2B = Fit.Const_Fxn(c.C2B,self,viol_Type=('D',),Default_Weight=0,
        Description='''It is a violation-showing fitness function that expresses one of the Soft Constraints C2.
    CHECKS:By how much does the schedule (particle) achieves HALF OF the Hospital's Minimum Preference i.e. On How many days in the schedule was this achieved
    PREFERENCE SET BY: preference - e.g. (4,2,2,2) means MINIMUM of 4 nurses - OFF, 2 - MORNING, 2-EVENING, 2-NIGHT
    EXTRA: Coarse-grained: Checks if all shift type and offs on each day simultaneously satisfy HALF the requirement
    NORMALIZATION: The result is normalized over all DAYS
    ''')
        self.C2B1 = Fit.Const_Fxn(c.C2B1,self,viol_Type=('D',1,1,1,1),Default_Weight=0,
        Description='''It is a violation-showing fitness function that expresses one of the Soft Constraints C2.
    CHECKS:By how much does the schedule (particle) achieves HALF OF the Hospital's Minimum Preference i.e. On How many days in the schedule was this achieved
    PREFERENCE SET BY: preference - e.g. (4,2,2,2) means MINIMUM of 4 nurses - OFF, 2 - MORNING, 2-EVENING, 2-NIGHT
    EXTRA: Fine-Grained: Checks if each shift type on each day satisfty HALF the corresponding requirement independently
    NORMALIZATION: The result is normalized over all DAYS and SHIFT
    ''')
        self.C3 = Fit.Const_Fxn(c.C3,self,viol_Type=('N',1,0,0,0),Default_Weight=1,
        Description='''It is a violation-showing fitness function that expresses one of the Soft Constraints C3.
    CHECKS: If a nurse has a minimum of one OFF (all work and no rest is a violation) 
    NORMALIZATION: The result is normalized over all NURSES
    ''')
        self.C4 = Fit.Const_Fxn(c.C4,self,viol_Type=('D','E'),Default_Weight=0,
        Description='''It is a violation-showing fitness function that expresses one of the Soft Constraints C4.
    CHECKS: For how many working shift in this schedule do we have at least "MINIMUM" experienced nurses assigned
    MINIMUM SET BY: min_experienced_nurse_per_shift e.g. =1 means at least one of the experienced nurses must be assigned to both M, E and N shift for each day to fulfil requirement
    EXTRA: Only checks by day, any shift that has no experienced nurse, renders the day a violation
    NORMALIZATION: The result is normalized over all DAYS
    ''')
        self.C4B = Fit.Const_Fxn(c.C4B,self,viol_Type=('D','E',0,1,1,1),Default_Weight=1,
        Description='''It is a violation-showing fitness function that expresses one of the Soft Constraints C4.
    CHECKS: For how many working shift in this schedule do we have at least "MINIMUM" experienced nurses assigned
    MINIMUM SET BY: min_experienced_nurse_per_shift e.g. =1 means at least one of the experienced nurses must be assigned to each shift for that shift to fulfil requirement
    EXTRA: fine-grained, each shift make independent contribution to the fitness fxn
    NORMALIZATION: The result is normalized over all DAYS and their SHIFTS
    ''')
        self.C5 = Fit.Const_Fxn(c.C5,self,viol_Type= (None,),Default_Weight=1,
        Description='''It is a violation-showing fitness function that expresses one of the Soft Constraints C5.
    CHECKS: How many night shift in the schedule (particle) is immediately followed by an OFF 
    NORMALIZATION: The result is normalized over all NIGHT SHIFT
    ''')
        self.C6 = Fit.Const_Fxn(c.C6,self,viol_Type=('N',0,0,0,1),Default_Weight=1,
        Description='''It is a violation-showing fitness function that expresses one of the Soft Constraints C6.
    CHECKS: If the night shifts in the schedule (particle) is greater than MINIMUM
    MINIMUM SET BY: min_night_per_nurse: e.g =3/14 means that we have minimum of 3 nights per two weeks 
    NORMALIZATION: The result is normalized over all NURSES
    ''')
        self.H23 = Fit.Fitness(c.cons,self,is_obj_fxn=True)
        self.hard_con_dict = dict(H2=self.H2,H3=self.H3)
        self.soft_con_dict = dict(C1=self.C1, C2A=self.C2A, C2A1=self.C2A1, C2B=self.C2B, C2B1=self.C2B1, C3=self.C3, C4=self.C4, C4B=self.C4B, C5=self.C5, C6=self.C6)
        part_Holder.__init__(self,Fitness=Fit.Fitness_Fxn(self))
        self.fitt.description += '\n   This is the Fitness function suspected to be used by the author of the article "Solving complex NSP using PSO C1 4,C2A 4,C2A1 0,C2B 0,C2B1 0,C3 1,C4 0,C4B 1,C5 1,C6 1"'
        self.curr_search = None
        self.prev_searches= {}
        self.curr_search_name = 'Curr_Search'
        self.self_name = 'NSP_default'
        self.particles['Random_Particle 1'] = self.create_rand_particle()
        self.particles['Random_Particle 2'] = self.create_rand_particle()
        self.particles['Random_Particle 3'] = self.create_rand_particle()
        if self.is_default():
            self.particles['The Best'] = np.array([2,1,1,0,0,3,0,3,0,1,3,2,0,2,
                                                    2,2,3,2,0,1,0,3,3,0,1,0,0,1,
                                                    3,3,0,3,0,0,2,0,2,0,2,1,1,1,
                                                    0,1,0,2,3,0,3,0,3,0,1,1,2,2,
                                                    1,0,0,1,1,0,3,2,0,2,2,3,0,3,
                                                    0,0,2,1,3,0,2,0,1,1,0,2,3,3,
                                                    3,0,0,3,0,2,0,0,2,2,3,0,1,0,
                                                    1,3,2,0,2,3,0,1,0,3,0,0,2,0,
                                                    0,0,3,0,2,2,1,1,0,3,0,3,0,0,
                                                    0,2,1,0,1,1,1,2,1,0,0,0,3,0])

        self.man_fitt ={}
