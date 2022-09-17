#version 1:
import traceback
import requests
from re import search
from sys import exc_info

session = None
token = ""

def initialize_handshake(HOST, PORT, login=False):    # setup socket and start the connection to the model
    global session
    session = requests.Session()
    if login:
        gettoken(HOST, PORT)

def gettoken(HOST, PORT):
    global token
    data = requests.get("http://"+HOST+":"+str(PORT)+"/login", timeout=2)
    token = "/%s"%data.url.split("/")[3]
    if data.status_code != 200 and data.status_code != 202:
        data = requests.get("http://"+HOST+":"+str(PORT)+"/0", timeout=2)
        token = "/0"
        if data.status_code != 200 and data.status_code != 202:
            raise ValueError("Could not login to a plant")

# Method to read URL
def process(HOST, PORT, GET, client = None):
        try:
            data = requests.get("http://"+HOST+":"+str(PORT)+"%s"%token+GET, timeout=4.50)
            response = data.text
            m = search('\[(.+?)\]', response)
            if m:
                response = m.groups()[-1]
        except:
                raise ValueError("Did not get response: ", exc_info(), (GET.split("time=")[1]).split("&")[0])
        return response

if __name__ == "__main__":
    host = 'castara' 
    data = '/state?time=now'
    port = 9163
    print(process(host, port, data))
