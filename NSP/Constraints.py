import numpy as np

def cons(x,*args):
    max_night_per_day, nurses_no, no_of_days = args[:3]
    
    if x.dtype == int:
        k = (x==3)
    else:
        k = np.logical_and(x>3, x<=4)    
    l= np.append(x,3)
    l = np.delete(l,0)
    m = np.logical_and(l>=1, l<2)
    n = np.logical_and(k,m)
    n = -1 *np.reshape(n, (nurses_no,no_of_days))
    k= 1 *np.reshape(k, (nurses_no,no_of_days))
    p = k[:,:-1].sum()
    if p==0:
        H2=0
    else:
        H2 = n[:,:-1].sum()/p
    k = k.sum(axis =1)
    o = max_night_per_day < (k/no_of_days) 
    o = o * -1
    H3 = o.sum()
    return H2,H3
def H2(x,*args):
    max_night_per_day, nurses_no, no_of_days = args[:3]
    if x.dtype == int:
        k = (x==3)
    else:
        k = np.logical_and(x>3, x<=4)    
    p= np.reshape(k,(nurses_no,no_of_days))
    p= p[:,:-1]
    y = np.zeros(nurses_no,dtype=bool)[:,np.newaxis]
    truu = p.copy()
    truu = np.hstack((y,truu))
    back = np.ones(truu.shape)*-1
    l= np.append(x,3)
    l = np.delete(l,0)#shift next day backwards
    m = np.logical_and(l>=1, l<2) #morning shift nxt day
    n = np.logical_and(k,m) #these are the violations
    ret = np.reshape(n,(nurses_no,no_of_days))
    ret = ret[:,:-1]
    reti = np.hstack((y,ret))
    back[truu] = 1
    back[reti] = 0
    n = -1 *np.reshape(n, (nurses_no,no_of_days)) #outliers
    k= 1 *np.reshape(k, (nurses_no,no_of_days))
    p= p.sum()
    if args[-1]:
        return np.array(back,dtype=int)
    else:
        if p==0:
            H2=0
        else:
            H2 = n[:,:-1].sum()/p
        return H2

def H3(x, *args):
    max_night_per_day, nurses_no, no_of_days = args[:3]
    if x.dtype == int:
        k = (x==3)
    else:
        k = np.logical_and(x>3, x<=4)
    k = np.reshape(k,(nurses_no,no_of_days))
    ret = k.sum(axis=1)/no_of_days <= max_night_per_day
    if args[-1]:
        return ret
    else:
        return ret.sum()/nurses_no - 1

def H3b(x, *args):
    max_night_per_day, nurses_no, no_of_days = args[:3]
    if x.dtype == int:
        k = (x==3)
    else:
        k = np.logical_and(x>3, x<=4)
    k = np.reshape(k,(nurses_no,no_of_days)) 
    R = k.sum(axis=1)/no_of_days 
    M = R <= max_night_per_day
    Fin = R.copy()
    nn,rr = k.copy(), k.copy()
    nn[rr] = False
    nn[M,:] = np.logical_or(nn[M,:],True)
    nn=nn*1
    nn[~rr] = -1
    Fin[M]=0
    rat = 1-max_night_per_day
    Fin[~M] = (R[~M]-max_night_per_day)/rat
    if args[-1]:
        return nn
    else:
        return Fin.sum()/nurses_no * -1
def C1(x, *args):
    nurses_no, no_of_days= args[1:3]
    h= np.reshape(x,(nurses_no, no_of_days))
    o = np.logical_and(h>=0, h<1).sum(axis=1)
    m = np.logical_and(h>=1, h<2).sum(axis=1)
    if x.dtype == int:
        e = (h==2).sum(axis=1)
        n = (h==3).sum(axis=1)
    else:
        e = np.logical_and(h>=2, h<=3).sum(axis=1)
        n = np.logical_and(h>3, h<=4).sum(axis=1)
    tar = np.transpose(np.vstack((o,m,e,n)))
    rea = np.unique(tar, axis=0) 
    j= np.array([])
    for grt in rea:
        j = np.append(j,(np.sum(np.sum(tar==grt,axis=1)==4)))
    if args[-1]:
        yy = np.argmax(j)
        return np.sum(tar==rea[yy,:],axis=1)==4
    else:
        return np.max(j)/nurses_no

def C2A(x, *args):
    nurses_no, no_of_days,preferences = args[1:4]
    h= np.reshape(x,(nurses_no,no_of_days))
    o = np.logical_and(h>=0, h<1).sum(axis=0)
    m = np.logical_and(h>=1, h<2).sum(axis=0)
    if x.dtype == int:
        e = (h==2).sum(axis=0)
        n = (h==3).sum(axis=0)
    else:
        e = np.logical_and(h>=2, h<=3).sum(axis=0)
        n = np.logical_and(h>3, h<=4).sum(axis=0)
    tar = np.transpose(np.vstack((o,m,e,n)))
    ret = np.sum(tar >= np.array(preferences), axis=1)==4
    if args[-1]:
        return ret
    else:
        return ret.sum()/no_of_days
