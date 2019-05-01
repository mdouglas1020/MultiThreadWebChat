#!/user/bin/env python3
# Michael Douglas
# Networks Lab 3 Chat App
# mjd8v2
# Student ID 14241220
# 05/1/19
import sys
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread


MAXCLIENTS = 3 # Max Clients
clients = {} # Client list
addresses = {} # Addresses list
HOST = "127.0.0.1" 
PORT = 11220 
BUFSIZE = 1024
ADDR = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

# Send all function technically 
def broadcast(msg, prefix=""): 
    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)

# Function to send to specific ONLINE user
def personalMessage(user, msg, prefix=""):
    for sock in clients:
        if user == clients[sock]:
            sock.send(bytes(prefix, "utf8")+ msg)

# Initial connection function
def accept_incoming_conn():
    while True:
        client, client_addr = SERVER.accept()
        print("%s:%s has connected" % client_addr)
        client.send(bytes("Welcome to the web chat! Please enter login to login, or click create account to create an account", "utf8"))
        addresses[client] = client_addr
        Thread(target=handle_client, args=(client,)).start()

# Function to recieve input from client
def handle_client(client):
    test = client.recv(BUFSIZE).decode("utf8") # Initial send from client 
    if test == '{newuser}': # If the new user button is clicked this is sent from the client, prompt new user signup
        client.send(bytes("Please enter new username: ", "utf8"))
        newUser = client.recv(BUFSIZE).decode("utf8")
        while len(newUser) > 32: # Error check username size
            client.send(bytes("Username is too long!! Please enter new username less than 32 characters: ", "utf8"))
            newUser = client.recv(BUFSIZE).decode("utf8")
            
        while newUser in open('users.txt').read(): # Check username isnt already in use
            client.send(bytes("User name already in use!!!  Please enter new username: ", "utf8"))
            newUser = client.recv(BUFSIZE).decode("utf8")
        client.send(bytes("Please enter new Password: ", "utf8"))
        newPwd = client.recv(BUFSIZE).decode("utf8")
        while len(newPwd) < 4 or len(newPwd) > 8: # Error check on password 
            client.send(bytes("Invalid Password format! Please enter new Password between 4 and 8 characters: ", "utf8"))
            newPwd = client.recv(BUFSIZE).decode("utf8")

        saveUserInfo = newUser + "," + newPwd # format user login data to fit format
        f = open("users.txt", "a+")
        f.write("\n%s" %saveUserInfo)
        f.close()
        client.send(bytes("New accout succefully made!\n\n","utf8"))

    logged_in = False
    while logged_in != True: # Begin login phase
        client.send(bytes("Enter Username Here and Password here : ", "utf8"))
        login_info = client.recv(BUFSIZE).decode("utf8")
        while login_info == "" or " " not in login_info or len(login_info) < 9: # if nothing sent
            client.send(bytes("Invalid Input! Enter Username Here and Password here : ", "utf8"))
            login_info = client.recv(BUFSIZE).decode("utf8")
            
        try: # try to split login info line
            login_info = login_info.split() 
        except ValueError:
            client.send(bytes("BadInput: Enter Username Here and Password here : ", "utf8"))
            login_info = client.recv(BUFSIZE).decode("utf8")
       
        with open("users.txt", "r") as fp:
            for line in fp.readlines():
                comp = line.split(",")
                pwd = comp[1].replace("\n", "")
                if login_info[0] == comp[0]: # check the login info given by user against names in file, if a match continue
                    if login_info[1] == pwd: # if the entered password matches, continue
                        logged_in = True
                        greet = 'Welcome %s! to logout type {logout} All commands should begin and end with curly braces' % login_info[0]
                        client.send(bytes(greet, "utf8"))
                        msg = "%s has joined the chat " % login_info[0]
                        broadcast(bytes(msg, "utf8"))
                        clients[client] = login_info[0] # add username to online clients list
                        while True:
                            try:
                                msg = client.recv(BUFSIZE)
                            except OSError:
                                client.close()
                                fp.close()
                                broadcast(bytes("%s has left the chat." % login_info[0], "utf8")) # if user logsout 
                                logged_in = False
                                break
                            if bytes("{pm}", "utf8") in msg: # If personal message function called
                   
                                pmInfo = str(msg).split() # Split message, and strip all unneeded bits for sending the message
                                usertest = pmInfo[1]
                                usertest = usertest.strip()
                                usertest = usertest.strip("'")
                                for x in clients: # look through all active users, if a match send personal message
                                    if str(usertest) in clients[x]:
                                        msg = str(msg).replace("{pm}", "")
                                        msg = msg.strip()
                                        msg = msg.strip("'")
                                        msg = msg.strip("b'")
                                        msg = msg.replace("%s"%usertest, "")
                                        msg = bytes(msg, "utf8")
                                        personalMessage(usertest,msg, "Personal Message from %s: " %usertest)
                                        msg = str(msg).replace("", "{pm}")
                                        msg = bytes(msg, "utf8")
                                        
                                    
                            if msg == bytes("{who}", "utf8"): # If who function is called, scan through online clients and print names
                                client.send(bytes("Currently Online: ", "utf8"))
                                for x in clients:
                                    client.send(bytes(clients[x] + " ", "utf8"))
                            if msg != bytes("{logout}", "utf8"): # THESE ifs are too ensure messages starting with these functions arent sent to everyone
                                if msg!= bytes("{who}", "utf8"):
                                    print("Test before pm test")
                                    if bytes("{pm}", "utf8") not in msg:
                                        print("Test before send")
                                        broadcast(msg, login_info[0]+": ")
                            else: # if logout is entered, SAME AS LOGOUT
                                fp.close()
                                client.send(bytes("{logout}", "utf8"))
                                client.close()
                                del clients[client]
                             
                                broadcast(bytes("%s has left the chat." % login_info[0], "utf8"))
                                logged_in = False
                                quit()
                            
            print("Incorrect login info: Please login before attempting to send messages! ")
 
      
       

                        
        

  


    


if __name__ == "__main__":
    SERVER.listen(MAXCLIENTS)
    
    ACCEPT_THREAD = Thread(target=accept_incoming_conn)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
   