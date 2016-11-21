#!/usr/bin/env python

import os
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from analysis.gnuplot.AnalyzeCommon import *

for thread in threads:
    thread_number = int(thread[7:])     # strip leading 'thread-'
    worker_nodes = [dir for dir in os.listdir(os.path.join(run_dir, thread)) if dir.startswith('worker-node-')]
    for stage in stages_for_thread(thread):
        stage_number=int(stage[6:])     # strip leading 'stage-'
        clients = int(experiment['threads'][thread_number - 1]['stages'][stage_number]['clients'])
        clients_per_worker_node = clients / len(worker_nodes)
        height=110 + 10 * clients
        if thread + ',' + stage not in start or thread + ',' + stage not in tmax:
            continue
        start_time = start[thread + ',' + stage]
        time_max = tmax[thread + ',' + stage]
        gnuplot_file = os.path.join(analysis_dir, 'gantt-' + thread + '-' + stage + '.gnuplot')
        output_file = os.path.join(analysis_dir, 'gantt-' + thread + '-' + stage + '.png')
        with open(gnuplot_file, 'w') as f:
            f.write("""
# gnuplot <"%(gnuplot_file)s"
set bars 1.0
set datafile separator ','
# The following margin calculation has been empirically derived so that the axes will line up with other charts when
# concatenated with montage.
set tmargin %(xmargin)d/2 - .075
set bmargin %(xmargin)d/2 + .025
set lmargin %(ymargin)d
set rmargin 0
set output "%(output_file)s"
set style fill solid
set term pngcairo noenhanced font "%(font)s" size %(height)d,%(width)d
set xlabel "clients" rotate by 180
set xr [-1.5:%(clients)d+0.5]
set xtics 0,10,%(clients)d-1 rotate format "%%g"
set ylabel "%(experiment_name)s (%(thread_name)s) %(stage)s"
unset ytics
set yr [-%(time_margin_before_stage)d/1000:%(time_max)d/1000]
set arrow 1 from -1.5,0 to %(clients)d+0.5,0 nohead
set arrow 2 from -1.5,%(duration)s/1000 to %(clients)d+0.5,%(duration)s/1000 nohead
start=%(start_time)d.0
plot \
            """ % {
                'clients': clients,
                'duration': duration,
                'experiment_name': experiment_name,
                'font': font,
                'gnuplot_file': gnuplot_file,
                'height': height,
                'output_file': output_file,
                'stage': stage,
                'start_time': start_time,
                'thread_name': experiment['threads'][thread_number - 1]['name'],
                'time_margin_before_stage': time_margin_before_stage,
                'time_max': time_max,
                'width': width,
                'xmargin': xmargin,
                'ymargin': ymargin
            })
            worker_node_number = 0
            comma = ''
            for worker_node in worker_nodes:
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
                f.write(""" %(comma)s "<(cat %(run_dir)s/%(thread)s/%(worker_node)s/%(stage)s/*-0-data.log)" \
                                using (%(worker_node_number)d*%(clients_per_worker_node)d+$1):(($4-start)/1000):(($4-start)/1000):(($4+$5-start)/1000):(($4+$5-start)/1000):($6>0 ? %(error_color)s : $3) \
                                with candlesticks lc variable notitle\\
                """ % {
                    'clients_per_worker_node': clients_per_worker_node,
                    'comma': comma,
                    'error_color': error_color,
                    'run_dir': run_dir,
                    'stage': stage,
                    'thread': thread,
                    'worker_node': worker_node,
                    'worker_node_number': worker_node_number
                })
                comma = ','
                worker_node_number += 1

            f.write('\n')

        print "Plotting %s" % gnuplot_file
        subprocess.call(['gnuplot'], stdin=open(gnuplot_file))
        subprocess.call(['mogrify', '-rotate', '90', output_file])
