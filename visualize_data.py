# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 14:18:34 2018

@author: Anna

This module plots our data and saves this plot in a PNG image.

"""

import numpy as np
import matplotlib.pyplot as plt
import os

delta_data = [] #x-axis in plot
time_data = [] #y-axis in plot
overall_time = []
overall_delta = []

def export_fig(name, fig):
    my_path = os.path.join("", name)
    fig.savefig(my_path)

with open('testtimelog.txt') as fp:
    for line in fp:
        old_d_6 = None
        get_d6 = line.split(',')
        delta_6 = get_d6[0] #we get delta_6 by seperating at the first comma and taking the first element
        if delta_6 != old_d_6:
            #make new plot
            fig = plt.figure(int(delta_6))
        
        #then get delta_7 and plot it vs its time in the plot
        data = get_d6[1].split('-')
        delta_7 = int(data[0])
        delta_data.append(delta_7) #add new delta_7-point ---- possibly value error of it thinks delta is a float
        timepoint = float(data[1])
        time_data.append(timepoint) #add corresponding time-point
        
        string = ''.join([str(delta_6), ",", str(delta_7)])
        overall_delta.append(string)
        overall_time.append(timepoint)

        if delta_7 == 4:
            plt.plot(delta_data,time_data, 'ro') #plot the data points - 'ro' means red dots
            export_fig(delta_6, fig) #export the figure to .png - stolen from some ML-code from handin 1 (model_stats.py)
            old_d_6 = delta_6 #we are done - ready for next delta_6
            delta_data = [] #reset data arrays
            time_data = [] #ready for new data points
        
min_index = np.argmin(overall_time)
minimum = overall_time[min_index]
min_delta = overall_delta[min_index]
print("Minimum: ", min_delta, " : ", minimum)
average = np.average(overall_time)
median = np.median(overall_time) 
print("Average: ", average, "\n Median: ", median)