#!/usr/bin/env python

import os
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from analysis.gnuplot.AnalyzeCommon import *

# Extract all test numbers and names from all Grinder files
tests = {}
for thread in threads:
    for stage in stages_for_thread(thread):
        for dir in os.listdir(os.path.join(run_dir, thread)):
            if dir.startswith('worker-node-'):
                stage_dir = os.path.join(run_dir, thread, dir, stage)
                for log_file in os.listdir(stage_dir):
                    if log_file.endswith('-0.log'):
                        with open(os.path.join(stage_dir, log_file)) as infile:
                            for line in infile:
                                m = re.match(r'Test ([0-9]*).*"([^"]*)"', line)
                                if m:
                                    tests[int(m.group(1))] = m.group(2)

for thread in threads:
    thread_number = int(thread[7:])     # strip leading 'thread-'
    grinder_files = []
    for dir in os.listdir(os.path.join(run_dir, thread)):
        if dir.startswith('worker-node-'):
            for stage in os.listdir(os.path.join(run_dir, thread, dir)):
                if stage.startswith('stage-'):
                    stage_dir = os.path.join(run_dir, thread, dir, stage)
                    for file in os.listdir(stage_dir):
                        if file.endswith('-0.log'):
                            grinder_files.append(os.path.join(stage_dir, file))

    gnuplot_file = os.path.join(analysis_dir, 'histogram-%s.gnuplot' % thread)
    output_file = os.path.join(analysis_dir, 'histogram-%s.png' % thread)
    with open(gnuplot_file, 'w') as f:
        f.write("""
# gnuplot <"%(gnuplot_file)s"
set border lw 1
set boxwidth 0.8 absolute
set datafile missing '-'
set key outside right top vertical Left reverse noenhanced autotitles columnhead nobox
set key invert samplen 4 spacing 1 maxcols 1 width 0 height 0
set output "%(output_file)s"
set style data histograms
set style fill solid 1.00 border lt -1
set style histogram rowstacked title  offset character 0, 0, 0
set style increment user
set term pngcairo noenhanced font "%(font)s" size %(width)s,800
set title "Throughput breakdown in %(experiment_name)s (%(thread_name)s)"
set xlabel "Load"
set xrange [*:*]
set xtics border in scale 0,0 nomirror offset character 0, 0, 0 autojustify
set xtics norangelimit
set ylabel "TPS"
set ytics auto
plot "<(%(calculate_histogram_py)s %(workloads_dir)s/%(workload)s.json %(grinder_files)s)" using 2:xtic(1), for [i=3:%(test_count)d] "" using i
    """ % {
            'calculate_histogram_py': os.path.abspath(os.path.join(os.path.dirname(__file__), 'CalculateHistogram.py')),
            'experiment_name': experiment_name,
            'font': font,
            'gnuplot_file': gnuplot_file,
            'grinder_files': ' '.join(grinder_files),
            'output_file': output_file,
            'test_count': len(tests) + 1,
            'thread_name': experiment['threads'][thread_number - 1]['name'],
            'width': width,
            'workload': workload,
            'workloads_dir': workloads_dir
        })

    print "Plotting %s" % gnuplot_file
    subprocess.call(['gnuplot'], stdin=open(gnuplot_file))
