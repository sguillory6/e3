#!/usr/bin/env python

import json
import os
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from analysis.gnuplot.AnalyzeCommon import *
from analysis.gnuplot.CalculateData import calculate_data

# Callback called from calculate_data that averages each agent's reported mean test time
def accumulate_mean_test_time(Value, stage, agent_data):
    desc = agent_data['desc']
    if desc == current_test_name:
        mean_test_time = agent_data['mean_test_time']
        test_count = agent_data['tests']
        Value[stage] = (Value[stage] * test_count_per_stage[stage] + mean_test_time * test_count) / (test_count_per_stage[stage] + test_count)
        test_count_per_stage[stage] += test_count

i = 0
for test_name in test_names:
    i += 1
    current_test_name = test_name
    mean_test_time_function = {}
    for thread in threads:
        grinder_files = []
        for dir in os.listdir(os.path.join(run_dir, thread)):
            if dir.startswith('worker-node-'):
                for stage in os.listdir(os.path.join(run_dir, thread, dir)):
                    if stage.startswith('stage-'):
                        stage_dir = os.path.join(run_dir, thread, dir, stage)
                        for file in os.listdir(stage_dir):
                            if file.endswith('-0.log'):
                                grinder_files.append(os.path.join(stage_dir, file))
        test_count_per_stage = [0] * len(stages_for_thread(thread))
        data_file = os.path.join(analysis_dir, 'mean-test-time-%03d-%s.data' % (i, thread))
        mean_test_time_function[thread] = calculate_data(grinder_files, accumulate_mean_test_time, data_file, include_origin=False)

    gnuplot_file = os.path.join(analysis_dir, 'mean-test-time-%03d.gnuplot' % i)
    output_file = os.path.join(analysis_dir, 'mean-test-time-%03d.png' % i)
    with open(gnuplot_file, 'w') as f:
        f.write("""
# gnuplot <"%(gnuplot_file)s"
set key outside right top vertical Left reverse noenhanced autotitles columnhead nobox
set key invert samplen 4 spacing 1 maxcols 1 width 0 height 0
set output "%(output_file)s"
set term pngcairo noenhanced font "%(font)s" size %(width)s,800
set title "%(test_name)s mean test time"
set xlabel "Load"
set xr [0:*]
set ylabel "Mean test time (ms)"
set yr [0:*]
set xtics (\
        """ % {
            'font': font,
            'gnuplot_file': gnuplot_file,
            'output_file': output_file,
            'test_name': test_name,
            'width': width,
        })

        data_files = [os.path.join(analysis_dir, file) for file in os.listdir(analysis_dir)
                      if file.startswith('mean-test-time-%03d' % i) and file.endswith('.data')]
        p = subprocess.Popen(['awk', 'FNR > 1 { print $1 }'] + data_files, stdout=subprocess.PIPE)
        comma = ''
        for clients in filter(None, p.communicate()[0].split('\n')):
            f.write('%s "%s" %s' % (comma, clients, clients))
            comma = ','
        f.write(""" )
    plot \
        """)

        comma = ' '
        lc = 1
        for thread in threads:
            thread_number = int(thread[7:])     # strip leading 'thread-'
            data_file = os.path.join(analysis_dir, 'mean-test-time-%03d-%s.data' % (i, thread))
            f.write(' %(comma)s "%(data_file)s" ps 3 pt 5 lc %(lc)s title "%(thread_name)s" ' % {
                'comma': comma,
                'data_file': data_file,
                'lc' : lc,
                'thread_name': experiment['threads'][thread_number - 1]['name']
            })
            comma = ','
            function = mean_test_time_function[thread]
            if function:
                f.write(' , %(function)s with lines lw 3 lc %(lc)s ' % {
                    'function': function,
                    'lc' : lc
                })
            lc += 1

        f.write('\n')

    print "Plotting %s" % gnuplot_file
    subprocess.call(['gnuplot'], stdin=open(gnuplot_file))
