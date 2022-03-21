# Version 1
from sys import exit, exc_info, argv
import timeit
import signal
from simple_pid import PID
from references import *
import utils
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
    KpR= float(argv[8]) if len(argv) > 8 else 0.1
    KiR= float(argv[9]) if len(argv) > 9 else 0.1
    KdR= float(argv[10]) if len(argv) > 10 else 0.001
    KpM= float(argv[11]) if len(argv) > 11 else 5.79
    KiM= float(argv[12]) if len(argv) > 12 else 0
    KdM= float(argv[13]) if len(argv) > 13 else .22
except:
	print(exc_info())
	print("Usage: nlcontroller_current [client(udp,tcp,dccp,...)] [network(eth, wifi)] [host] [port] [suffix] duration STEPSIZE KPball KIball KDball KPbeam KIbeam KDbeam")
	exit(1)
 
from requestsclient import *
initialize_handshake(host, port, True)

clock = timeit.default_timer

#Performance parameters
iteration = 0 #Keep track of loop iterations
mse_x = 0 #Mean squared error in x
mse_y = 0 #Mean squared error in y
mse_z = 0 #Mean squared error in z
tcrash = float('inf') #Time the program crashed. If it didn't crash, this is infinite
crashed = False #If the program crashed


#strip off trailing slash and http, if present.
host = host.split('http://')[-1].strip('/')

# / get these from mds (xkernel, xamplitude, xfrequency)
xkernel = None
xamplitude = None
xfrequency = None

u_max=20;
CumulativeError = 0

pid = PID(KpR, KiR, KdR, setpoint=0)
pid.output_limits = (-5, 5)  
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
        print("%.4f\t%.4f\t%.5f\t%.4f\t%.4f\t%.5g\t%.5f" % (theta,thetadot,t,control,error,tr-t,StateTime))
    except:
        print("Failed to control at %s seconds || Because %s"%(t,exc_info()) )

if __name__ == "__main__":
    url = "/init?value0=0&time=0"
    process(host,port,url,clientport)
    taskmetadata = utils.gettaskmds()
    xkernel = taskmetadata["xkernel"]
    xamplitude = taskmetadata["xamplitude"]
    xfrequency = 1/taskmetadata["xperiod"]
    utils.initjobmds(xkernel, xamplitude, xfrequency)

    #(timer, interrupt)=(signal.ITIMER_PROF, signal.SIGPROF)
    (timer, interrupt)=(signal.ITIMER_REAL, signal.SIGALRM)
    signal.signal(interrupt, controlloop)
    signal.setitimer(timer, h, h)

    t0 = clock()
    t=0

    #Stop program after duration
    while t < dur and crashed == False:
        pass

    # Stop timer and plant
    #signal.setitimer(signal.ITIMER_REAL, 0, h)
    signal.setitimer(signal.ITIMER_PROF, 0, h)
    url = "/init?value0=0&time=0"
    utils.finishjobmds()
    process(host,port,url,clientport)