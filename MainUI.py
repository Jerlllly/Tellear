from tkinter import *
import tkinter.filedialog
import os
from Assembler import Assembler
from Parser import Parser
from Lexer import Lexer

global file_name
global content
def lexer():
    global content
    lexer=Lexer()
    lexer.main(content)
    buffer=[]
    for token in lexer.tokens:
        #print ('(%s, %s)' % (token.type, token.value))
        buffer.append('(%s, %s)' % (token.type, token.value))
    return buffer
def parser():
    global content
    parser = Parser(content)
    parser.main()
    parser.display(parser.tree.root)
    return
def assembler():
    global file_name
    global content
    assem = Assembler(content)
    assem.traverse(assem.tree.root)
    assem.ass_file_handler.generate_ass_file(file_name)
def openfile(t1):
    t1.delete(0.0,END)
    global content
    global file_name
    file_name = tkinter.filedialog.askopenfilename()
    source_file = open(file_name, 'r')
    content = source_file.read()
    t1.insert(END,content)
def prelex(t2):
    t2.delete(0.0,END)
    buffer=lexer()
    str1='\n'.join(buffer)
    t2.insert(END,str1)
def prepars(t2):
    t2.delete(0.0, END)
    parser()
    f=open('tree.txt','r')
    str3=f.read()
    t2.insert(END, str3)
    f.close()
    os.remove("tree.txt")
def preassembl(t2):
    global file_name
    t2.delete(0.0, END)
    assembler()
    f=open(file_name[0:-2]+'.txt','r')
    str4=f.read()
    t2.insert(END,str4)
    f.close()
    os.remove(file_name[0:-2]+'.txt')
def prerun():
    global file_name
    shell=''
    shell='gcc -m32 '+file_name[0:-2]+'.S '+'-o '+file_name[0:-2]+'.out'
    os.system(shell)
    shell=file_name[0:-2]+'.out'
    os.system(shell)

if __name__ == '__main__':
    # 定义一个顶级大窗口
    root = Tk()
    root.geometry('1400x450')
    root.iconbitmap('./icon.ico')
    root.title('Tellear')
    # 在大窗口下定义一个顶级菜单实例
    menubar = Menu(root)

    fmenu = Menu(menubar)
    fmenu.add_command(label="打开", command=lambda:openfile(t1), accelerator='Ctrl+O')

    amenu = Menu(menubar)
    amenu.add_command(label='词法分析',command=lambda:prelex(t2))
    amenu.add_command(label='语意分析', command=lambda:prepars(t2))

    rmenu = Menu(menubar)
    rmenu.add_command(label='编译', command=lambda:preassembl(t2))
    rmenu.add_command(label='执行', command=prerun)

    menubar.add_cascade(label='文件', menu=fmenu)
    menubar.add_cascade(label='分析', menu=amenu)
    menubar.add_cascade(label='编译执行', menu=rmenu)
    # 顶级菜单实例应用到大窗口中
    root['menu'] = menubar
    s1 = tkinter.Scrollbar()
    s2 = tkinter.Scrollbar()
    t1 = Text(root,width=80,height=30)
    t2 = Text(root, width=80, height=30)
    l1 = Label(root, text='C语言程序')
    l2 = Label(root, text='分析区域')
    t1.grid(column=0,row=0,padx=100)
    t2.grid(column=1,row=0,padx=0)
    s1.config(command=t1.yview)
    s2.config(command=t2.yview)
    t1.config(yscrollcommand=s1.set)
    t2.config(yscrollcommand=s2.set)
    l1.grid()
    l2.grid(row=1,column=1,sticky=S,pady=0)
    s1.grid(row=0,column=0,sticky=E+N+S,padx=84)
    s2.grid(row=0, column=0, sticky=N+S+E, padx=0)
    root.mainloop()
