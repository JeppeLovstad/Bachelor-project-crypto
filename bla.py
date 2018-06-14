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
subpltno = 111

def export_fig(name, fig):
    my_path = os.path.join("", name)
    fig.savefig(my_path)

with open('timeLog_goodstuff') as fp:
    for line in fp:
        old_d_7 = None
        get_d6 = line.split(',')
        delta_6 = get_d6[0] #we get delta_6 by seperating at the first comma and taking the first element
        #then get delta_7 and plot vs its time in the plot
        data = get_d6[1].split('-')
        delta_7 = int(data[0])
        delta_data.append(int(delta_6)) #add new delta_6-point ---- possibly value error of it thinks delta is a float
        timepoint = float(data[1])
        time_data.append(timepoint) #add corresponding time-point 
        

        if delta_7 != old_d_7:
            #make new plot
            fig = plt.figure(int(delta_7))
            old_d_7 = delta_7
        
        
        string = ''.join([str(delta_6), ",", str(delta_7)])
        overall_delta.append(string)
        overall_time.append(timepoint)

        if int(delta_6) == 255:
            plt.plot(delta_data,time_data, 'ro') #plot the data points - 'ro' means red dots
            export_fig(str(delta_7), fig) #export the figure to .png - stolen from some ML-code from handin 1 (model_stats.py)
            #old_d_7 = delta_7 #we are done - ready for next delta_6
            delta_data = [] #reset data arrays
            time_data = [] #ready for new data points
        
plt.plot(delta_data,time_data, 'ro') #plot the data points - 'ro' means red dots
export_fig(str(delta_7), fig) #export the figure to .png - stolen from some ML-code from handin 1 (model_stats.py)
last_fig = delta_7 +1

min_index = np.argmin(overall_time)
minimum = overall_time[min_index]
min_delta = overall_delta[min_index]
print("Minimum: ", min_delta, " : ", minimum)
average = np.average(overall_time)
median = np.median(overall_time) 
allowed_error = 1.05
print("Average: ", average, "\n Median: ", median)
#overall_time[min_index] = np.inf
#sec_index = np.argmin(overall_time)
#sec_min = overall_time[sec_index]
#sec_delta = overall_delta[sec_index]
#print("Second smallest: ", sec_delta, " : ", sec_min)
#remove outliers:
clean_time = []
clean_delta = []
for i in range(len(overall_delta)):
    if overall_time[i] <= average*allowed_error:
        clean_time.append(overall_time[i])
        clean_delta.append(overall_delta[i])

min_index = np.argmin(clean_time)
minimum = clean_time[min_index]
min_delta = clean_delta[min_index]
print("Without outliers")
print("Minimum: ", min_delta, " : ", minimum)
average = np.average(clean_time)
median = np.median(clean_time) 
print("Average: ", average, "\n Median: ", median)


clean_delta_data = []
clean_time_data = []

with open('timeLog_goodstuff') as fp:
    for line in fp:
        old_d_7 = None
        get_d6 = line.split(',')
        delta_6 = get_d6[0] #we get delta_6 by seperating at the first comma and taking the first element
        #then get delta_7 and plot vs its time in the plot
        data = get_d6[1].split('-')
        delta_7 = int(data[0])
        timepoint = float(data[1])
        if timepoint <= average*allowed_error:
            clean_delta_data.append(int(delta_6)) #add new delta_6-point ---- possibly value error of it thinks delta is a float
            clean_time_data.append(timepoint) #add corresponding time-point 
        

        if delta_7 != old_d_7:
            #make new plot
            fig = plt.figure(last_fig+delta_7)
            old_d_7 = delta_7

        if int(delta_6) == 255:
            plt.plot(clean_delta_data,clean_time_data, 'go') #plot the data points - 'ro' means red dots
            export_fig(str(delta_7)+ "_clean", fig) #export the figure to .png - stolen from some ML-code from handin 1 (model_stats.py)
            #old_d_7 = delta_7 #we are done - ready for next delta_6
            clean_delta_data = []
            clean_time_data = []
        
plt.plot(delta_data,time_data, 'go') #plot the data points - 'ro' means red dots
export_fig(str(delta_7), fig) #export the figure to .png - stolen from some ML-code from handin 1 (model_stats.py)