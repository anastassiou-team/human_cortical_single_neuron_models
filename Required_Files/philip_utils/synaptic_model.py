# Contains functions related to synapses

import numpy as np

#Return probability distribution of n_synapses, assuming an exponential distribution.
#See Figure 7F in "A petavoxel fragment of human cerebral cortex reconstructed at nanoscale resolution"
def nsyns_exp_distribution(x, a = 9, b = 10):
    
    pdf = a*np.power(b*np.ones(len(x)),-x)
    pdf[-1] = 1 - np.sum(pdf[:-1])
    
    return pdf

#Return probability distribution of n_synapses, assuming a power law.
#See Figure 7F in "A petavoxel fragment of human cerebral cortex reconstructed at nanoscale resolution"
def nsyns_power_distribution(x, a = 0.9, exponent = 6):
    
    pdf = np.divide(a,x**exponent)
    pdf[-1] = 1 - np.sum(pdf[:-1])

    return pdf

#Return a number between nsyns_min and nsyns_max sampled from nsyns_exp_distribution or nsyns_power_distribution
def nsyns_sample(nsyns_min,nsyns_max, distribution = 'power'):
    
    #Interval of possible number of synapses
    interval = np.arange(nsyns_min,nsyns_max + 1)

    #Get probability distribution
    if distribution == 'power':
        pdf = nsyns_power_distribution(interval)
    elif distribution == 'exp':
        pdf = nsyns_exp_distribution(interval)
    else:
        pdf = (1/len(interval))*np.ones(len(interval)) #otherwise assume a uniform distribution
        
    #Sample from chosen probability distribution
    n = np.random.choice(interval, p=pdf)
    
    return n
