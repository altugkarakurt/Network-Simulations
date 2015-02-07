import numpy as np
import random
import math 

##----------------------------------------------------------------------------------------
##              ANALYSIS of SHORTEST PATH BASED NETWORKING
##----------------------------------------------------------------------------------------
## Altug Karakurt, December 2014                    
##----------------------------------------------------------------------------------------
 
## Network Initialization ----------------------------------------------------------------
traffic = np.tril([[((math.ceil(random.random() * 1000) / 1000) * 4) for x in range(14)] for y in range(14)], k = -1)
linklist = np.zeros(21)		#holds link loads of the current trial
nodelist = ['ny', 'pa', 'ca1', 'ca2', 'wa', 'ut', 'co', 'tx', 'ne', 'il', 'mi', 'ga', 'dc', 'nj']
max_load = np.zeros(100)	#holds the list of heaviest loads for all trials
link_occur = np.zeros(21)	#holds the number of times the links have become the heaviest

## Routing Tables ----------------------------------------------------------------------
ny_m2 = [['ca1', 1], ['ca2', 2], ['wa', 2], ['ut', 2], ['co', 2], ['ne', 2], ['tx', 2], ['il', 2], ['mi', 1, 'd'], ['pa', 2, 'd'], ['ga', 2], ['dc', 3, 'd'], ['nj', 3]]
pa_m2 = [['ca1', 10], ['ca2', 10], ['wa', 10], ['ut', 10], ['co', 10], ['ne', 10], ['tx', 8], ['il', 10, 'd'], ['mi', 2], ['ny', 2, 'd'], ['ga', 8, 'd'], ['dc', 4], ['nj', 4, 'd']]
ca1_m2 = [['ny', 16], ['ca2', 19, 'd'], ['wa', 18, 'd'], ['ut', 16, 'd'], ['co', 16], ['ne', 16], ['tx', 19], ['il', 16], ['mi', 16], ['pa', 16], ['ga', 19], ['dc', 16], ['nj', 16]]
ca2_m2 = [['ca1', 19, 'd'], ['ny', 19], ['wa', 17, 'd'], ['ut', 19], ['co', 19], ['ne', 19], ['tx', 20,'d'], ['il', 19], ['mi', 19], ['pa', 19], ['ga', 20], ['dc', 20], ['nj', 20]]
wa_m2 = [['ca1', 18, 'd'], ['ca2', 17, 'd'], ['ny', 12], ['ut', 18], ['co', 18], ['ne', 12], ['tx', 17], ['il', 12, 'd'], ['mi', 18], ['pa', 12], ['ga', 12], ['dc', 12], ['nj', 12]]
ut_m2 = [['ca1', 16, 'd'], ['ca2', 16], ['wa', 16], ['ny', 13], ['co', 13, 'd'], ['ne', 13], ['tx', 13], ['il', 13], ['mi', 15, 'd'], ['pa', 13], ['ga', 13], ['dc', 13], ['nj', 15]]
co_m2 = [['ca1', 15], ['ca2', 15], ['wa', 15], ['ut', 15, 'd'], ['ny', 14], ['ne', 14, 'd'], ['tx', 21, 'd'], ['il', 14], ['mi', 15], ['pa', 14], ['ga', 21], ['dc', 14], ['nj', 14]]
tx_m2 = [['ca1', 20], ['ca2', 20, 'd'], ['wa', 20], ['ut', 21], ['co', 21, 'd'], ['ne', 21], ['ny', 9], ['il', 9], ['mi', 9], ['pa', 9], ['ga', 9, 'd'], ['dc', 7, 'd'], ['nj', 7]]
ne_m2 = [['ca1', 14], ['ca2', 14], ['wa', 11], ['ut', 14], ['co', 14, 'd'], ['ny', 11], ['tx', 14], ['il', 11, 'd'], ['mi', 11], ['pa', 11], ['ga', 11], ['dc', 11], ['nj', 11]]
il_m2 = [['ca1', 11], ['ca2', 11], ['wa', 12, 'd'], ['ut', 11], ['co', 11], ['ne', 11, 'd'], ['tx', 10], ['ny', 10], ['mi', 10], ['pa', 10, 'd'], ['ga', 10], ['dc', 10], ['nj', 10]]
mi_m2 = [['ca1', 13], ['ca2', 13], ['wa', 1], ['ut', 13, 'd'], ['co', 13], ['ne', 1], ['tx', 1], ['il', 1], ['ny', 1, 'd'], ['pa', 1], ['ga', 1], ['dc', 1], ['nj', 5, 'd']]
ga_m2 = [['ca1', 9], ['ca2', 9], ['wa', 8], ['ut', 9], ['co', 9], ['ne', 8], ['tx', 9, 'd'], ['il', 8], ['mi', 8], ['pa', 8, 'd'], ['ny', 8], ['dc', 8], ['nj', 8]]
dc_m2 = [['ca1', 3], ['ca2', 8], ['wa', 3], ['ut', 3], ['co', 3], ['ne', 3], ['tx', 8, 'd'], ['il', 3], ['mi', 3], ['pa', 3], ['ga', 3], ['ny', 3, 'd'], ['nj', 6, 'd']]
nj_m2 = [['ca1', 5], ['ca2', 6], ['wa', 4], ['ut', 5], ['co', 4], ['ne', 4], ['tx', 6], ['il', 4], ['mi', 5, 'd'], ['pa', 4, 'd'], ['ga', 4], ['dc', 6, 'd'], ['ny', 4]]
M2 = [ny_m2, pa_m2, ca1_m2, ca2_m2, wa_m2, ut_m2, co_m2, tx_m2, ne_m2, il_m2, mi_m2, ga_m2, dc_m2, nj_m2]

