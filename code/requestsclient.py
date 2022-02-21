#version 1:
import traceback
import requests
from re import search
from sys import exc_info

session = None

def initialize_handshake(HOST, PORT):    # setup socket and start the connection to the model
    global session
    session = requests.Session()

# Method to read URL
def process(HOST, PORT, GET, client = None):
        try:
            data = session.get("http://"+HOST+":"+str(PORT)+GET, timeout=.150)
            response = data.text;
            m = search('\[(.+?)\]', response)
            if m:
                response = m.groups()[-1]
        except:
                print("Did not get response: ", exc_info())
                response = (GET.split("time=")[1]).split("&")[0]
        return response

if __name__ == "__main__":
    host = 'castara' 
    data = '/state?time=now'
    port = 9163
    print(process(host, port, data))