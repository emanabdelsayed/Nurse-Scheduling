import numpy as np
from functools import partial
from Search import Search

def Hard_Viol(x, m, *args):
    S = m(x, *args)
    S = S==0
    S = S.ravel()
    return S
    
def create_pattern(nurses_no,no_of_days):
    f = lambda m: m%2
    A = np.fromfunction(f,(no_of_days,), dtype=int)
    A = np.array(A,dtype=bool)        
    B = np.vstack([A for x in range(nurses_no)])
    return B.ravel()

def regenerat(x,fit_args,lst_Hard,lb=0,ub=4):
    tmp=x.copy()
    for m in lst_Hard:
        ser = Hard_Viol(tmp,m,*fit_args)
        while ser.sum():
            tmp[ser] = np.random.randint(lb,ub,ser.sum())
            ser = Hard_Viol(tmp,m,*fit_args)
    return tmp

class regen_gen_algo(Search):
    def start(self):
        Search.start(self)
        self.search()
        self.after_ended()
        
    def regenerate(self):
        xn = self.x.copy()
        for i in range(self.S):
            tmp = xn[i]
            undone = True
            while(undone): #This ensures that if fulfiling a violation triggers another violation, there will still be a correction chance
                undone = False
                for m in self.lst_Hard():
                    ser = Hard_Viol(tmp,m,*self.get_fit_args())
                    while ser.sum():
                        undone = True
                        tmp[ser] = np.random.randint(self.lb,self.ub,ser.sum())
                        ser = Hard_Viol(tmp,m,*self.get_fit_args())
            xn[i] =tmp
        self.x = xn
    def regenerate_itera(self):
        self.regenerate()

    def calc_Fitness(self):
        fxm = self.fx.copy()
        for i in range(len(fxm)):
            fxm[i] = self.get_obj_fxn()(self.x[i],*self.get_fit_args())
        self.fx = fxm
    def pair_selection(self,arg_eligible = None):
        if isinstance(arg_eligible,(np.ndarray,list)):
            a = arg_eligible #arg_where
            pp = 1 -self.fx[a]
        else:
            a = np.arange(self.S)
            pp = 1 -self.fx
        pp = pp/pp.sum()
        choice = np.random.choice(a, (self.S,2), p=pp)
        return choice
    
    def cross_over(self, pattern, choice):
        xn = self.x.copy()
        for i in range(self.S):
            tmp1 = self.x[choice[i,0]].copy()
            tmp2 = self.x[choice[i,1]].copy()
            xn[i,pattern] = tmp1[pattern]
            xn[i,~pattern] = tmp2[~pattern]
        self.x = xn

    def random_mutation(self):
        if 0 < self.mut_prob <= 1:
            choice = np.random.choice([True,False],(self.S,self.D()),p=[self.mut_prob, 1-self.mut_prob])
            self.x[choice] = np.random.randint(self.lb,self.ub,choice.sum())

    def update_best(self,ite,arg_eligible=None):
        if isinstance(arg_eligible,(np.ndarray,list)):            
            if len(arg_eligible):
                fx = self.fx[arg_eligible]
                i_min = np.argmin(fx)
            else:
                return None
        else:
            fx = self.fx
            i_min = np.argmin(fx)
        if(self.fx[i_min] < self.fg):
            g= self.x[i_min,:].copy()
            fg = self.fx[i_min]
            self.new_best(ite,g,fg)
            return True

    def search(self):
        maxiter = self.maxite
        self.regenerate()
        self.calc_Fitness()
        self.update_best(0)
        pattern = create_pattern(self.get_nurses_no(),self.get_no_of_days())
        self.new_msg(0,'initialized','Succesfully initialized')
        itera = 1
        while itera <= maxiter:
            choice = self.pair_selection()
            self.cross_over(pattern,choice)
            self.random_mutation()
            self.regenerate_itera()
            self.calc_Fitness()
            self.update_best(itera)
            maxiter += self.ite_changed(itera,maxiter,self.fx,x=self.x,g=self.g,fg=self.fg)
            itera += 1
        self.new_msg(itera-1,'ended','Successfully ended at %s'%(itera-1))

    def lst_Hard(self):
        return self.nsp.get_Hard_Viol_fxns()

    def __init__(self,lb,ub,pop_size,mutation_probability,nsp,Fitness,maxite,pre_begin = False):
        Search.__init__(self,maxite,Fitness,nsp)
        self.lb = lb
        self.ub = ub
        self.S = pop_size
        self.mut_prob = mutation_probability 
        self.x = np.random.randint(lb,ub,(self.S,self.D()))
        self.fx = np.ones(self.S)*np.inf
        self.g=[]
        self.fg=np.inf
        if pre_begin:
            self.BEGIN()

def lst_H_cons_wrapper(func_lst,args,x):
    return np.array([func(x,*args) for func in func_lst])

def is_feasible_wrapper(func,x):
    return np.all(func(x)>=0)

class allowance_gen_algo(regen_gen_algo):
    def __init__(self,lb,ub,pop_size,mutation_probability,nsp,Fitness,maxite,allow_prob=0.1,regen_init = True,pre_begin=False):
        regen_gen_algo.__init__(self,lb,ub,pop_size,mutation_probability,nsp,Fitness,maxite,pre_begin=pre_begin)
        hard_Lst =[a.obj_fxn for a  in self.nsp.hard_con_dict.values()]
        hcons = partial(lst_H_cons_wrapper,hard_Lst,self.nsp.get_fitness_args())
        self.is_feasible = partial(is_feasible_wrapper,hcons)
        self.fs = np.zeros(self.S,dtype=bool)
        if 0 <= allow_prob <= 1:
            self.toler = allow_prob
        else: raise ValueError('Invalid value for allow_prob')
        self.regen_init = regen_init
        self.man = int(self.toler * self.S)
        if self.man < 2:
            self.man = 2
    def calc_Fitness(self):
        fxm = self.fx.copy()
        fs = self.fs.copy()
        for i in range(len(fxm)):
            fxm[i] = self.get_obj_fxn()(self.x[i],*self.get_fit_args())
            fs[i] = self.is_feasible(self.x[i])
        self.fx = fxm
        self.fs = fs
    def pair_selection(self):
        man = self.man
        kal = np.argsort(self.fx)
        kal = kal[:man]
        twal = (np.nonzero(self.fs))[0] #the legitimate
        eli = np.unique(np.concatenate((kal,twal)))
        errf = (np.nonzero(np.isfinite(self.fx)))[0]
        real_eli = np.intersect1d(eli,errf)
        if len(real_eli) >= man:
            return regen_gen_algo.pair_selection(self,arg_eligible=real_eli)
        else:
            return regen_gen_algo.pair_selection(self)
    def regenerate_itera(self):
        pass
    def regenerate(self):
        if self.regen_init:
            regen_gen_algo.regenerate(self)
        else:
            pass
    def update_best(self,ite):
        eli = np.nonzero(self.fs)[0]            
        regen_gen_algo.update_best(self,ite,arg_eligible=eli)