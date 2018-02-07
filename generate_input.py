#!/usr/bin/python

import os,sys,random,math
import numpy as np

n_J = 3
n_cols = 216 * 15
n_samples = 5300
n_samples_real = 5000
input_data_low = {}
input_data_high = {}

# input_data is a dic with key the sample # and                                                                                                      
for i in range(n_samples_real * n_J):
    input_data_low[i] = []

for i in range(n_samples_real * n_J):
    input_data_high[i] = []

count_J = 0
for J in [1.30, 1.40, 1.50]:
    count = 0
    last_timestep = 3000000
    for i in range(n_samples):
        if count < n_samples_real:
            flag = 0
            flag_nan = 0
            try:
                f = open('../Gel/Train/J_%.2f/Low_' % J + str(i) + '/' + 'dump_' + str(i) + '.lammpstrj')
                for j in f:
                    line = j.split()
                    if len(line) == 1 and int(line[0]) == last_timestep:
                        flag = 1
                        count += 1
                    elif flag == 1 and len(line) == 5 and flag_nan == 0:
                        for k in range(2,5):
                            if math.isnan(float(line[k])):
                                flag = 0
                                input_data_low[count - 1 + count_J * n_samples_real] = []
                                count -= 1
                                flag_nan = 1
                                break
                            elif float(line[k]) > 1:
                                line[k] = float(line[k]) - 1
                            elif float(line[k]) < 0:
                                line[k] = float(line[k]) + 1
                        if flag_nan == 1:
                            break
                        elif flag_nan == 0:
                            input_data_low[count - 1 + count_J * n_samples_real].append(float(line[2]))
                            input_data_low[count - 1 + count_J * n_samples_real].append(float(line[3]))
                            input_data_low[count - 1 + count_J * n_samples_real].append(float(line[4]))
                if flag == 1 and flag_nan == 0:
                    input_data_low[count - 1 + count_J * n_samples_real].append(str(1))
                elif flag_nan == 1:
                    print 'nan', J, i
                    sys.stdout.flush()
                else:
                    print 'no data:', J, i 
                    sys.stdout.flush()
            except:
                print 'no dump:', J, i
                sys.stdout.flush()
    count_J += 1
count_J = 0

for J in [0.70, 0.60, 0.50]:
    for i in range(n_samples_real):
        f= open('../Sol/Train/J_%.2f/dump_' % J + str(i)+ '.lammpstrj')
        for j in f:
            line = j.split()
            if len(line) == 8: # Note here that the sol output actually contains images
                for k in range(2,5):
                    if float(line[k]) > 1:
                        line[k] = float(line[k]) - 1
                    elif float(line[k]) < 0:
                        line[k] = float(line[k]) + 1
                input_data_high[i + count_J * n_samples_real].append(float(line[2]))
                input_data_high[i + count_J * n_samples_real].append(float(line[3]))
                input_data_high[i + count_J * n_samples_real].append(float(line[4]))
        input_data_high[i + count_J * n_samples_real].append(str(0))
    count_J += 1

if os.path.isfile('input_5000_nJ_%s.dat' % (n_J * 2)):
    os.system('rm input_5000_nJ_%s.dat' % (n_J * 2))

f = open('input_5000_nJ_%s.dat' % (n_J * 2), 'a')

for i in range(n_samples_real * n_J):
    for j in range(len(input_data_low[i])):
        f.write(str(input_data_low[i][j]) + ' ')
    f.write('\n')

for i in range(n_samples_real * n_J):                            
    for j in range(len(input_data_high[i])):
        f.write(str(input_data_high[i][j]) + ' ')
    f.write('\n')

f.close()
'''
n_shuffle = 0

index = range(216)
if os.path.isfile('input_data_shuffle_%s_J_%s_1.dat' % (n_shuffle, n_J * 2)):
    os.system('rm input_data_shuffle_%s_J_%s_1.dat' % (n_shuffle, n_J * 2))
                  
f = open('input_data_shuffle_%s_J_%s_1.dat' % (n_shuffle, n_J * 2), 'a')

for i in range(n_samples_real * n_J):
    for each in range(n_shuffle):
        random.shuffle(index)
        for j in index:
            for k in range(int(j) * 15 * 3, (int(j) + 1) * 15 * 3):
                f.write(str(input_data_low[i][k]) + ' ')
        f.write(str(1))
        f.write('\n')

for i in range(n_samples_real * n_J):
    for each in range(n_shuffle):
        random.shuffle(index)
        for j in index:
            for k in range(int(j) * 15 * 3, (int(j) + 1) * 15 * 3):
                f.write(str(input_data_high[i][k]) + ' ')
        f.write(str(0))
        f.write('\n')

f.close()
'''

