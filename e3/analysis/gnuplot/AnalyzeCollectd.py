#!/usr/bin/env python

import os
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from analysis.gnuplot.AnalyzeCommon import *

for file in os.listdir(analysis_dir):
    if file.startswith('collectd-') and file.endswith('.png'):
        os.remove(os.path.join(analysis_dir, file))

# List of collectd metrics of interest, one regex per chart.  These metrics (if present in the experiment run data)
# will be charted for all nodes (worker nodes, cluster nodes, and file server) in the experiment.
vars = [
    "aggregation-cpu-average/cpu-(user|system)",
    "interface-eth0/if_octets",
    "interface-eth0/if_packets",
    "memory/memory-(buffered|cached|used)",
    #"GenericJMX-com.atlassian.bitbucket_CommandTickets/gauge-Used",
    "GenericJMX-com.atlassian.bitbucket_HostingTickets/gauge-(Total|Used)",
    "GenericJMX-com.atlassian.bitbucket_HostingTickets/gauge-Used",
    "GenericJMX-com.atlassian.bitbucket_HostingTickets/gauge-QueuedRequests",
    "GenericJMX-com.hazelcast_HazelcastInstance.OperationService.hazelcast.oper/derive-executedOperationCount",
    "GenericJMX-com.hazelcast_HazelcastInstance.OperationService.hazelcast.oper/derive-executedRemoteOperationCount",
    #"GenericJMX-com.hazelcast_HazelcastInstance.OperationService.hazelcast.oper/gauge-responseQueueSize",
    #"GenericJMX-com.hazelcast_HazelcastInstance.OperationService.hazelcast.oper/gauge-runningOperationsCount",
    "GenericJMX-com.zaxxer.hikari_Poolbitbucket/gauge-ActiveConnections"
]

# All the following dictionaries are indexed by regex string (which must match one of the vars above):

# Dictionary giving the gnuplot "y" expression for each metric regex, if different from '2'.  The value may be any
# expression acceptable to gnuplot.  Note that gnuplot allows simple column numbers (e.g., '2' or '3') by themselves,
# but in any more complex expression column numbers must be referenced using the syntax '$2' or 'column(2)' or
# '"value"' or 'column("value")'.  See "help using" in gnuplot.
y = {
    "aggregation-cpu-average/cpu-(user|system)": "(get($1)):(derive_and_stack($1,$2))",
    "interface-eth0/if_octets": "(derive2($1,$2,$3))",
    "interface-eth0/if_packets": "(derive2($1,$2,$3))",
    "memory/memory-(buffered|cached|used)": "(get($1)):(stack($1,$2/1024**3))",
    "GenericJMX-com.hazelcast_HazelcastInstance.OperationService.hazelcast.oper/derive-executedOperationCount": "(derive($1,$2))",
    "GenericJMX-com.hazelcast_HazelcastInstance.OperationService.hazelcast.oper/derive-executedRemoteOperationCount": "(derive($1,$2))"
}
# Dictionary giving the gnuplot "ylabel" string for each metric regex, if any.
ylabel = {
    "aggregation-cpu-average/cpu-(user|system)": "per cent",
    "memory/memory-(buffered|cached|used)": "GiBytes"
}
# Dictionary giving the gnuplot "yrange" maximum value for each metric regex, if any.  This controls the vertical scale
# for the chart.  If missing, then a '*' will be specified, allowing gnuplot to scale each chart automatically.
yr = {
    "aggregation-cpu-average/cpu-(user|system)": 100,
    "interface-eth0/if_octets": 1e8,
    "interface-eth0/if_packets": 1e5,
    "memory/memory-(buffered|cached|used)": 7.5,
    "GenericJMX-com.atlassian.bitbucket_HostingTickets/gauge-(Total|Used)": 50,
    "GenericJMX-com.hazelcast_HazelcastInstance.OperationService.hazelcast.oper/derive-executedOperationCount": 100,
    "GenericJMX-com.hazelcast_HazelcastInstance.OperationService.hazelcast.oper/derive-executedRemoteOperationCount": 100,
    "GenericJMX-com.zaxxer.hikari_Poolbitbucket/gauge-ActiveConnections": 80,
}

# The following dictionaries are indexed by fully expanded variable name.

# Dictionary giving the gnuplot "lc" (line color) value to use for each metric, if different from '1'.  The value may
# be any <colorspec> acceptable to gnuplot.  See "help lc" in gnuplot.
lc = {
    "aggregation-cpu-average/cpu-user": 2,
    "aggregation-cpu-average/cpu-system": 3,
    "interface-eth0/if_octets": 7,
    "interface-eth0/if_packets": 8,
    "memory/memory-buffered": 4,
    "memory/memory-cached": 5,
    "memory/memory-used": 6,
    "GenericJMX-com.atlassian.bitbucket_HostingTickets/gauge-Total": 3,
    "GenericJMX-com.atlassian.bitbucket_HostingTickets/gauge-Used": 4,
}

# Dictionary giving the gnuplot "style" string to use for each metric, if different from 'filledcurves fs transparent solid 0.5 noborder'.
# The value may be any <style> acceptable to gnuplot.  See "help style" in gnuplot.
style = {
    "aggregation-cpu-average/cpu-user": "filledcurves fs solid noborder",
    "aggregation-cpu-average/cpu-system": "filledcurves fs solid noborder",
    "memory/memory-buffered": "filledcurves fs solid noborder",
    "memory/memory-cached": "filledcurves fs solid noborder",
    "memory/memory-used": "filledcurves fs solid noborder",
}

