#!/usr/bin/env python

import json
import os
import re
import sys

root = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
workloads_dir = os.path.join(root, 'e3/data/workloads')

# Write a datafile to output in the following form:
#     Test	"Clone over SSH"	"Merge pull requests"	"Merge pull requests - Clone"	"Merge pull requests - Push"
#     20	0.48	0.11	0.04	0.04
#     40	0	0	0	0
#     80	0.73	0.26	0.09	0.08
def calculate_histogram(grinder_files, workload, output):
    Load = []
    TPS = {}
    Test = []
    stages = 0
    max = 0
    for file in grinder_files:
        threads = 0
        stage = int(os.path.basename(os.path.dirname(file))[6:])     # strip initial 'stage-'
        if (stages < stage + 1):
            stages = stage + 1
        while len(Load) <= stage:
            Load.append(0)
        with open(file, 'r') as f:
            for line in f:
                # Count the threads in this Grinder logfile by looking at all the unique log messages.
                # This is to determine the load level empirically.
                # TODO: There is probably a more efficient way to communicate this from experiment execution.
                m = re.match(r'....-..-.. ..:..:..,... INFO  .*-0 thread-([0-9]*)', line)
                if m:
                    thread = int(m.group(1))
                    if (threads < thread + 1):
                        threads = thread + 1
                m = re.match(r'Test ', line)
                if m:
                    # grinder-0.log file format:
                    #   $1 = "Test"
                    #   $2 = "0"...
                    #   $3 = Tests
                    #   $4 = Errors
                    #   $5 = Mean Test Time (ms)
                    #   $6 = Test Time Standard Deviation (ms)
                    #   $7 = TPS
                    #   $8 = Mean response length
                    #   $9 = Response bytes per second
                    #   $10 = Response errors
                    #   $11 = Mean time to resolve host
                    #   $12 = Mean time to establish connection
                    #   $13 = Mean time to first byte
                    #   $14 = Description
                    #             Tests        Errors       Mean Test    Test Time    TPS          Mean         Response     Response     Mean time to Mean time to Mean time to
                    #                                       Time (ms)    Standard                  response     bytes per    errors       resolve host establish    first byte
                    #                                                    Deviation                 length       second                                 connection
                    #                                                    (ms)
                    #
                    #Test 0       1060         0            10224.49     7229.27      0.58         19.77        11.51        5            0.04         0.28         10221.48      "Status"
                    #Test 1       2408         0            10490.14     7157.16      1.32         16665.09     22049.02     8            0.04         0.30         10485.22      "Projects"
                    fields = re.split("[ \t]+", line)
                    test = int(fields[1])
                    tps = float(fields[6])
                    desc = line.split('"')[1]
                    scale = 1.0
                    for job in workload:
                        if desc.startswith(job['description']):
                            scale = job['scale']
                            break
                    tps *= scale
                    while len(Test) <= test:
                         Test.append('')
                    Test[test] = desc
                    key = str(stage) + ',' + str(test)
                    if key in TPS:
                        TPS[key] += tps
                    else:
                        TPS[key] = tps
                    if max < test:
                        max = test
        Load[stage] += threads

    output.write('Test\t')
    for j in range(0, max+1):
        output.write('"%s"\t' % Test[j])
    output.write('\n')
    for i in range(0, stages):
        output.write("%d\t" % Load[i])
        for j in range(0, max+1):
            key = str(i) + ',' + str(j)
            if key in TPS:
                output.write("%g\t" % TPS[key])
            else:
                output.write("-\t")
        output.write("\n")


workload = sys.argv[1]
grinder_files = sys.argv[2:]

workload_list = json.loads(open(os.path.join(workloads_dir, workload)).read())
calculate_histogram(grinder_files, workload_list, sys.stdout)
