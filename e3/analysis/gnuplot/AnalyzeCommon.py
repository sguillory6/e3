#!/usr/bin/env python

# Common code for all analysis stages.

import json
import os
import re
import sys

root = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'e3-home'))

def usage():
    print "Usage: %s <run>" % sys.argv[0]
    runs_parent_dir = os.path.join(root, 'runs')
    available_runs = os.listdir(runs_parent_dir) if os.path.exists(runs_parent_dir) else []
    if len(available_runs) >= 1:
        print "Available experiment runs:"
        for run in available_runs:
            print '    %s' % run
    else:
        print "No experiment runs to analyze! Try Run.py first."
    exit(1)

if len(sys.argv) <= 1:
    usage()

run = sys.argv[1] if sys.argv[1] != '-r' else sys.argv[2]
run_dir = os.path.join(os.path.join(root, 'runs'), run)

if not os.path.isdir(run_dir):
    print 'No such run "%s"' % run
    usage()

# Globally defined variables used by all analysis stages

analysis_dir = os.path.join(run_dir, 'analysis')
if not os.path.exists(analysis_dir):
    os.makedirs(analysis_dir)

experiment_name = re.sub(r'-....-..-..T..:..:..$', '', run)
experiment = json.loads(open(os.path.join(run_dir, '%s.json' % run)).read())

duration = experiment['duration']
workload = experiment['workload']
threads = sorted([thread for thread in os.listdir(run_dir) if thread.startswith('thread-')])

workloads_dir = os.path.join(root, 'workloads')

error_color = 7
font = "Arial,16"
time_margin_before_stage = 60000
time_margin_after_stage = 60000
width = 2000
xmargin = 8
ymargin = 3

# Return the ordered list of stage(s) for the named thread of the experiment
def stages_for_thread(thread):
    stages = set()
    for dir in os.listdir(os.path.join(run_dir, thread)):
        if dir.startswith('worker-node-'):
            for stage in os.listdir(os.path.join(run_dir, thread, dir)):
                if stage.startswith('stage-'):
                    stages.add(stage)
    return sorted(stages)

# Calculate:
#  - the time that each stage of each thread actually started and finished,
#  - the names of all tests that executed
# from Grinder output.  These are extracted from Grinder output, not taken from the experiment configuration files,
# just in case these files are edited _after_ an experiment ran, or if the actual experiment times differed subtly from
# what was actually requested for some reason.
#
# This would be a lot easier and faster if Grinder allowed log levels to be controlled to exclude voluminous output.
# See http://sourceforge.net/p/grinder/mailman/message/31237017/.
start = {}
elapsed_time = {}
test_names = set()
for thread in threads:
    for stage in stages_for_thread(thread):
        # Each worker node may have a different idea of the start and elapsed time, even in the same experiment stage,
        # so gather all of them.
        for dir in os.listdir(os.path.join(run_dir, thread)):
            if dir.startswith('worker-node-'):
                stage_dir = os.path.join(run_dir, thread, dir, stage)
                for log_file in os.listdir(stage_dir):
                    if log_file.endswith('-0.log'):
                        with open(os.path.join(stage_dir, log_file)) as infile:
                            for line in infile:
                                m = re.match(r'.*start time is ([0-9]*) ms since Epoch', line)
                                if m:
                                    start[thread + ',' + stage] = int(m.group(1))
                                m = re.match(r'.*elapsed time is ([0-9]*) ms', line)
                                if m:
                                    elapsed_time[thread + ',' + stage] = int(m.group(1))
                                m = re.match(r'Test [0-9]+', line)
                                if m:
                                    test_names.add(line.split('"')[1])
# Apply a bit of a time margin before and after each stage.  This allows the time charts to show a bit of interesting
# information before and after the actual experiment execution (in case anyone suspects effect(s) there that might have
# influenced the results).
tmin = {}
tmax = {}
for thread in threads:
    for stage in stages_for_thread(thread):
        if thread + ',' + stage in start:
            tmin[thread + ',' + stage] = start[thread + ',' + stage] - time_margin_before_stage
        if thread + ',' + stage in elapsed_time:
            tmax[thread + ',' + stage] = elapsed_time[thread + ',' + stage] + time_margin_after_stage
