from SimPy.Simulation import *
from random import expovariate, seed
import numpy as np

##----------------------------------------------------------------------------------------
##      ORDINARY ETHERNET SIMULATION	
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
        arriveTime = now()                            # timestamp for frame arrival
        print("%8.12f %s: I arrived" % (now(), self.name))
        yield request, self, b                        # frame asks for service
        waitTime = now() - arriveTime
        wM.observe(waitTime)                          # Monitor object calculates E[W]
        wait_array.append(waitTime)                   # waiting duration of frames
        print("%8.12f %s: Waited %6.12f" % (now(), self.name, waitTime))          
        yield hold, self, processTime                 # frame gets service                          
        yield release, self, b                        # service is done, frame leaves
        print("%8.12f %s: Done      " % (now(), self.name))

## Experiment data -------------------------
number_of_frames = 5000000                            # frame arrival count of the link
maxTime = 1000000000000.0                             # simulation period (µs)
processTime = 0.640                                   # mean frame service period(µs)
lambd03 = 2.133                                       # arrival rate for 0.3 load(µs)     
lambd06 = 1.067                                       # arrival rate for 0.6 load(µs)
lambd09 = 0.711                                       # arrival rate for 0.9 load(µs)             

## Model/Experiment ------------------------------
wait_array = []
k = Resource(name="EthernetLink", unitName="LinkQueue") # initiation of link's model
wM = Monitor()                                                       
initialize()
s = Source('Source')
activate(s, s.generate(number=number_of_frames, lambd=lambd03,
                        resource=k), at=0.0)
simulate(until=maxTime)

## Result  ----------------------------------
result = wM.count(), wM.mean()                        # E[W] is obtained
w99_array = np.array(wait_array)
w99_array = np.sort(w99_array)          
w99 = w99_array[int(number_of_frames * 99/100)]       # W(99) value
print("Average wait for %7d completions was %5.3f microseconds." % result)
print("The 99 percentile waiting time was %5.3f microseconds." % w99)
