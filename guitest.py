from tkinter import *
root=Tk()
Label(root,text='Adat').pack()
t1=Text(root, height=20, width=80)
t1.pack()
'''
def value(t):
    x=t.get('1.0','end-1c')
    return x
'''

def submit():
    a=value(t1)
    print(a)


Button(root, text='Küldés', command=submit).pack()
mainloop()
