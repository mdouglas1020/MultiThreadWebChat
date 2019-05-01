#!/user/bin/env python3
# Michael Douglas
# Networks Lab 3 Chat App
# mjd8v2
# Student ID 14241220
# 05/1/19

import sys
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tk
# Setting up tkinter environment variables
top = tk.Tk() 
top.title("My Chat Room Client V2")
msg_frame = tk.Frame(top)
scrollBar = tk.Scrollbar(msg_frame)
msg_list = tk.Listbox(msg_frame, height=40, width=100, yscrollcommand=scrollBar.set)
msg_list.config(width= 100)
master = tk.Tk()
my_msg = tk.StringVar()# For the messages to be sent.
my_msg.set("Type your messages here.")
BUFSIZE = 1024

# Handles recieving input
def receive():

    while True:
        try:
            msg = client_socket.recv(BUFSIZE).decode("utf8")
            print(msg)
            msg_list.insert(tk.END, msg)
        except OSError:
            break

# Handles sending from client
def send(event=None): 
 
    msg = my_msg.get()
    my_msg.set("")
    print("Send test\n")
    if "\n" in msg:
        print("newline test\n")
        msg = msg.split("\n")
        msg = msg.strip("'")
        for splits in msg:
            print("YEAH test\n")
            client_socket.send(bytes(msg[splits], "utf8")) 
    else:
        client_socket.send(bytes(msg, "utf8"))
        if msg == "{logout}":
            client_socket.close()
            top.quit()

# What gets sent on close
def on_close(event=None):
    my_msg.set("{logout}")
    send()

# message sent when newuser button clicked
def newuser(event=None):
    my_msg.set("{newuser}")
    send()




my_msg = tk.StringVar()
my_msg.set(" ")

#GUI Positioing and setup

scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
msg_list.pack()
msg_frame.pack()

msg_field = tk.Entry(top, textvariable=my_msg)
msg_field.bind("<Return>", send)
msg_field.pack()
sendBtn = tk.Button(top, text = "Send", command=send) # Buttons created and packed
newUserBtn = tk.Button(top, text = "New User", command=newuser)
sendBtn.pack()
newUserBtn.pack()


top.protocol("WM_DELETE_WINDOW", on_close)
HOST = "127.0.0.1" # localhost
PORT = 11220 # port set to 1 + last four digits of ID

ADDR = (HOST, PORT)
client_socket = socket(AF_INET, SOCK_STREAM) 
client_socket.connect(ADDR) # Connect client

receive_thread = Thread(target=receive) # begin thread with recieve as target
receive_thread.start()
tk.mainloop()