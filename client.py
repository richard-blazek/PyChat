import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import time
import sockets

def append_text(out, *texts):
    out.config(state=tk.NORMAL)
    for pair in texts:
        out.insert(tk.END, *pair)
    out.config(state=tk.DISABLED)

def get_nickname():
    while True:
        var=simpledialog.askstring("Zadání", "Zadej přezdívku, pod kterou tě uvidí ostatní")
        if var and len(var)<=15:
            break
        messagebox.showwarning("Chybné zadání", "Přezdívka může mít nejvýše 15 znaků")
    return var

s=sockets.connect(sys.argv[1] if len(sys.argv)>1 else '127.0.0.1', 5000, False)

window=tk.Tk()
text_output=tk.Text(window)
text_output.config(state=tk.DISABLED)
text_output.tag_config('msginfo', foreground='red')
text_output.tag_config('yourtext', foreground='blue')
intext=tk.StringVar()
text_entry=tk.Entry(window, textvariable=intext)
flagtext=tk.StringVar()
flaglabel=tk.Label(window, textvariable=flagtext)

lasttext=''
wastyping=False

def send():
    global lasttext
    if intext.get()!='':
        s.send_json({'message':intext.get(), 'nick':nick})
        append_text(text_output, ['You'+'>', 'msginfo'], [intext.get()+'\n', 'yourtext'])
        intext.set('')
        lasttext=''

button=tk.Button(window, text='Send', command=send)
text_entry.bind('<Return>', lambda x:send())

def change():
    global lasttext, wastyping
    if lasttext!=intext.get() and not wastyping:
        s.send_json({'istyping': True, 'nick':nick})
        wastyping=True
    elif lasttext==intext.get() and wastyping:
        s.send_json({'istyping': False, 'nick':nick})
        wastyping=False
    lasttext=intext.get()

def show():
    recieved=s.recv_json()
    if recieved==sockets.CLOSED:
        window.destroy()
        return
    for value in recieved:
        if 'message' in value:
            if value['message']!='':
                append_text(text_output, [value['nick']+'>', 'msginfo'], [value['message']+'\n'])
        elif 'istyping' in value:
            flagtext.set(value['nick']+' is typing...' if value['istyping'] else '')
        elif 'login' in value:
            append_text(text_output, ["'"+value['login']+"'"+' has logged in\n', 'msginfo'])
        elif 'logout' in value:
            append_text(text_output, ["'"+value['logout']+"'" + ' has logged out\n', 'msginfo'])

def periodic():
    window.after(500, periodic)
    change()
    show()

window.protocol("WM_DELETE_WINDOW", lambda:type(s.send_json({'logout':nick}))==type(window.destroy()))

text_output.grid(row=0,column=0,columnspan=3)
flaglabel.grid(row=1, column=0)
text_entry.grid(row=1, column=1)
button.grid(row=1, column=2)
scroll=tk.Scrollbar(window, command=text_output.yview)
text_output.config(yscrollcommand=scroll.set)
scroll.grid(row=0,column=3, sticky=tk.S+tk.N)
tk.Grid.grid_columnconfigure(window, 0, minsize=200)
window.after(500, periodic)

nick=get_nickname()
s.send_json({'login':nick})

window.mainloop()