def C2A1(x, *args):
    nurses_no, no_of_days,preferences = args[1:4]
    h= np.reshape(x,(nurses_no,no_of_days))
    o = np.logical_and(h>=0, h<1).sum(axis=0)
    m = np.logical_and(h>=1, h<2).sum(axis=0)
    if x.dtype == int:
        e = (h==2).sum(axis=0)
        n = (h==3).sum(axis=0)
    else:
        e = np.logical_and(h>=2, h<=3).sum(axis=0)
        n = np.logical_and(h>3, h<=4).sum(axis=0)
    tar = np.transpose(np.vstack((o,m,e,n)))
    ret = tar >= np.array(preferences)
    if args[-1]:
        return ret
    else:
        return ret.sum()/(4*no_of_days)
def C2B(x, *args):
    nurses_no, no_of_days,preferences = args[1:4]
    pref=[]
    for w in preferences:
        qwi = int(w/2)
        if qwi >= 1:
            pref.append(qwi)
        else:
            pref.append(1)
    preferences = tuple(pref)
    h= np.reshape(x,(nurses_no,no_of_days))
    o = np.logical_and(h>=0, h<1).sum(axis=0)
    m = np.logical_and(h>=1, h<2).sum(axis=0)
    if x.dtype == int:
        e = (h==2).sum(axis=0)
        n = (h==3).sum(axis=0)
    else:
        e = np.logical_and(h>=2, h<=3).sum(axis=0)
        n = np.logical_and(h>3, h<=4).sum(axis=0)
    tar = np.transpose(np.vstack((o,m,e,n)))
    ret = np.sum(tar >= np.array(preferences), axis=1)==4 
    if args[-1]:
        return ret
    else:
        return ret.sum()/no_of_days
def C2B1(x, *args):
    nurses_no, no_of_days,preferences = args[1:4]
    pref=[]
    for w in preferences:
        qwi = int(w/2)
        if qwi >= 1:
            pref.append(qwi)
        else:
            pref.append(1)
    preferences = tuple(pref)
    h= np.reshape(x,(nurses_no,no_of_days))
    o = np.logical_and(h>=0, h<1).sum(axis=0)
    m = np.logical_and(h>=1, h<2).sum(axis=0)
    if x.dtype == int:
        e = (h==2).sum(axis=0)
        n = (h==3).sum(axis=0)
    else:
        e = np.logical_and(h>=2, h<=3).sum(axis=0)
        n = np.logical_and(h>3, h<=4).sum(axis=0)
    tar = np.transpose(np.vstack((o,m,e,n)))
    ret = tar >= np.array(preferences)
    if args[-1]:
        return ret
    else:
        return ret.sum()/(4*no_of_days)
    
def C3(x,*args):
    nurses_no, no_of_days = args[1:3]

    t= np.reshape(x,(nurses_no,no_of_days))
    r = np.sum(np.logical_and(t>=0,t<1), axis=1)
    ret = r > 0
    if args[-1]:
        return ret
    else:
        return np.sum(ret)/nurses_no
def C4(x,*args):
    nurses_no,no_of_days,exp_nurses_no,min_exp_nurses_per_wshift = *args[1:3],*args[4:6]
    h = np.reshape(x,(nurses_no,no_of_days))
    h = h[:exp_nurses_no,:]
    m = np.logical_and(h>=1, h<2).sum(axis=0)
    if x.dtype == int:
        e = (h==2).sum(axis=0)
        n = (h==3).sum(axis=0)
    else:
        e = np.logical_and(h>=2, h<=3).sum(axis=0)
        n = np.logical_and(h>3, h<=4).sum(axis=0)

    tar = np.transpose(np.vstack((m,e,n)))
    c = min_exp_nurses_per_wshift
    ret = np.sum(tar >= c, axis=1) == 3
    if args[-1]:
        return ret
    else:
        return ret.sum()/no_of_days

def C4B(x,*args):
    nurses_no,no_of_days,exp_nurses_no,min_exp_nurses_per_wshift = *args[1:3],*args[4:6]
    h = np.reshape(x,(nurses_no,no_of_days))
    h = h[:exp_nurses_no,:]
    m = np.logical_and(h>=1, h<2).sum(axis=0)
    if x.dtype == int:
        e = (h==2).sum(axis=0)
        n = (h==3).sum(axis=0)
    else:
        e = np.logical_and(h>=2, h<=3).sum(axis=0)
        n = np.logical_and(h>3, h<=4).sum(axis=0)
    tar = np.transpose(np.vstack((m,e,n)))
    ret = tar >= min_exp_nurses_per_wshift
    if args[-1]:
        return ret
    else:
        return ret.sum()/(3*no_of_days)

