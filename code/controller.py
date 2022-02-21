# Version 1
from sys import exit, exc_info, argv
import timeit
import signal
from simple_pid import PID
from references import *
from math import pi

#Take arguments to determine file name, port, etc.
try:
    client = argv[1]
    network = argv[2]
    host = argv[3]
    port = argv[4]
    suffix = argv[5]
    clientport = 0;
    dur= float(argv[6]) if len(argv) > 6 else 3 * 3600
    h= float(argv[7]) if len(argv) > 7 else .02
    KpR= float(argv[8]) if len(argv) > 8 else -.312-1
    KiR= float(argv[9]) if len(argv) > 9 else 0
    KdR= float(argv[10]) if len(argv) > 10 else 1.299
    KpM= float(argv[11]) if len(argv) > 11 else 5.79
    KiM= float(argv[12]) if len(argv) > 12 else 0
    KdM= float(argv[13]) if len(argv) > 13 else .22
except:
	print(exc_info())
	print("Usage: nlcontroller_current [client(udp,tcp,dccp,...)] [network(eth, wifi)] [host] [port] [suffix] duration STEPSIZE KPball KIball KDball KPbeam KIbeam KDbeam")
	exit(1)
 
from requestsclient import *
initialize_handshake(host, port)
#Log data to the correct file
clock = timeit.default_timer
t0 = clock()
t=0

#Performance parameters
iteration = 0 #Keep track of loop iterations
mse_x = 0 #Mean squared error in x
mse_y = 0 #Mean squared error in y
mse_z = 0 #Mean squared error in z
tcrash = float('inf') #Time the program crashed. If it didn't crash, this is infinite
crashed = False #If the program crashed


#strip off trailing slash and http, if present.
host = host.split('http://')[-1].strip('/')

ykernel = 'butterfly2'
yamplitude = 2.0
yfrequency = 1.0/100.00
psikernel = 'butterfly1'
psiamplitude = 0*pi/180
psifrequency = 1.0/125.0
xkernel = 'butterfly1'
xamplitude = 2.0
xfrequency = 1.0/100.00

u_max=20;
CumulativeError = 0

pid = PID(1, 0.05, 0.001, setpoint=90)
control = 0

def controlloop(signum, _):
    global t, StateTime, control
    global tcrash, crashed, iteration, mse_x, mse_y
    
    # Update the time and iteration number
    iteration += 1

    t = clock()-t0
    url = "/u?value0=%.4f&time=%.6f&access=8783392" % (control, t)
    try:
        response=process(host,port,url,clientport)
        # Compute new output from the PID according to the systems current value
        response_split=response.split()
        theta = float(response_split[0])
        thetadot = float(response_split[1])
        StateTime = float(response_split[2])

        thetadot_d = ref(t, xkernel, xamplitude, xfrequency)
        error = thetadot_d - thetadot
        pid.setpoint = thetadot_d
        control = pid(thetadot)
        tr = clock() - t0
        #Write the logs
        print("%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.5g\t%.5g" % (theta,thetadot,t,control,error,tr,StateTime))
    except:
        print("Failed to control at %s seconds || Because %s"%(t,exc_info()) )

if __name__ == "__main__":
    url = "/init?value0=0&time=0"
    process(host,port,url,clientport)

    #(timer, interrupt)=(signal.ITIMER_PROF, signal.SIGPROF)
    (timer, interrupt)=(signal.ITIMER_REAL, signal.SIGALRM)
    signal.signal(interrupt, controlloop)
    signal.setitimer(timer, h, h)
  
    #Stop program after duration
    while t < dur and crashed == False:
        pass
  
    # Stop timer and plant
    #signal.setitimer(signal.ITIMER_REAL, 0, h)
    signal.setitimer(signal.ITIMER_PROF, 0, h)
    url = "/init?value0=0&time=0"
    process(host,port,url,clientport)