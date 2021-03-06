from SimPy.Simulation import *
from random import randint
import numpy as np
##----------------------------------------------------------------------------------------
##      802.11b CONTENTION WINDOW MAC ANALYSIS  
##----------------------------------------------------------------------------------------
## Altug Karakurt, November 2014                     
##----------------------------------------------------------------------------------------

## Model components ------------------------
class Source(Process):
    """ Source simulates the N hosts with infinite queues, by
		simultaneously refilling an N long queue, representing
		the first packets waiting in queue of each host		"""                                             
    def generate(self, resource):
        global packets_so_far						  # counts number of arriving packets
        global isIdle    							  # checks whether link is available
        min_backoff = 0								  # the minimum back-off to decrement
        while(served_packets < number_of_packets):	  # models new arrivals to N hosts
            for i in range(N):						  
                if (packet_q[i] is None):        	  # refills the processed N packet
                    packet_q[i] = Packet(name="Packet%07d" % (packets_so_far))
                    trial_q[i] = 0					  # resets for the new packets 
                    backoff_q[i] = randint(0, cw[trial_q[i]])  # random back-off choice
                    packets_so_far += 1               
            np_q = np.array(backoff_q)
            min_idxs = [idx for idx, val in enumerate(backoff_q) if val == np_q.min()]
            min_backoff = backoff_q[min_idxs[0]]   	  #retrieves hosts with min back-off
            for k in range(N):
                backoff_q[k] -= min_backoff			  # decrements counters
            if ((len(min_idxs) == 1) and (isIdle)):   # case of no collisions
                isIdle = False						  # reserves the link for service
                next_packet = packet_q[min_idxs[0]]	  # sends the packet to get service
                activate(next_packet, next_packet.service(b = resource))
                packet_q[min_idxs[0]] = None		  # empties the corresponding entry
                trial_q[min_idxs[0]] = cwmin		  # resets to initial values
                backoff_q[min_idxs[0]] = 0			  # resets to initial values
            elif(len(min_idxs) > 1):        		  # case of len(min_idxs) collisions
                isIdle = False						  # blocks the link to prevent 
													  # services, because of collision
                yield hold, self, processTime		  # gives the required delay,
                yield hold, self, sifs				  # that is caused by collisions
                yield hold, self, ack
                for col in min_idxs:				# colliding packets pick new back-off
                    if(cw[trial_q[col]] < cwmax ):	  # limits cw to CWmax
                        trial_q[col] += 1
                    backoff_q[col] = randint(0, cw[trial_q[col]])
                isIdle = True					      # releases the link for service
            yield hold, self, difs  				  # delays the link for DIFS     
			 		 
class Packet(Process):
    """ Models the process of packets getting serviced """ 
    def service(self, b):                                                            
        global served_packets						  
        global isIdle								  
        yield request, self, b  				# packet asks for service                                                  
        yield hold, self, processTime 			# packet gets serviced                                     
        served_packets += 1
        yield hold, self, sifs					# packet waits for ACK
        yield hold, self, ack                   # ACK arrives
        yield release, self, b                  # service completed, releases link                
        print("%7d %s: Done" % (served_packets, self.name))
        isIdle = True						    # link is available
        if (served_packets == number_of_packets): # checks whether simulation is over 
            totalTime = now()
            throughput = 1500.0 * 8 * number_of_packets / totalTime
            with open('results.txt', 'a') as file: # results are recorded in text file
                file.write('N = %4d \nCWmin = %d \nThroughput is %8.4f MBits \nThroughput ratio is %8.4f percent \n############### \n' % (N, cw[cwmin], throughput, throughput * 100 / (5.5)))
            print('Throughput is %8.4f MBits' % (throughput))
            print('Throughput ratio is %8.4f percent' % (throughput * 100 / (5.5)))
            stopSimulation()				    # simulation is terminated

## Experiment data -------------------------
number_of_packets = 100000      				# number of packets to be serviced        
packets_so_far = 0       						# number of generated packets
maxTime = 1000000000000.0                       # simulation period (µs)
packet_q = []                  				    # queue representing the N hosts
backoff_q = []              				    # picked back-off values
trial_q = []                   					# number of trials of each packet
cw = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]	# possible CW limits
processTime = 2180   							# mean packet service period (µs)
isIdle = True									# flag for tracing link availability
served_packets = 0								# number of completed services
cwmax = 1024									# upper boundary for CW
difs = 20										# constant DIFS (µs)
sifs = 10										# constant SIFS (µs)
ack = 145           							# arbitrary ACK service time
												# calculated for 100 bytes length               
N = 5											# number of hosts
cwmin = 3										# initial CWmin = 2^(cwmin - 1)

## Model/Experiment ------------------------------
for j in range(N):								# initializes the required arrays
    packet_q.append(None)
    backoff_q.append(0)
    trial_q.append(cwmin)        
k = Resource(name="WLAN", unitName="NQueueSimulation")
initialize()
s = Source('Source')
activate(s, s.generate(resource=k), at=0.0)
simulate(until=maxTime)