for thread in threads:
    thread_number = int(thread[7:])     # strip leading 'thread-'
    instance_nodes = [dir for dir in os.listdir(os.path.join(run_dir, thread))
                      if dir.startswith('cluster-node-') or dir.startswith('file-server-')]
    worker_nodes = [dir for dir in os.listdir(os.path.join(run_dir, thread)) if dir.startswith('worker-node-')]
    for stage in stages_for_thread(thread):
        if thread + ',' + stage not in start or thread + ',' + stage not in tmax:
            continue
        start_time = start[thread + ',' + stage]
        time_max = tmax[thread + ',' + stage]
        gnuplot_file = os.path.join(analysis_dir, 'collectd-' + thread + '-' + stage + '.gnuplot')
        with open(gnuplot_file, 'w') as f:
            f.write("""
# gnuplot <"%(gnuplot_file)s"
set datafile separator ','
set tmargin 0
set bmargin 0
set lmargin %(xmargin)d
set rmargin %(xmargin)d
set term pngcairo noenhanced font "%(font)s" size %(width)s,200
set xdata time
set xr [-%(time_margin_before_stage)d/1000:%(time_max)d/1000]
set arrow 1 from 0,.001 to 0,1e12 nohead
set arrow 2 from %(duration)s/1000,.001 to %(duration)s/1000,1e12 nohead
start=%(start_time)d.0
get(i) = ( \
  pos = strstrt(encoded_string, sprintf("%%.0f", i) . "="), \
  pos == 0 ? ( \
    0 \
  ) : ( \
    substr = encoded_string[pos:], \
    begin = strstrt(substr, "="), \
    end = strstrt(substr, " "), \
    substr[begin+1:end-1] + 0.0 \
  ) \
)
put(time, value) = ( \
  encoded_string = sprintf("%%.0f=%%.15g %%s", time, value, encoded_string) \
)
stack(time,value) = ( \
  stacked_value = get(time) + value, \
  put(time, stacked_value), \
  stacked_value \
)
derive_and_stack(new_time,new_value) = ( \
  rate = (new_value-old_value)/(new_time-old_time), \
  old_value = new_value, \
  old_time = new_time, \
  stacked_rate = get(new_time) + rate, \
  put(new_time, stacked_rate), \
  stacked_rate \
)
derive(new_time,new_value) = (\
  rate = (new_value-old_value)/(new_time-old_time), \
  old_value = new_value, \
  old_time = new_time, \
  rate \
)
derive2(new_time,new_value1,new_value2) = ( \
  rate = (new_value1+new_value2-old_value)/(new_time-old_time), \
  old_value = new_value1+new_value2, \
  old_time = new_time, \
  rate \
)
old_time = NaN
old_value = NaN
            """ % {
                'duration': duration,
                'font': font,
                'gnuplot_file': gnuplot_file,
                'start_time': start_time,
                'time_margin_before_stage': time_margin_before_stage,
                'time_max': time_max,
                'width': width,
                'xmargin': xmargin,
            })
            output = 0
            done = set()
            for var in vars:
                for node in worker_nodes + instance_nodes:
                    collectd_csv_dir = os.path.join(run_dir, thread, node, 'collectd-csv')
                    for host in os.listdir(collectd_csv_dir):
                        host_dir = os.path.join(collectd_csv_dir, host)
                        plot = False
                        for subdir in os.listdir(host_dir):
                            for file in os.listdir(os.path.join(host_dir, subdir)):
                                # Test if each recorded metric matches this "var" regex
                                metric = subdir + '/' + file
                                m = re.match(var, metric)
                                if m:
                                    # Strip '-yyyy-mm-dd' suffix appended by collectd
                                    expanded_var = re.sub(r'-....-..-..$', '', metric)
                                    if expanded_var + host_dir not in done:
                                        done.add(expanded_var + host_dir)
                                        if not plot:
                                            plot = True
                                            comma = ' '
                                            output += 1
                                            output_file = os.path.join(analysis_dir, 'collectd-' + thread + '-' + stage + '-%05d.png' % output)
                                            f.write(("\n"
                                                     "set output \"%(output_file)s\"\n"
                                                     "set ylabel \"%(ylabel)s\"\n"
                                                     "set yr [0:%(yr)s]\n"
                                                     "encoded_string = \" \"\n"
                                                     "plot \\\n") % {
                                                'output_file': output_file,
                                                'ylabel': ylabel[var] if var in ylabel else '',
                                                'yr': yr[var] if var in yr else '*'
                                            })
                                        else:
                                            comma = ','
                                        title="%s %s" % (node, expanded_var)
                                        f.write(" %(comma)s \"<(cat %(host_dir)s/%(expanded_var)s-????-??-??)\" using ($1-start/1000):%(y)s with %(style)s "
                                                "lc %(lc)s title \"%(title)s\"" % {
                                            'comma': comma,
                                            'host_dir': host_dir,
                                            'expanded_var': expanded_var,
                                            'lc': lc[expanded_var] if expanded_var in lc else '1',
                                            'style': style[expanded_var] if expanded_var in style else 'filledcurves x1 fs transparent solid 0.5 noborder',
                                            'title': title,
                                            'y': y[var] if var in y else '2'
                                        })

                    f.write('\n')

            f.write('\n')

        print "Plotting %s" % gnuplot_file
        subprocess.call(['gnuplot'], stdin=open(gnuplot_file))