## Routing Functions -------------------------------------------------------------------
def packetWrapper(demand, srcIdx, destIdx):	
    return [demand, srcIdx, destIdx]	#wraps demand with destination and source info

def network_init():						#re-initializes the parameters for next trial
    global traffic
    global linklist
    traffic = np.tril([[((math.ceil(random.random() * 1000) / 1000) * 4) for x in range(14)] for y in range(14)], k = -1)
    linklist = np.zeros(21)

def trafficIterator():					#iterates through all demands and sends them  
    for i in range(14): 				      
        for j in range(14):     
            if(i > j):
                pathfinder(packetWrapper(traffic[i][j], i, j))

def pathfinder(p):				#a basic and recursive single-routed routing function
    print ('from %s to %s' % (nodelist[p[1]], nodelist[p[2]]))
    src = p[1]
    dest = p[2]
    for k in range(13):        
            if (nodelist[dest] == M1[src][k][0]):	#the next link to be used is found
                print 'Found a path!'
                match = M1[src][k]
                match_link = M1[src][k][1]
                match_str = M1[src][k][0]
                print match_link
                linklist[match_link - 1] += p[0]	#the demand is added to the link
                if (len(match) != 3):		#checks if the next hop is the destination 
											#if not, recalls itself with next hop as 
											#the destination
                    for l in range(13):
                        if ((match_link == M1[src][l][1]) and (len(M1[src][l]) == 3)):
                            next = M1[src][l]#the node at the end of next link is found
                            next_str = M1[src][l][0]
                            break
                    for m in range(14):	#array index of next hop is found
                        if(next_str == nodelist[m]):
                            next_node = m
                            break
                    pathfinder(packetWrapper(p[0], next_node, dest)) #recursive call
                else:
                    break

for cnt in range(100):	#the simulation is held 100 times
    network_init()		#network is re-initialized for the next trial 
    trafficIterator()	#handles the demand iteration between each node pair
    with open('results.txt', 'a') as file: # results are recorded in text file
        file.write('The max loaded link is %d with load %3.3f\n' % (np.argmax(linklist) + 1, linklist[np.argmax(linklist)] * 100 / 40))
    max_load[cnt] = linklist[np.argmax(linklist)] * 100 / 40 #heaviest load is recorded
    link_occur[np.argmax(linklist)] += 1 #holds occurrences of each link as the heaviest
with open('results.txt', 'a') as file: # results are recorded in text file
    file.write ('\n#################\nThe average load of the heaviest loaded link is:  %3.3f\nThe most frequently loaded link is %d with %d' % (sum(max_load) / len(max_load), np.argmax(link_occur), link_occur[np.argmax(link_occur)]))
print max_load
print ('The average load of the heaviest loaded link is:  %3.3f\n' % (sum(max_load) / len(max_load)))