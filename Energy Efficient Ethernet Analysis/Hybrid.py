from SimPy.Simulation import *
from random import expovariate, seed
import numpy as np

##----------------------------------------------------------------------------------------
##      HYBRID ENERGY EFFICIENT ETHERNET SIMULATION	
##----------------------------------------------------------------------------------------
## Altug Karakurt, November 2014					 
##----------------------------------------------------------------------------------------

## Model components ------------------------
class Source(Process):                                # frame generating source
    """ Source generates ethernet frames by a 
         Poisson Process to feed into the ethernet link """
    def generate(self, number, lambd, resource):
        for i in range(number):
            f = Frame(name="Frame%07d" % (i))         # frame is created
            activate(f, f.arrive(b=resource))         # destination is set to link
            t = expovariate(1.0 / lambd)              # arrival is set as poisson process
            yield hold, self, t                       # delayed for interarrival time 


class Frame(Process):
    """ The frame's activities and the link's state
          transitions are handled """
    def arrive(self, b):                              # frame arrives to link
        global queue_length                           # number of waiting frames
        global isActive                               # if link is active or in LPI
        global lpi_start                              # timestamp of LPI transition 
        global lpi_durations                          # LPI mode durations of the link
        def inLine():                                 # checks if the waiting frames,
			return isActive							  #	can be serviced
            return isActive
        def firstInLine():                            # checks if 1st frame in line 
													  # can be serviced or not
            return ((queue_length >= Nmax) or (now() - arriveTime >= T-Tw))
        arriveTime = now()                            # timestamp for frame arrival
        print("%8.12f %s: I arrived" % (now(), self.name)) 
        queue_length += 1                             # incremented due to the arrival
        if (not(isActive) and (queue_length == 1)):   # behavior of 1st arriving frame 
													  # in LPI state
            yield waituntil, self, firstInLine
            lpi_durations.append(now() - lpi_start)   # records the LPI mode duration
            yield hold, self, Tw                      # when LPI mode ends, 1st frame
													  # in line keeps the link busy for
                                                      # extra Tw, simulating wake-up
            isActive = True                           # link enters active mode
        elif((queue_length > 1) and (not(isActive))):
            yield waituntil, self, inLine             # other frames than the 1st, 
													  # wait in the queue
        yield request, self, b                        # frame asks for service
        waitTime = now() - arriveTime                                  
        wM.observe(waitTime)                          # Monitor object calculates E[W]
        wait_array.append(waitTime)                   # waiting duration of frames
        print("%8.12f %s: Waited %6.12f" % (now(), self.name, waitTime))          
        yield hold, self, processTime                 # frame gets service           
        queue_length -= 1                                                       
        if (queue_length == 0):						  # if queue is empty,
            isActive = False                          # link goes to LPI
            yield hold, self, Ts                      # the last frame to leave the queue 
                                                      # keeps the link busy for extra Ts,
													  # simulating the sleep process
            lpi_start = now()                         # timestamp for LPI transition
        yield release, self, b                        # service is done, frame leaves
        print("%8.12f %s: Done      " % (now(), self.name))

## Experiment data -------------------------
number_of_frames = 5000000                            # frame arrival count of the link
maxTime = 1000000000000.0                             # simulation period (µs)
processTime = 0.640                                   # mean frame service period(µs)
lambd03 = 2.133                                       # arrival rate for 0.3 load(µs)     
lambd06 = 1.067                                       # arrival rate for 0.6 load(µs)
lambd09 = 0.711                                       # arrival rate for 0.9 load(µs)              
Ts = 2.5 * N                                          # sleep state duration
Tw = 5 * N                                            # wake-up state duration
Nmax = 10                                             # frame count     
N = 4											      # given N
T = 1000        									  # timer count                        
## Model/Experiment ------------------------------
queue_length = 0
isActive = False
lpi_start = 0
wait_array = []
lpi_durations = []
k = Resource(name="EthernetLink", unitName="LinkQueue") # initiation of link's model
wM = Monitor()
initialize()
s = Source('Source')
activate(s, s.generate(number=number_of_frames, lambd=lambd03,
                        resource=k), at=0.0)
simulate(until=maxTime)

## Result  ----------------------------------
result = wM.count(), wM.mean()                        # E[W] is obtained
lpi_total = sum(lpi_durations)                        # Total duration of LPI state
active_total = now() - lpi_total                      # Total duration of Active state
w99_array = np.array(wait_array)                                      
w99_array = np.sort(w99_array)          
w99 = w99_array[int(number_of_frames * 99/100)]       # W(99) value
print("Average wait for %7d completions was %5.3f microseconds." % result)
print("The 99 percentile waiting time was %5.3f microseconds." % w99)
print("LPI duration was %5.3f microseconds, while Active duration was %5.3f" %(lpi_total, active_total))
print("p = 0.3, N = 4, Nmax = 10, T = 100")
