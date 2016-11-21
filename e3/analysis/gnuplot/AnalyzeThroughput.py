#!/usr/bin/env python

import json
import os
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from analysis.gnuplot.AnalyzeCommon import *
from analysis.gnuplot.CalculateData import calculate_data

throughput_function = {}

workload_list = json.loads(open(os.path.join(workloads_dir, '%s.json' % workload)).read())

# Callback called from calculate_data that sums each agent's reported TPS (after first applying any "scale" factor)
def accumulate_scaled_tps(Value, stage, agent_data):
    scale = 1.0
    desc = agent_data['desc']
    for job in workload_list:
        if desc.startswith(job['description']):
            scale = job['scale']
            break
    tps = agent_data['tps'] * scale
    Value[stage] += tps


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
    data_file = os.path.join(analysis_dir, 'throughput-%s.data' % thread)

    throughput_function[thread] = calculate_data(grinder_files, accumulate_scaled_tps, data_file)

gnuplot_file = os.path.join(analysis_dir, 'throughput.gnuplot')
output_file = os.path.join(analysis_dir, 'throughput.png')
with open(gnuplot_file, 'w') as f:
    f.write("""
# gnuplot <"%(gnuplot_file)s"
set key outside right top vertical Left reverse noenhanced autotitles columnhead nobox
set key invert samplen 4 spacing 1 maxcols 1 width 0 height 0
set output "%(output_file)s"
set term pngcairo noenhanced font "%(font)s" size %(width)s,800
set title "Throughput in %(experiment_name)s"
set xlabel "Load"
set xr [0:*]
set ylabel "TPS"
set yr [0:*]
set xtics (\
    """ % {
        'experiment_name': experiment_name,
        'font': font,
        'gnuplot_file': gnuplot_file,
        'output_file': output_file,
        'width': width,
    })

    data_files = [os.path.join(analysis_dir, file) for file in os.listdir(analysis_dir)
                  if file.startswith('throughput-') and file.endswith('.data')]
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
        data_file = os.path.join(analysis_dir, 'throughput-%s.data' % thread)
        f.write(' %(comma)s "%(data_file)s" ps 3 pt 5 lc %(lc)s title "%(thread_name)s" ' % {
            'comma': comma,
            'data_file': data_file,
            'lc' : lc,
            'thread_name': experiment['threads'][thread_number - 1]['name']
        })
        comma = ','
        function = throughput_function[thread]
        if function:
            f.write(' , %(function)s with lines lw 3 lc %(lc)s ' % {
                'function': function,
                'lc' : lc
            })
        lc += 1

    f.write('\n')

print "Plotting %s" % gnuplot_file
subprocess.call(['gnuplot'], stdin=open(gnuplot_file))
