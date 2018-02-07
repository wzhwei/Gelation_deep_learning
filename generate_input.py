#!/software/anaconda2/bin/python

"""
This code extract gel coordinates from LAMMPS (a molecular dynamics simulation package) dump files.
The head of a dump file looks like this:
ITEM: TIMESTEP
0
ITEM: NUMBER OF ATOMS
3240
ITEM: BOX BOUNDS pp pp pp
-19.5 19.5
-19.5 19.5
-19.5 19.5
ITEM: ATOMS id type xs ys zs ix iy iz
1 1 0.350185 0.418963 0.982197 12 3 -5
2 1 0.357697 0.450238 0.990947 12 3 -5
3 1 0.365208 0.481513 -0.000303315 12 3 -4
4 2 0.347932 0.5013 0.0167325 12 3 -4
5 2 0.328853 0.523337 0.0292705 12 3 -4
6 2 0.33663 0.552692 0.0128355 12 3 -4
7 2 0.343211 0.565529 0.984418 12 3 -5
8 2 0.318806 0.546478 0.980161 12 3 -5
9 2 0.288713 0.527586 0.990856 12 3 -5
10 2 0.252615 0.521472 0.000254309 12 3 -4
11 2 0.222737 0.517017 0.0232944 12 3 -4
...

I will extract coordinates (xs ys zs) of all 3240 beads at timestep of 3000000 and put them in one line. 
Then append the label (0/1) to the end of this entry depending on at what tempature the simulation is conducted.

Need to extract coordinates from a number of dump files and generate one input file data.dat in the end
"""

import os,sys,random,math
import numpy as np

n_J = 3 # number of coupling strength (J) sampled 
n_cols = 216 * 15 # number of beads (equal to the number of columns) in the simulation configuration
n_samples = 5300 # number of simulations submitted for each coupling strength
n_samples_real = 5000 # number of true samples will be used for each coupling strength

input_data_low = {}
input_data_high = {}
# input_data is a dictionary with key the sample number and value the list of gel coordinates

for i in range(n_samples_real * n_J):
    input_data_low[i] = []

for i in range(n_samples_real * n_J):
    input_data_high[i] = []

count_J = 0 # count how many J has been scanned till now
for J in [1.30, 1.40, 1.50]:
    count = 0 # track how many samples I have extracted. Some simulations can be killed with error.
    last_timestep = 3000000 # Only extract simulation configuration at last timestep of 3000000
    for i in range(n_samples):
        if count < n_samples_real:
            flag = 0
            flag_nan = 0
            try:
                for j in open('../Gel/Train/J_%.2f/Low_' % J + str(i) + '/' + 'dump_' + str(i) + '.lammpstrj'):
                    line = j.split()
                    if len(line) == 1 and int(line[0]) == last_timestep: # found simulation configurations at timestep of 3000000
                        flag = 1
                        count += 1
                    elif flag == 1 and len(line) == 5 and flag_nan == 0: # found lines that contain coordinates
                        for k in range(2,5):
                            if math.isnan(float(line[k])): # if there is an error in the dump file then re-initialize dictionary and update counts
                                flag = 0
                                input_data_low[count - 1 + count_J * n_samples_real] = [] 
                                count -= 1
                                flag_nan = 1
                                break
                            elif float(line[k]) > 1: # scale all the coordinates to be between [0, 1]
                                line[k] = float(line[k]) - 1
                            elif float(line[k]) < 0:
                                line[k] = float(line[k]) + 1
                        if flag_nan == 1:
                            break
                        elif flag_nan == 0: # if everything is fine, append the coordinates into the list for sample "count-1+count_J*n_samples_real"
                            input_data_low[count - 1 + count_J * n_samples_real].append(float(line[2]))
                            input_data_low[count - 1 + count_J * n_samples_real].append(float(line[3]))
                            input_data_low[count - 1 + count_J * n_samples_real].append(float(line[4]))
                if flag == 1 and flag_nan == 0: # if there is a perfect simulation data at timestep of 3000000
                    input_data_low[count - 1 + count_J * n_samples_real].append(str(1))
                elif flag_nan == 1: # if simulation has error with nan
                    print 'nan', J, i
                else: # if the simulation was killed before the timestep of 3000000
                    print 'no data:', J, i 
            except: # if the dump file don't exist
                print 'no dump:', J, i
    count_J += 1
count_J = 0

for J in [0.70, 0.60, 0.50]: # there is no error in simulations at high temperature, so no need to check for error like above
    for i in range(n_samples_real):
        for j in open('../Sol/Train/J_%.2f/dump_' % J + str(i)+ '.lammpstrj'):
            line = j.split()
            if len(line) == 8: # found lines that contain coordinates 
                for k in range(2,5): # scale all the coordinates to be between [0, 1]
                    if float(line[k]) > 1:
                        line[k] = float(line[k]) - 1
                    elif float(line[k]) < 0:
                        line[k] = float(line[k]) + 1
                input_data_high[i + count_J * n_samples_real].append(float(line[2]))
                input_data_high[i + count_J * n_samples_real].append(float(line[3]))
                input_data_high[i + count_J * n_samples_real].append(float(line[4]))
                # if everything is fine, append the coordinates into the list for sample "i+count_J*n_samples_real"
        input_data_high[i + count_J * n_samples_real].append(str(0))
    count_J += 1

if os.path.isfile('data.dat' % (n_J * 2)):
    os.system('rm data.dat' % (n_J * 2))

f = open('data.dat' % (n_J * 2), 'a')

for i in range(n_samples_real * n_J):
    for j in range(len(input_data_low[i])):
        f.write(str(input_data_low[i][j]) + ' ')
    f.write('\n')

for i in range(n_samples_real * n_J):                            
    for j in range(len(input_data_high[i])):
        f.write(str(input_data_high[i][j]) + ' ')
    f.write('\n')
f.close()