def C5(x,*args):
    nurses_no, no_of_days = args[1:3]

    if x.dtype == int:
        ln = x==3
    else:
        ln = np.logical_and(x>3,x<=4)
    lo = np.append(x,-1) 
    lo = np.delete(lo,0)
    lo = np.logical_and(lo>=0,lo<1) 
    ln = ln.reshape(nurses_no, no_of_days)
    lo= lo.reshape(nurses_no,no_of_days)

    ln = ln[:,:-1] 
    lo= lo[:,:-1]
    
    y = np.zeros(nurses_no,dtype=bool)[:,np.newaxis]
    truu = ln.copy()
    truu = np.hstack((y,truu))
    back = np.ones(truu.shape)*-1    

    tar = np.transpose(np.vstack((ln.ravel(),lo.ravel())))
    w = np.sum(ln)
    ret = np.reshape(np.sum(tar,axis=1)==2,(nurses_no,no_of_days-1))
    
    reti = np.hstack((y,ret))
    back[truu] = 0
    back[reti] = 1
    
    if not args[-1]:
        if(w==0):
            return 0
        else:
            return ret.sum()/w 
    else:
        return back

def C6(x,*args):
    nurses_no, no_of_days, min_night_per_day= *args[1:3],args[6]
    
    if(x.dtype == int):
        f = x==3
    else:
        f = np.logical_and(x>3,x<=4)

    l = np.reshape(f,(nurses_no,no_of_days))
    h = np.sum(l,axis=1) 
    ret = (h/no_of_days) >= min_night_per_day

    if (args[-1]):
        return ret
    else:
        return np.sum(ret)/nurses_no

if __name__ == '__main__':

    g_goal = np.array([2,3,1,3,0,3,0,3,0,1,3,2,0,2,
        2,2,3,2,0,1,0,3,3,0,1,0,0,1,
        3,3,3,3,0,0,2,0,2,3,2,1,1,1,
        0,1,3,2,3,0,3,3,3,0,1,1,2,2,
        1,0,3,1,1,0,3,2,0,2,2,3,0,3,
        0,0,2,1,3,0,2,0,1,1,0,2,3,3,
        3,0,0,3,0,2,0,0,2,2,3,0,1,0,
        1,3,2,0,2,3,0,1,0,3,0,0,2,0,
        0,0,3,0,2,2,1,1,0,3,0,3,0,0,
        0,2,1,0,1,1,1,2,1,0,0,0,3,0])

    randomer = [1,3,2,1,2,2,1,1,3,3,3,2,3,1,
                2,2,3,2,2,1,2,3,3,2,1,2,3,3,
                1,2,1,3,2,1,3,3,2,1,2,2,1,2,
                1,3,2,1,3,2,3,2,2,1,2,3,3,2,
                
                ]
    ran =np.random.randint(0,4,10*14)
    g = ran

    print(np.reshape(g,(10,14)))
    print(C1(g,3/14,10,14,(4,2,2,2),4,1,3/14, False))
    print(C2A(g,3/14,10,14,(4,2,2,2),4,1,3/14,False))
    print(C3(g,3/14,10,14,(4,2,2,2),4,1,3/14,False))
    print(C4B(g,3/14,10,14,(4,2,2,2),4,1,3/14,False))
    print('C5 here',1 * (C5(g,3/14,10,14,(4,2,2,2),4,1,3/14,True)==1))
    print(C6(g,3/14,10,14,(4,2,2,2),4,1,3/14,False))

    v = H3b(g,3/14,10,14,(4,2,2,2),4,1,3/14,False)
    while v<0:
        print(v)
        m =H3b(g,3/14,10,14,(4,2,2,2),4,1,3/14,True)
        print(m)
        m= m==0
        m= m.ravel()
        g[m]= np.random.randint(0,4,m.sum())
        v = H3b(g,3/14,10,14,(4,2,2,2),4,1,3/14,False)
        print(np.reshape(g,(10,14)))
    print(v)

    print('\n\n\n\n\n')

    v = H2(g,3/14,10,14,(4,2,2,2),4,1,3/14,False)
    while v<0:
        print(v)
        m =H2(g,3/14,10,14,(4,2,2,2),4,1,3/14,True)
        print(m)
        m= m==0
        m= m.ravel()
        g[m]= np.random.randint(0,4,m.sum())
        v = H2(g,3/14,10,14,(4,2,2,2),4,1,3/14,False)
        print(np.reshape(g,(10,14)))
    print(v)
    print(H2(g,3/14,10,14,(4,2,2,2),4,1,3/14,False))
