from tkinter import *
import numpy as np

root = Tk()

Nsp_Problem = dict(no_of_days=4,nurses_no=6,experienced_nurses_no=3)

def buildManEnter(root, nurses_no, no_of_days,experienced_nurses_no):
    ManEnter = Toplevel(root) 
    part_sub_var=[]
    for i in range(0,no_of_days + 1):
        if i:
            Label(ManEnter,text='Day %s'%str(i)).grid(row=i,column=0)
        else:
            Label(ManEnter,text = 'Day\\Nurses').grid(row=0,column=0)
        
        for j in range(1,nurses_no + 1):
            if not i:
                Label(ManEnter,text='N%s '%str(j)).grid(row=i,column=j)
            elif j<=experienced_nurses_no:
                r= StringVar()
                Entry(ManEnter, width='3', bg='green', fg='white', textvariable=r).grid(row=i,column=j)
                part_sub_var.append(r)
            else:
                r= StringVar()
                Entry(ManEnter, width='3', textvariable=r).grid(row=i,column=j)
                part_sub_var.append(r)
        
    Button(ManEnter,text='Close',command= lambda: close_manual()).grid(row=no_of_days +1,column=0, columnspan= int(nurses_no/2)+1, padx =1, pady=3,sticky=E)
    
    Button(ManEnter,text='Submit', command= lambda a=part_sub_var, b=nurses_no,c=experienced_nurses_no, d=no_of_days: submit_manual(a,b,c,d)  ).grid(row=no_of_days +1,column= int(nurses_no/2)+1, columnspan= int(nurses_no/2)+1, padx =1, pady=3, sticky= W)   
    
def close_manual():
    pass
def submit_manual(part_sub_var,nurses_no, experienced_nurses_no,no_of_days ):
    CharToInt = {'O':0, 'M':1, 'E':2, 'N':3}
    
    emptErr =[i for i, m in enumerate(part_sub_var) if m.get()=='']
    errSyntax = [i for i, m in enumerate(part_sub_var) if m.get().upper() not in CharToInt.keys()]

    if(len(emptErr)):
        print('Syntax Error: ', len(emptErr), ' cells out of ',no_of_days*nurses_no, ' cells empty')
        if(len(errSyntax)-len(emptErr)):print('Syntax Error: ',len(errSyntax) - len(emptErr), ' wrong entries found')        
    elif(len(errSyntax)-len(emptErr)):print('Syntax Error: ',len(errSyntax) - len(emptErr), ' wrong entries found')
    else:
        inter = [CharToInt[r.get().upper()] for r in part_sub_var]
        x = np.array(inter)
        x = x.reshape(no_of_days,nurses_no)
        x = np.transpose(x)
                
        print('Solved: ',x )



    # root.transient(ManEnter)

buildManEnter(root,**Nsp_Problem)
root.mainloop()

