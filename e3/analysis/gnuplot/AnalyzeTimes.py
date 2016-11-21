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
    for stage in stages_for_thread(thread):
        if thread + ',' + stage not in start or thread + ',' + stage not in tmax:
            continue
        start_time = start[thread + ',' + stage]
        time_max = tmax[thread + ',' + stage]
        gnuplot_file = os.path.join(analysis_dir, 'times-' + thread + '-' + stage + '.gnuplot')
        output_file = os.path.join(analysis_dir, 'times-' + thread + '-' + stage + '.png')
        with open(gnuplot_file, 'w') as f:
            f.write("""
# gnuplot <"%(gnuplot_file)s"
set datafile separator ','
set key outside right top vertical Left reverse noenhanced autotitles columnhead nobox
set format x "%%H:%%M"
set logscale y 10
set tmargin 0
set bmargin %(ymargin)s
set lmargin %(xmargin)s
set rmargin %(xmargin)s
set output "%(output_file)s"
set term pngcairo noenhanced font "%(font)s" size %(width)s,800
set xdata time
set xlabel "Time (hh:mm)"
set xr [-%(time_margin_before_stage)d/1000:%(time_max)d/1000]
set ylabel "duration (s)"
set yr [.001:99000]
set arrow 1 from 0,.001 to 0,99000 nohead
set arrow 2 from %(duration)s/1000,.001 to %(duration)s/1000,99000 nohead
start=%(start_time)d.0
plot """ % {
                'duration': duration,
                'font': font,
                'gnuplot_file': gnuplot_file,
                'output_file': output_file,
                'start_time': start_time,
                'time_margin_before_stage': time_margin_before_stage,
                'time_max': time_max,
                'width': width,
                'xmargin': xmargin,
                'ymargin': ymargin
            })
            comma = ''
            for i, test_name in tests.iteritems():
                # grinder-0-data.log file format:
                #   $1 = Thread
                #   $2 = Run
                #   $3 = Test
                #   $4 = Start time (ms since Epoch)
                #   $5 = Test time
                #   $6 = Errors
                #   $7 = HTTP response code
                #   $8 = HTTP response length
                #   $9 = HTTP response errors
                #   $10 = Time to resolve host
                #   $11 = Time to establish connection
                #   $12 = Time to first byte
                #   $13 = New connections
                f.write(""" %(comma)s "<(awk -F, '$3==%(i)d' %(run_dir)s/%(thread)s/worker-node-*/%(stage)s/*-0-data.log)" \
                     using (($4-start)/1000):($5/1000):($6>0 ? %(error_color)s : $3) with points lc variable ps 1 pt 5 \
                     title "%(test_name)s"\\
                """ % {
                    'comma': comma,
                    'error_color': error_color,
                    'i': i,
                    'run_dir': run_dir,
                    'stage': stage,
                    'test_name': test_name,
                    'thread': thread
                })
                comma = ','

            f.write('\n')

        print "Plotting %s" % gnuplot_file
        subprocess.call(['gnuplot'], stdin=open(gnuplot_file))
