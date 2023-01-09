class Fitness:
    def opp_fxn(self,x,*args):
        m = self.Original_fxn(x,*args)
        if isinstance(m,tuple):
            together =()
            for y in m:
                together = together + (1-y,)
            return together
        else:
            return 1 - m

    def obj_fxn(self,x,*args):
        if self.is_obj_fxn:
            return self.Original_fxn(x,*args)
        else:
            return self.opp_fxn(x,*args)
        

    def check_fit(self,x,*args):
        if self.is_obj_fxn:
            return self.opp_fxn(x,*args)
        else:
            return self.Original_fxn(x,*args)

    def __init__(self,fxn,NS_problem,is_obj_fxn=False,Description="This is a fitness function"):
        self.description = Description
        self.Original_fxn = fxn
        self.is_obj_fxn = is_obj_fxn
        from Prob import NSP
        if isinstance(NS_problem,NSP):
            self.NS_problem = NS_problem
        else:
            raise TypeError('NS_problem must be a valid instance of NSP()')

class Const_Fxn(Fitness):
    all_const = {}
    count = 0
    all_weight ={}
    violations=dict(nd2=None,n='N',d='N',n1=('N',1,1,1,1), d1=('D',1,1,1,1),d1_s=('D',0,1,1,1),n1_o=('N',1,0,0,0,), n1_n=('N',0,0,0,1)) 
    def __new_fxn__(self, x, *args):
        return self.__viol_fxn(x, *args,False)
    def viol_fxn(self,x, *args):
        return self.__viol_fxn(x, *args, True)
    def opp_fxn(self,x,*args):
        if self.is_Hard:
            m = self.Original_fxn
            return -1 *(1 + m(x,*args))
        else:
            return Fitness.opp_fxn(self,x,*args)
    def __init__(self,fxn,Ns_problem,is_Hard=False,is_obj_fxn=False,Description="This is a Constrained fitness fxn, with ability to show violations", viol_Type= None,Default_Weight =1):
        self.__viol_fxn= fxn
        self.viol_Type = viol_Type
        self.is_Hard = is_Hard
        Fitness.__init__(self,self.__new_fxn__,Ns_problem,is_obj_fxn=is_obj_fxn,Description=Description)
        name = str(fxn.__name__) + ' ' + str(Const_Fxn.count)
        Const_Fxn.all_const[name] = self
        Const_Fxn.all_weight[name] = Default_Weight
        Const_Fxn.count +=1
class Fitness_Fxn(Fitness):
    def __fit_fxn__(self,x,*args):
        kg_sum=0
        summ=0
        for m in self.Const.keys():
            if m in self.weights.keys():
                kg_sum += self.weights[m]
                summ += self.weights[m]*self.Const[m].check_fit(x,*args)
        if kg_sum:
            return summ/kg_sum

    def __init__(self, NS_problem,Description="This is type of Fitness fxn whose fitness is obtained from the wieghted mean of other fitness fxns",const_fxns =Const_Fxn.all_const, weights=Const_Fxn.all_weight):
        self.Const = const_fxns
        self.weights = weights
        Fitness.__init__(self,self.__fit_fxn__,NS_problem,is_obj_fxn = False,Description=Description)